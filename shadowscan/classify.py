"""Módulo [4a] — Classificação heurística dos shadow endpoints.

Regras aplicadas em ordem; a primeira que casar define a categoria.
Comparação por segmento inteiro, ignorando maiúsculas e `_`/`-` nas pontas
(`_internal`, `debug-`, `Admin` casam).
"""

from __future__ import annotations

import re

from shadowscan.diff import Shadow, canonical, segments
from shadowscan.spec_parser import Endpoint

VERSION_RE = re.compile(r"^v\d+$", re.IGNORECASE)
DEBUG_WORDS = {"debug", "test", "tests", "testing", "dev", "internal", "actuator", "trace", "dump", "phpinfo"}
ADMIN_WORDS = {"admin", "administrator", "manage", "management", "console", "dashboard", "superuser"}

VERSAO = "versao_obsoleta"
DEBUG = "rota_debug"
ADMIN = "administrativo"
OUTRO = "nao_classificado"


def _clean(seg: str) -> str:
    return seg.lower().strip("_-.")


def differs_only_by_version(a: str, b: str) -> bool:
    sa, sb = segments(canonical(a)), segments(canonical(b))
    if len(sa) != len(sb):
        return False
    diffs = [(x, y) for x, y in zip(sa, sb) if x != y]
    return len(diffs) == 1 and all(VERSION_RE.match(s) for s in diffs[0])


def classify(shadow: Shadow, declared: set[Endpoint]) -> str:
    if any(differs_only_by_version(shadow.path, e.path) for e in declared):
        return VERSAO
    segs = {_clean(s) for s in segments(shadow.path)}
    if segs & DEBUG_WORDS:
        return DEBUG
    if segs & ADMIN_WORDS:
        return ADMIN
    return OUTRO


def classify_all(shadows: list[Shadow], declared: set[Endpoint]) -> None:
    for s in shadows:
        s.categoria = classify(s, declared)
