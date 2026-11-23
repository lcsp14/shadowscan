"""CLI: python -m shadowscan --url http://127.0.0.1:5000 --spec spec.yml [--ground-truth gt.json]"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from shadowscan.classify import classify_all
from shadowscan.diff import compute_diff
from shadowscan.discovery import DEFAULT_METHODS, Discoverer, load_wordlist
from shadowscan.metrics import evaluate
from shadowscan.responses import SIMILARITY_THRESHOLD
from shadowscan.spec_parser import parse_spec_file

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORDLISTS = [str(ROOT / "wordlists" / "seclists_objects.txt"),
                     str(ROOT / "wordlists" / "seclists_actions.txt")]


def parse_headers(raw: list[str]) -> dict[str, str]:
    out = {}
    for h in raw:
        k, _, v = h.partition(":")
        out[k.strip()] = v.strip()
    return out


def scan(url: str, spec: str, wordlists: list[str], headers: dict[str, str], concurrency: int,
         template_policy: str, param_value: str, methods: tuple[str, ...],
         probe_methods: tuple[str, ...] = ("GET", "POST"), auth_refresh=None,
         refresh_every: float = 45.0) -> dict:
    declared = parse_spec_file(spec)
    words = load_wordlist(wordlists)
    t0 = time.perf_counter()
    disc = asyncio.run(Discoverer(url, declared, words, methods=methods, headers=headers,
                                  concurrency=concurrency, param_value=param_value,
                                  probe_methods=probe_methods, auth_refresh=auth_refresh,
                                  refresh_every=refresh_every).run())
    elapsed = time.perf_counter() - t0
    diff = compute_diff(declared, disc.observed, template_policy)
    classify_all(diff.shadow, declared)
    return {
        "config": {
            "url": url, "spec": spec, "wordlists": wordlists, "n_palavras": len(words),
            "metodos": list(methods), "metodos_fase_a": list(probe_methods), "concorrencia": concurrency, "template_policy": template_policy,
            "param_value": param_value, "limiar_similaridade": SIMILARITY_THRESHOLD,
            "autenticado": bool(headers) or auth_refresh is not None,
            "renovacao_auth_s": refresh_every if auth_refresh is not None else None,
        },
        "execucao": {"requisicoes": disc.requests, "erros": disc.erros, "renovacoes_auth": disc.renovacoes_auth, "caminhos_vivos": disc.paths_vivos,
                     "segundos": round(elapsed, 2)},
        "n_declarados": len(declared),
        "shadow": [asdict(s) for s in diff.shadow],
        "zombie": [str(e) for e in diff.zombie],
        "ambiguos": [asdict(s) for s in diff.ambiguos],
        "observados": [asdict(o) for o in disc.observed],
        "_diff": diff,
    }


def print_report(report: dict, console: Console) -> None:
    t = Table(title=f"Shadow endpoints ({len(report['shadow'])})")
    for col in ("Método", "Caminho", "Categoria", "Status", "Origem", "Colide com"):
        t.add_column(col)
    for s in report["shadow"]:
        t.add_row(s["method"], s["path"], s["categoria"], str(s["status"]), s["origem"], s["ambiguo_com"] or "")
    console.print(t)
    if report["zombie"]:
        console.print(f"[yellow]Zombie (declarados sem resposta):[/] {', '.join(report['zombie'])}")
    ex = report["execucao"]
    console.print(f"{ex['requisicoes']} requisições, {ex['caminhos_vivos']} caminhos vivos, {ex['segundos']}s")
    if "metricas" in report:
        m = report["metricas"]
        console.print(f"[bold]Precisão {m['precisao']:.2f} | Revocação {m['revocacao']:.2f} | F1 {m['f1']:.2f}[/]"
                      f"  (VP={m['vp']} FP={m['fp']} FN={m['fn']})")
        if m["lista_fp"]:
            console.print(f"  FP: {m['lista_fp']}")
        if m["lista_fn"]:
            console.print(f"  FN: {m['lista_fn']}")


def main() -> None:
    ap = argparse.ArgumentParser(prog="shadowscan", description="Detector de shadow endpoints em APIs REST")
    ap.add_argument("--url", required=True, help="URL base da API (somente alvos locais/autorizados)")
    ap.add_argument("--spec", required=True, help="especificação OpenAPI (JSON/YAML)")
    ap.add_argument("--ground-truth", help="ground_truth.json para calcular precisão/revocação/F1")
    ap.add_argument("--wordlist", nargs="*", default=DEFAULT_WORDLISTS)
    ap.add_argument("-H", "--header", action="append", default=[], help="ex.: 'Authorization: Bearer X'")
    ap.add_argument("-c", "--concurrency", type=int, default=10)
    ap.add_argument("--template-policy", choices=["declarado", "shadow"], default="declarado")
    ap.add_argument("--param-value", default="1", help="valor usado para instanciar {param}")
    ap.add_argument("--methods", nargs="*", default=list(DEFAULT_METHODS))
    ap.add_argument("--probe-methods", nargs="*", default=["GET", "POST"], help="métodos da fase A")
    ap.add_argument("--intrinsecos", help="JSON com lista de shadows reais da API original (excluídos do FP)")
    ap.add_argument("-o", "--out", help="arquivo JSON de saída")
    args = ap.parse_args()

    report = scan(args.url, args.spec, args.wordlist, parse_headers(args.header), args.concurrency,
                  args.template_policy, args.param_value, tuple(m.upper() for m in args.methods),
                  tuple(m.upper() for m in args.probe_methods))
    diff = report.pop("_diff")
    if args.ground_truth:
        gt = json.loads(Path(args.ground_truth).read_text(encoding="utf-8"))
        report["ground_truth"] = args.ground_truth
        intr = json.loads(Path(args.intrinsecos).read_text(encoding="utf-8")) if args.intrinsecos else []
        report["metricas_brutas"] = evaluate(diff.shadow, gt["removidos"])
        report["metricas"] = evaluate(diff.shadow, gt["removidos"], intr)

    print_report(report, Console())
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
