"""Cálculo de precisão, revocação e F1 contra o ground truth.

- VP (verdadeiro positivo): shadow reportado que está no ground truth
- FP (falso positivo):      shadow reportado que NÃO está no ground truth
- FN (falso negativo):      endpoint do ground truth que não foi reportado

Atenção a um detalhe de método: a spec ORIGINAL pode não ser completa. Um FP
pode ser um shadow REAL da API original (não declarado nem na spec completa).
Por isso os FPs são listados nominalmente, para inspeção manual no artigo.
"""

from __future__ import annotations

from shadowscan.diff import Shadow, canonical


def _key(method: str, path: str) -> tuple[str, str]:
    return (method, canonical(path))


def evaluate(shadows: list[Shadow], removed: list[dict], intrinsecos: list[str] | None = None) -> dict:
    """`intrinsecos`: shadows REAIS da API original (achados com a spec completa e
    verificados manualmente, ex.: "GET /console"). São retirados do conjunto
    reportado antes de contar FP — não são erro da ferramenta (D9)."""
    intr = set()
    for s in intrinsecos or []:
        m, _, p = s.partition(" ")
        intr.add(_key(m, p))
    reported = {s.key for s in shadows} - intr
    truth = {_key(r["method"], r["path"]): r for r in removed}

    vp = reported & truth.keys()
    fp = reported - truth.keys()
    fn = truth.keys() - reported

    p = len(vp) / len(reported) if reported else 0.0
    r = len(vp) / len(truth) if truth else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0

    por_tipo = {}
    for tipo in sorted({t.get("tipo", "?") for t in truth.values()}):
        keys = {k for k, v in truth.items() if v.get("tipo") == tipo}
        por_tipo[tipo] = {"total": len(keys), "encontrados": len(keys & vp)}

    fmt = lambda ks: sorted(f"{m} {p}" for m, p in ks)
    return {
        "intrinsecos_excluidos": len(intr),
        "vp": len(vp), "fp": len(fp), "fn": len(fn),
        "precisao": round(p, 4), "revocacao": round(r, 4), "f1": round(f1, 4),
        "revocacao_por_tipo": por_tipo,
        "lista_vp": fmt(vp), "lista_fp": fmt(fp), "lista_fn": fmt(fn),
    }
