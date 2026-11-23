"""Gera uma spec OpenAPI 3 mínima a partir de um routes/api.php do Laravel.

Usado no vAPI, que não publica spec OpenAPI (só coleção Postman). Derivar a spec
da tabela de rotas do framework garante que ela seja COMPLETA e VERIFICÁVEL — o
pré-requisito do método de degradação (seção 5 do briefing). Registrado em D16.

Uso:
    python -m experiments.laravel_routes_to_openapi envs/vapi/vapi/routes/api.php --prefix /vapi -o specs/vapi_openapi3.yml
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

ROUTE_RE = re.compile(r"Route::(?:[a-z]+\([^)]*\)->)*(get|post|put|patch|delete)\(\s*'([^']+)'", re.IGNORECASE)


def convert(php: str, prefix: str, title: str) -> dict:
    # Ignora linhas comentadas (// ...) — rotas desativadas não existem.
    lines = [l for l in php.splitlines() if not l.strip().startswith("//")]
    paths: dict[str, dict] = {}
    for method, path in ROUTE_RE.findall("\n".join(lines)):
        p = "/" + path.strip("/")
        paths.setdefault(p, {})[method.lower()] = {"responses": {"200": {"description": "ok"}}}
    return {
        "openapi": "3.0.0",
        "info": {"title": title, "version": "1.0", "description": "Gerada de routes/api.php"},
        "servers": [{"url": prefix}],
        "paths": dict(sorted(paths.items())),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("routes")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--title", default="API")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    spec = convert(Path(a.routes).read_text(encoding="utf-8"), a.prefix, a.title)
    Path(a.out).write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    n = sum(len(v) for v in spec["paths"].values())
    print(f"{n} operações em {len(spec['paths'])} caminhos -> {a.out}")


if __name__ == "__main__":
    main()
