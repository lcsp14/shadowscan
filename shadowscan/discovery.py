"""Módulo [2] — Descoberta ativa.

Monta o conjunto O de endpoints que efetivamente respondem na API.

Fluxo:
  0. BASELINES  — pede caminhos aleatórios (que certamente não existem) para
                  aprender como a API responde a "não encontrado" (ver responses.py).
  1. FASE A     — descobre CAMINHOS vivos, só com GET:
                  prefixos literais da spec, variações de versão e wordlist.
  2. FASE B     — para cada caminho vivo + caminhos declarados, testa todos os
                  métodos (GET, POST, PUT, PATCH, DELETE) e decide quais existem.

Dois tipos de candidato, tratados de forma diferente (D6 em docs/decisoes.md):
- "literal": caminho montado a partir de wordlist/prefixo (`/users/v1/admin`).
  Comparado com o baseline GLOBAL e com o baseline do PAI (`/users/v1/<aleatório>`).
  O baseline do pai detecta rotas-coringa: se `/users/v1/{username}` existe,
  qualquer `/users/v1/<palavra>` responde "usuário não encontrado" — isso não
  é um endpoint novo, é o template respondendo.
- "template": instância de um caminho declarado (`/users/v1/1` para
  `/users/v1/{username}`). Comparado SÓ com o baseline global: aqui o
  "usuário não encontrado" é justamente a prova de que a rota existe.
"""

from __future__ import annotations

import asyncio
import re
import secrets
import time
from dataclasses import dataclass, field

import httpx

from shadowscan.responses import Resp, same_response
from shadowscan.spec_parser import Endpoint

DEFAULT_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
# Status que significam "este MÉTODO não existe neste caminho" independentemente
# do corpo. 405 também prova que o CAMINHO existe (com outro método).
METHOD_ABSENT = {405, 501}
PARAM_RE = re.compile(r"\{[^/}]+\}")
VERSION_RE = re.compile(r"^v(\d+)$", re.IGNORECASE)


@dataclass
class Observation:
    """Um endpoint observado como existente."""

    method: str
    path: str                 # caminho concreto pedido (ex.: /users/v1/1)
    template: str | None      # se veio de um template declarado, qual (ex.: /users/v1/{username})
    origem: str               # declarado | prefixo | versao | wordlist
    status: int

    @property
    def key(self) -> str:
        return f"{self.method} {self.template or self.path}"


@dataclass
class Candidate:
    path: str
    template: str | None
    origem: str

    @property
    def kind(self) -> str:
        return "template" if self.template else "literal"


@dataclass
class DiscoveryResult:
    observed: list[Observation] = field(default_factory=list)
    requests: int = 0
    paths_vivos: int = 0
    erros: int = 0
    renovacoes_auth: int = 0


def random_segment() -> str:
    return "zz" + secrets.token_hex(6)


def parent_of(path: str) -> str:
    parent = path.rstrip("/").rsplit("/", 1)[0]
    return parent or ""


def instantiate(template: str, value: str) -> str:
    """`/users/{id}` -> `/users/1`. Valor fixo e registrado (D7)."""
    return PARAM_RE.sub(value, template)


def literal_prefixes(path: str) -> list[str]:
    """Prefixos literais próprios: `/users/v1/{u}/email` -> [/users, /users/v1]."""
    segs = path.strip("/").split("/")
    out = []
    for i in range(1, len(segs)):
        if PARAM_RE.search(segs[i - 1]):
            break
        out.append("/" + "/".join(segs[:i]))
    return out


def version_variants(path: str) -> list[str]:
    """`/api/v2/x` -> [/api/v1/x, /api/v3/x]. Testa de v1 até v(k+1), exceto vk."""
    segs = path.split("/")
    out = []
    for i, s in enumerate(segs):
        m = VERSION_RE.match(s)
        if not m:
            continue
        k = int(m.group(1))
        for v in range(1, k + 2):
            if v != k:
                out.append("/".join(segs[:i] + [f"v{v}"] + segs[i + 1:]))
    return out


