"""Módulo [1] — Parser de especificação OpenAPI 3.x.

Lê um arquivo JSON ou YAML e devolve o conjunto D de endpoints declarados,
cada um como um par (método HTTP, caminho-template).

Decisão de design: o caminho é mantido em forma de TEMPLATE (`/users/{id}`),
sem expandir parâmetros. É o motor diferencial (módulo 3) que vai casar
caminhos observados (`/users/42`) contra esses templates.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml

# Chaves de um Path Item do OpenAPI 3 que representam operações HTTP.
# Outras chaves possíveis ("parameters", "summary", "servers"...) NÃO são métodos
# e precisam ser ignoradas.
HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


@dataclass(frozen=True, order=True)
class Endpoint:
    """Um endpoint = método + caminho. `frozen` permite usar em set (operações de conjunto)."""

    method: str  # sempre em maiúsculas: "GET", "POST"...
    path: str    # caminho completo (com base path do servidor), em forma de template

    def __str__(self) -> str:
        return f"{self.method} {self.path}"


def load_spec(spec_path: str | Path) -> dict:
    """Carrega a especificação como dicionário. Aceita .json, .yml e .yaml."""
    text = Path(spec_path).read_text(encoding="utf-8")
    if str(spec_path).lower().endswith(".json"):
        return json.loads(text)
    # YAML é superconjunto de JSON, então serve como fallback para qualquer extensão.
    return yaml.safe_load(text)


def normalize_path(path: str) -> str:
    """Normalização mínima e explícita de caminho (registrada em docs/decisoes.md):
    - garante barra inicial;
    - remove barra final (exceto na raiz "/"), pois `/users/` e `/users`
      são tratados como o mesmo endpoint.
    """
    if not path.startswith("/"):
        path = "/" + path
    if len(path) > 1:
        path = path.rstrip("/")
    return path


def base_path(spec: dict) -> str:
    """Prefixo de caminho vindo de `servers[0].url` (ex.: 'http://x/api' -> '/api').

    No OpenAPI 3, os caminhos em `paths` são relativos ao servidor. Se o servidor
    declarar um prefixo, ele precisa ser somado ao caminho, senão comparamos
    `/users` (spec) com `/api/users` (observado) e geramos falso positivo.
    """
    servers = spec.get("servers") or []
    if not servers:
        return ""
    prefix = urlparse(servers[0].get("url", "")).path
    return prefix.rstrip("/")


def parse_spec(spec: dict) -> set[Endpoint]:
    """Extrai o conjunto D de endpoints declarados de uma spec já carregada."""
    prefix = base_path(spec)
    declared: set[Endpoint] = set()
    for raw_path, path_item in (spec.get("paths") or {}).items():
        full_path = normalize_path(prefix + raw_path)
        for key in path_item or {}:
            if key.lower() in HTTP_METHODS:
                declared.add(Endpoint(key.upper(), full_path))
    return declared


def parse_spec_file(spec_path: str | Path) -> set[Endpoint]:
    return parse_spec(load_spec(spec_path))


if __name__ == "__main__":
    # Uso: python -m shadowscan.spec_parser specs/vampi_openapi3.yml
    endpoints = parse_spec_file(sys.argv[1])
    for ep in sorted(endpoints, key=lambda e: (e.path, e.method)):
        print(ep)
    print(f"\nTotal: {len(endpoints)} endpoints declarados")
