"""Módulo [3] — Motor diferencial.

Calcula O \\ D (shadow) e D \\ O (zombie), com casamento por TEMPLATE.

Por que não basta comparar strings: a spec declara `/users/{id}` e a descoberta
observa `/users/42`. São o mesmo endpoint. Comparando strings, todo endpoint com
parâmetro viraria um shadow falso (e um zombie falso). Por isso cada caminho
observado é casado contra os templates declarados, segmento a segmento,
tratando `{param}` como coringa que casa com exatamente UM segmento.

Ordem de precedência (D8 em docs/decisoes.md):
  1. casamento literal exato  (`/users/v1/login` == `/users/v1/login`)
  2. casamento por template    (`/users/v1/admin` ~ `/users/v1/{username}`)
O caso 2 é ambíguo: `/users/v1/admin` pode ser um usuário chamado "admin" OU
uma rota escondida que colide com o template. A política é configurável
(`template_policy`): "declarado" (padrão, conservador: assume que é o template)
ou "shadow". Os casos ambíguos são sempre listados no relatório.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from shadowscan.discovery import Observation
from shadowscan.spec_parser import Endpoint

PARAM_RE = re.compile(r"\{[^/}]+\}")


def canonical(path: str) -> str:
    """Nome do parâmetro não importa: `/u/{id}` e `/u/{user_id}` são o mesmo template."""
    return PARAM_RE.sub("{}", path)


def segments(path: str) -> list[str]:
    return [s for s in path.split("/") if s]


def matches_template(concrete: str, template: str) -> bool:
    """Casa caminho concreto contra template, segmento a segmento."""
    cs, ts = segments(concrete), segments(template)
    if len(cs) != len(ts):
        return False
    return all(t == c or PARAM_RE.fullmatch(t) for c, t in zip(cs, ts))


@dataclass
class Shadow:
    method: str
    path: str               # forma template quando conhecida
    origem: str
    status: int
    ambiguo_com: str | None = None  # template declarado com o qual colide
    categoria: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.method, canonical(self.path))


@dataclass
class DiffResult:
    shadow: list[Shadow] = field(default_factory=list)
    zombie: list[Endpoint] = field(default_factory=list)
    declarados_vistos: list[Endpoint] = field(default_factory=list)
    ambiguos: list[Shadow] = field(default_factory=list)


def compute_diff(declared: set[Endpoint], observed: list[Observation],
                 template_policy: str = "declarado") -> DiffResult:
    by_key = {(e.method, canonical(e.path)): e for e in declared}
    templated = [e for e in declared if PARAM_RE.search(e.path)]
    # D21: templates OBSERVADOS e não declarados (ex.: rota-coringa da fase C,
    # `/users/v1/{param}`). Um caminho literal que casa com um deles é o mesmo endpoint
    # (ex.: `/users/v1/admin`, usuário real) e não deve virar um segundo shadow.
    shadow_templates = sorted({
        (o.method, o.template) for o in observed
        if o.template and (o.method, canonical(o.template)) not in by_key
    })
    seen_declared: set[Endpoint] = set()
    shadows: dict[tuple[str, str], Shadow] = {}
    result = DiffResult()

    for o in observed:
        path = o.template or o.path
        key = (o.method, canonical(path))

        # 1) literal exato (ou mesmo template)
        if key in by_key:
            seen_declared.add(by_key[key])
            continue

        # 2) por template (só faz sentido para caminhos concretos)
        hit = None
        if o.template is None:
            hit = next((e for e in templated if e.method == o.method and matches_template(o.path, e.path)), None)
        if hit is not None:
            s = Shadow(o.method, o.path, o.origem, o.status, ambiguo_com=hit.path)
            result.ambiguos.append(s)
            if template_policy == "declarado":
                seen_declared.add(hit)
                continue

        # 3) literal que casa com um template observado como shadow (D21): agrupa nele
        if o.template is None and hit is None:
            stpl = next((t for m, t in shadow_templates if m == o.method and matches_template(o.path, t)), None)
            if stpl is not None:
                result.ambiguos.append(Shadow(o.method, o.path, o.origem, o.status, ambiguo_com=stpl))
                if template_policy == "declarado":
                    continue

        if key not in shadows:
            shadows[key] = Shadow(o.method, path, o.origem, o.status,
                                  ambiguo_com=hit.path if hit else None)

    result.shadow = sorted(shadows.values(), key=lambda s: (s.path, s.method))
    result.declarados_vistos = sorted(seen_declared, key=lambda e: (e.path, e.method))
    result.zombie = sorted(declared - seen_declared, key=lambda e: (e.path, e.method))
    return result
