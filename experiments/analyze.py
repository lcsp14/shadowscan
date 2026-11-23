"""Agrega uma ou mais baterias em tabelas para o artigo. NÃO executa nada contra o alvo.

Recalcula as métricas a partir de resultado.json + ground_truth.json de cada
execução (a lista de shadows intrínsecos pode ser revisada sem reexecutar).

Três níveis de métrica (D17 em docs/decisoes.md):
- FIM-A-FIM: descoberta + diferencial (P, R, F1). Desempenho prático da ferramenta.
- DESCOBERTA: dos endpoints removidos (ground truth), quantos a descoberta ativa
  observou respondendo (estão em O)?
- DIFERENCIAL ISOLADO: dos removidos que a descoberta observou, quantos o motor
  diferencial classificou corretamente como shadow? Isola a contribuição central.
  Revocação fim-a-fim = revocação da descoberta × revocação do diferencial.

Sempre emite duas versões (D9): BRUTA (sem excluir intrínsecos) e AJUSTADA.
Também reporta contagem por CAMINHO único, além de por (método, caminho).

Uso:
    python -m experiments.analyze runs/exp_vampi_principal --intrinsecos specs/vampi_intrinsecos.json
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

from shadowscan.diff import Shadow, canonical, matches_template
from shadowscan.metrics import evaluate


def _gt_key(r: dict) -> tuple[str, str]:
    return (r["method"], canonical(r["path"]))


def discovered_gt(observed: list[dict], removed: list[dict]) -> set[tuple[str, str]]:
    """Endpoints do ground truth que estão em O (a descoberta os viu respondendo).

    Um removido conta como descoberto se alguma observação, do mesmo método:
    - tem a mesma chave canônica (literal ou template, ex.: /books/v1/{param} da fase C); ou
    - é um caminho concreto que casa com o template removido (ex.: /books/v1/1).
    """
    found = set()
    for r in removed:
        k = _gt_key(r)
        for o in observed:
            if o["method"] != r["method"]:
                continue
            path = o["template"] or o["path"]
            if canonical(path) == k[1] or (o["template"] is None and matches_template(o["path"], r["path"])):
                found.add(k)
                break
    return found


def path_metrics(shadows: list[Shadow], removed: list[dict], intr: list[str]) -> dict:
    """Mesmas contas, mas a unidade é o CAMINHO (ignora o método)."""
    intr_paths = {canonical(s.partition(" ")[2]) for s in intr}
    rep = {canonical(s.path) for s in shadows} - intr_paths
    truth = {canonical(r["path"]) for r in removed}
    vp = rep & truth
    p = len(vp) / len(rep) if rep else 0.0
    r = len(vp) / len(truth) if truth else 0.0
    return {"precisao": p, "revocacao": r, "f1": 2 * p * r / (p + r) if p + r else 0.0,
            "vp": len(vp), "fp": len(rep - truth), "fn": len(truth - rep)}


def load_runs(batch: Path, intr: list[str]) -> list[dict]:
    rows = []
    for run in sorted(p for p in batch.iterdir() if (p / "resultado.json").exists()):
        rep = json.loads((run / "resultado.json").read_text(encoding="utf-8"))
        gt = json.loads((run / "ground_truth.json").read_text(encoding="utf-8"))
        removed = gt["removidos"]
        if not removed:  # N=0: execução de levantamento de intrínsecos, sem métrica
            continue
        shadows = [Shadow(s["method"], s["path"], s["origem"], s["status"], s["ambiguo_com"], s["categoria"])
                   for s in rep["shadow"]]
        adj = evaluate(shadows, removed, intr)
        raw = evaluate(shadows, removed)
        pth = path_metrics(shadows, removed, intr)

        reported = {s.key for s in shadows}
        disc = discovered_gt(rep["observados"], removed)
        diff_ok = disc & reported
        tipos = adj["revocacao_por_tipo"]
        rows.append({
            "execucao": run.name, "n": gt["n"], "seed": gt["seed"],
            "auth": "sim" if rep["config"]["autenticado"] else "nao",
            # fim-a-fim ajustada
            "precisao": adj["precisao"], "revocacao": adj["revocacao"], "f1": adj["f1"],
            "vp": adj["vp"], "fp": adj["fp"], "fn": adj["fn"],
            # fim-a-fim bruta
            "precisao_bruta": raw["precisao"], "f1_bruto": raw["f1"], "fp_bruto": raw["fp"],
            # decomposição
            "gt_total": len(removed), "gt_descobertos": len(disc), "gt_diferencial_ok": len(diff_ok),
            "rev_descoberta": len(disc) / len(removed),
            "rev_diferencial": (len(diff_ok) / len(disc)) if disc else None,
            # por caminho único
            "precisao_caminho": round(pth["precisao"], 4), "revocacao_caminho": round(pth["revocacao"], 4),
            "f1_caminho": round(pth["f1"], 4),
            # por tipo de remoção
            "gt_caminho": tipos.get("caminho", {}).get("total", 0),
            "vp_caminho": tipos.get("caminho", {}).get("encontrados", 0),
            "gt_metodo": tipos.get("metodo", {}).get("total", 0),
            "vp_metodo": tipos.get("metodo", {}).get("encontrados", 0),
            "requisicoes": rep["execucao"]["requisicoes"], "erros": rep["execucao"].get("erros", 0),
            "segundos": rep["execucao"]["segundos"],
            "fn_lista": adj["lista_fn"], "fp_lista": adj["lista_fp"],
            "fn_nao_descobertos": sorted(f"{m} {p}" for m, p in {_gt_key(r) for r in removed} - disc),
            "fn_diferencial": sorted(f"{m} {p}" for m, p in disc - reported),
        })
    return rows


def ms(vals: list) -> str:
    vals = [v for v in vals if v is not None]
    if not vals:
        return "-"
    if len(vals) == 1:
        return f"{vals[0]:.2f}"
    return f"{st.mean(vals):.2f} ± {st.stdev(vals):.2f}"


def table(groups: dict, header: list[str], cells) -> list[str]:
    out = ["| Auth | N | Exec. | " + " | ".join(header) + " |", "|---" * (3 + len(header)) + "|"]
    for (auth, n), rs in sorted(groups.items()):
        out.append(f"| {auth} | {n} | {len(rs)} | " + " | ".join(cells(rs)) + " |")
    return out


def frac(rs: list[dict], num: str, den: str) -> str:
    a, b = sum(r[num] for r in rs), sum(r[den] for r in rs)
    return f"{a}/{b} ({a / b:.2f})" if b else "-"


def summarize(rows: list[dict]) -> str:
    groups = defaultdict(list)
    for r in rows:
        groups[(r["auth"], r["n"])].append(r)
    g = lambda k: lambda rs: ms([r[k] for r in rs])

    out = ["## Tabela 1 — Fim-a-fim: bruta × ajustada (D9)\n",
           "Bruta = sem excluir shadows intrínsecos. Ajustada = intrínsecos verificados excluídos do FP.\n"]
    out += table(groups, ["Precisão bruta", "Precisão ajustada", "F1 bruto", "F1 ajustado", "Revocação",
                          "FP bruto (soma)", "FP ajustado (soma)"],
                 lambda rs: [g("precisao_bruta")(rs), g("precisao")(rs), g("f1_bruto")(rs), g("f1")(rs),
                             g("revocacao")(rs), str(sum(r["fp_bruto"] for r in rs)), str(sum(r["fp"] for r in rs))])

    out += ["\n## Tabela 2 — Decomposição da revocação (D17)\n",
            "Revocação fim-a-fim = descoberta × diferencial. Somas sobre todas as execuções do grupo.\n"]
    out += table(groups, ["Removidos descobertos (descoberta)", "Descobertos classificados shadow (diferencial)",
                          "Revocação fim-a-fim"],
                 lambda rs: [frac(rs, "gt_descobertos", "gt_total"),
                             frac(rs, "gt_diferencial_ok", "gt_descobertos"),
                             frac(rs, "vp", "gt_total")])

    out += ["\n## Tabela 3 — Por caminho único × por (método, caminho)\n"]
    out += table(groups, ["Precisão (endpoint)", "Precisão (caminho)", "Revocação (endpoint)",
                          "Revocação (caminho)", "F1 (endpoint)", "F1 (caminho)"],
                 lambda rs: [g("precisao")(rs), g("precisao_caminho")(rs), g("revocacao")(rs),
                             g("revocacao_caminho")(rs), g("f1")(rs), g("f1_caminho")(rs)])

    out += ["\n## Tabela 4 — Revocação por tipo de remoção e custo\n"]
    out += table(groups, ["Rev. tipo caminho", "Rev. tipo método", "Requisições", "Erros (soma)", "Tempo (s)"],
                 lambda rs: [frac(rs, "vp_caminho", "gt_caminho"), frac(rs, "vp_metodo", "gt_metodo"),
                             g("requisicoes")(rs), str(sum(r["erros"] for r in rs)), g("segundos")(rs)])

    def recurring(key: str) -> list[str]:
        c = defaultdict(int)
        for r in rows:
            for x in r[key]:
                c[x] += 1
        return [f"- `{k}`: {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))] or ["- nenhum"]

    out += ["\n## FN por causa (endpoint: nº de execuções)\n", "**Não descobertos (limite da descoberta/wordlist)**\n"]
    out += recurring("fn_nao_descobertos")
    out += ["\n**Descobertos mas não classificados como shadow (limite do diferencial)**\n"]
    out += recurring("fn_diferencial")
    out += ["\n## Falsos positivos ajustados\n"]
    out += recurring("fp_lista")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", nargs="+", help="um ou mais diretórios de bateria")
    ap.add_argument("--intrinsecos")
    ap.add_argument("--out", help="diretório de saída (padrão: o primeiro batch)")
    a = ap.parse_args()
    intr = json.loads(Path(a.intrinsecos).read_text(encoding="utf-8")) if a.intrinsecos else []
    rows = [r for b in a.batch for r in load_runs(Path(b), intr)]
    if not rows:
        raise SystemExit("nenhuma execução com ground truth não vazio encontrada")
    md = summarize(rows)
    out = Path(a.out or a.batch[0])
    (out / "resumo.md").write_text(md, encoding="utf-8")
    with open(out / "metricas_recalculadas.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(md)


if __name__ == "__main__":
    main()