def build_candidates(declared: set[Endpoint], wordlist: list[str], param_value: str) -> list[Candidate]:
    """Gera os caminhos da fase A, sem duplicatas."""
    seen: dict[str, Candidate] = {}

    def add(path: str, template: str | None, origem: str) -> None:
        concrete = instantiate(template, param_value) if template else path
        if concrete not in seen:
            seen[concrete] = Candidate(concrete, template, origem)

    declared_paths = sorted({e.path for e in declared})
    for p in declared_paths:
        add(p, p if PARAM_RE.search(p) else None, "declarado")

    # A raiz é sempre candidata (D18). Sem isso, se "/" não estiver na spec, nenhuma
    # outra regra a gera: prefixos próprios nunca incluem a raiz e a wordlist só gera "/palavra".
    add("/", None, "raiz")

    bases = {""}
    for p in declared_paths:
        for pre in literal_prefixes(p):
            add(pre, None, "prefixo")
            bases.add(pre)

    for p in declared_paths:
        for var in version_variants(p):
            add(var, var if PARAM_RE.search(var) else None, "versao")
        for pre in literal_prefixes(p):
            for var in version_variants(pre):
                add(var, None, "versao")
                bases.add(var)

    for base in sorted(bases):
        for word in wordlist:
            add(f"{base}/{word.strip('/')}", None, "wordlist")
    return list(seen.values())


class Discoverer:
    def __init__(
        self,
        base_url: str,
        declared: set[Endpoint],
        wordlist: list[str],
        methods: tuple[str, ...] = DEFAULT_METHODS,
        headers: dict[str, str] | None = None,
        concurrency: int = 10,
        param_value: str = "1",
        timeout: float = 10.0,
        n_baseline: int = 3,
        probe_methods: tuple[str, ...] = ("GET", "POST"),
        auth_refresh=None,
        refresh_every: float = 45.0,
    ):
        """`auth_refresh`: função sem argumentos que devolve headers de autenticação
        novos (ex.: faz login de novo). Se informada, é chamada a cada `refresh_every`
        segundos (D19). Credenciais de vida curta (o JWT do VAmPI vale 60 s) expiram no
        meio de uma execução de vários minutos e transformam "autenticado" em
        "credencial expirada" sem aviso (diário E22). Sem `auth_refresh`, os headers
        são fixos e o comportamento é idêntico ao da versão anterior."""
        self.probe_methods = probe_methods
        self.auth_refresh = auth_refresh
        self.refresh_every = refresh_every
        self._last_refresh = 0.0
        self._refresh_lock = asyncio.Lock()
        self.base_url = base_url.rstrip("/")
        self.declared = declared
        self.wordlist = wordlist
        self.methods = methods
        self.headers = headers or {}
        self.concurrency = concurrency
        self.sem = asyncio.Semaphore(concurrency)
        self.param_value = param_value
        self.timeout = timeout
        self.n_baseline = n_baseline
        self.result = DiscoveryResult()
        self._global: dict[str, list[Resp]] = {}
        self._parent: dict[tuple[str, str], list[Resp]] = {}
        self._parent_locks: dict[tuple[str, str], asyncio.Lock] = {}

    # ---------- HTTP ----------
    async def maybe_refresh_auth(self) -> None:
        """Renova os headers de autenticação se o intervalo venceu (D19)."""
        if self.auth_refresh is None:
            return
        async with self._refresh_lock:
            now = time.monotonic()
            if now - self._last_refresh >= self.refresh_every:
                # auth_refresh é síncrona (httpx.post); roda em thread para não travar o loop.
                self.headers = await asyncio.to_thread(self.auth_refresh)
                self._last_refresh = now
                self.result.renovacoes_auth += 1

    async def request(self, client: httpx.AsyncClient, method: str, path: str) -> Resp | None:
        async with self.sem:
            await self.maybe_refresh_auth()
            self.result.requests += 1
            try:
                # Corpo JSON vazio em métodos com corpo: sem isso, várias APIs
                # respondem 415/400 antes do roteamento e tudo vira ruído.
                kwargs = {"json": {}} if method in ("POST", "PUT", "PATCH") else {}
                # Headers enviados por requisição (e não fixados no cliente) para que a
                # renovação de credencial (D19) valha imediatamente.
                r = await client.request(method, self.base_url + path, headers=self.headers, **kwargs)
            except httpx.HTTPError:
                # Falhas de rede são contadas e reportadas: uma taxa alta de erros
                # invalida a execução (endpoints não sondados viram falso negativo).
                self.result.erros += 1
                return None
        ctype = r.headers.get("content-type", "").split(";")[0].strip()
        return Resp(method, path, r.status_code, ctype, r.text)

    # ---------- baselines ----------
    async def build_global_baselines(self, client: httpx.AsyncClient) -> None:
        for m in dict.fromkeys(self.methods + self.probe_methods):
            paths = []
            for _ in range(self.n_baseline):
                paths.append("/" + random_segment())
                paths.append("/" + random_segment() + "/" + random_segment())
            resps = await asyncio.gather(*(self.request(client, m, p) for p in paths))
            self._global[m] = [r for r in resps if r]

    async def parent_baseline(self, client: httpx.AsyncClient, method: str, parent: str) -> list[Resp]:
        key = (method, parent)
        lock = self._parent_locks.setdefault(key, asyncio.Lock())
        async with lock:
            if key not in self._parent:
                resps = await asyncio.gather(
                    *(self.request(client, method, f"{parent}/{random_segment()}") for _ in range(2))
                )
                self._parent[key] = [r for r in resps if r]
        return self._parent[key]

    async def looks_not_found(self, client: httpx.AsyncClient, resp: Resp, cand: Candidate) -> bool:
        if any(same_response(resp, b) for b in self._global.get(resp.method, [])):
            return True
        if cand.kind == "literal":
            parent = parent_of(cand.path)
            for b in await self.parent_baseline(client, resp.method, parent):
                if same_response(resp, b):
                    return True
        return False

    # ---------- fases ----------
    async def path_alive(self, client: httpx.AsyncClient, cand: Candidate) -> tuple[bool, dict[str, Resp]]:
        """Fase A: o caminho existe (com qualquer método)?

        Sonda com `probe_methods` (padrão GET e POST — D10). Só GET não basta:
        se `GET /users/v1/{username}` existe, `GET /users/v1/register` responde
        "usuário não encontrado" e esconde a rota `POST /users/v1/register`.
        """
        cache: dict[str, Resp] = {}
        alive = False
        for m in self.probe_methods:
            resp = await self.request(client, m, cand.path)
            if resp is None:
                continue
            cache[m] = resp
            if resp.status in METHOD_ABSENT:
                # 405 prova que o caminho existe — a menos que o pai inteiro dê 405
                # (aí o 405 vem de um template, não deste caminho).
                if resp.status == 405 and not await self.looks_not_found(client, resp, cand):
                    alive = True
            elif not await self.looks_not_found(client, resp, cand):
                alive = True
            if alive:
                break
        return alive, cache

    async def probe_method(self, client, cand: Candidate, method: str, cached: dict[str, Resp]) -> None:
        resp = cached.get(method) or await self.request(client, method, cand.path)
        if resp is None or resp.status in METHOD_ABSENT:
            return
        if await self.looks_not_found(client, resp, cand):
            return
        self.result.observed.append(Observation(method, cand.path, cand.template, cand.origem, resp.status))

    async def infer_wildcards(self, client: httpx.AsyncClient, parents: list[str]) -> None:
        """Fase C — rota-coringa inferida.

        Se `/books/v1/<aleatório>` NÃO responde como o "não encontrado" global,
        existe uma rota com parâmetro sob `/books/v1` (ex.: `/books/v1/{book_title}`),
        mesmo que nenhuma palavra da wordlist a revele. Registramos como
        `/books/v1/{param}`; o motor diferencial casa por template, ignorando o
        nome do parâmetro.
        """
        async def check(parent: str, method: str) -> None:
            resps = await self.parent_baseline(client, method, parent)
            if not resps or any(r.status in METHOD_ABSENT for r in resps):
                return
            for r in resps:
                if any(same_response(r, b) for b in self._global.get(method, [])):
                    return
            tpl = f"{parent}/{{param}}"
            self.result.observed.append(Observation(method, tpl, tpl, "coringa", resps[0].status))

        await asyncio.gather(*(check(p, m) for p in parents for m in self.methods))

    async def run(self) -> DiscoveryResult:
        candidates = build_candidates(self.declared, self.wordlist, self.param_value)
        limits = httpx.Limits(max_connections=self.concurrency)
        async with httpx.AsyncClient(timeout=self.timeout, limits=limits,
                                     follow_redirects=False) as client:
            await self.build_global_baselines(client)

            # Fase A
            alive_flags = await asyncio.gather(*(self.path_alive(client, c) for c in candidates))
            alive = [(c, resp) for c, (ok, resp) in zip(candidates, alive_flags)
                     if ok or c.origem == "declarado"]
            self.result.paths_vivos = len(alive)

            # Fase B
            await asyncio.gather(*(
                self.probe_method(client, c, m, resp) for c, resp in alive for m in self.methods
            ))

            # Fase C — sob cada caminho literal vivo
            parents = sorted({c.path for c, _ in alive if c.kind == "literal"})
            await self.infer_wildcards(client, parents)
        self.result.observed.sort(key=lambda o: (o.path, o.method))
        return self.result


def load_wordlist(paths: list[str]) -> list[str]:
    words: dict[str, None] = {}
    for p in paths:
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                w = line.strip()
                if w and not w.startswith("#") and "%" not in w and w != "@":
                    words[w.strip("/")] = None
    return list(words)
