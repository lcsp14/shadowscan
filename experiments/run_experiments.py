"""Bateria de experimentos: varia N (nº de remoções), semente e autenticação.

Para cada combinação:
  1. reseta o banco do alvo (estado reprodutível);
  2. gera spec degradada + ground truth;
  3. executa a ferramenta;
  4. calcula métricas e grava uma linha no CSV.

Uso (VAmPI):
    python -m experiments.run_experiments --alvo vampi --n 3 6 --seeds 1 2 3 4 5 --auth nao sim
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import httpx
import yaml

from shadowscan.__main__ import DEFAULT_WORDLISTS, scan
from shadowscan.ground_truth import degrade
from shadowscan.metrics import evaluate
from shadowscan.spec_parser import load_spec

ROOT = Path(__file__).resolve().parent.parent

ALVOS = {
    "vampi": {
        "url": "http://127.0.0.1:5000",
        "spec": ROOT / "specs" / "vampi_openapi3.yml",
        "intrinsecos": ROOT / "specs" / "vampi_intrinsecos.json",
    },
    "vapi": {
        "url": "http://127.0.0.1:8000",
        "spec": ROOT / "specs" / "vapi_openapi3.yml",
        "intrinsecos": ROOT / "specs" / "vapi_intrinsecos.json",
    },
}


def vampi_reset(url: str) -> None:
    httpx.get(f"{url}/createdb", timeout=30)


def vampi_token(url: str) -> dict[str, str]:
    """Cria (ou reaproveita) um usuário comum e devolve o header de autenticação."""
    cred = {"username": "tcc_scanner", "password": "tcc_scanner_pw", "email": "scanner@tcc.local"}
    httpx.post(f"{url}/users/v1/register", json=cred, timeout=30)
    r = httpx.post(f"{url}/users/v1/login", json={k: cred[k] for k in ("username", "password")}, timeout=30)
    return {"Authorization": f"Bearer {r.json()['auth_token']}"}


RESET = {"vampi": vampi_reset, "vapi": lambda url: None}
# vAPI: cada sub-API (api1..api10) tem esquema de autenticação próprio -> só modo sem auth.
AUTH = {"vampi": vampi_token}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo", default="vampi", choices=ALVOS)
    ap.add_argument("--n", type=int, nargs="+", default=[3, 6])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    ap.add_argument("--auth", nargs="+", default=["nao", "sim"], choices=["nao", "sim"])
    ap.add_argument("--template-policy", default="declarado", choices=["declarado", "shadow"])
    ap.add_argument("-c", "--concurrency", type=int, default=10)
    ap.add_argument("--out", default=None)
    ap.add_argument("--retomar", action="store_true",
                    help="pula execuções que já têm resultado.json (retomada após interrupção; diário E33)")
    args = ap.parse_args()

    alvo = ALVOS[args.alvo]
    url = alvo["url"]
    spec = load_spec(alvo["spec"])
    intr = json.loads(alvo["intrinsecos"].read_text(encoding="utf-8")) if alvo["intrinsecos"].exists() else []
    out = Path(args.out or ROOT / "runs" / f"exp_{args.alvo}_{time.strftime('%Y%m%d_%H%M%S')}")
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    if args.alvo not in AUTH:
        args.auth = ["nao"]
    for auth in args.auth:
        for n in args.n:
            for seed in args.seeds:
                tag = f"n{n}_s{seed}_auth-{auth}"
                if args.retomar and (out / tag / "resultado.json").exists():
                    print(f"[{tag}] já concluída — pulada (--retomar)", flush=True)
                    continue
                # Execução sem resultado.json = interrompida: é refeita do zero (spec e
                # ground truth são regenerados pela semente, idênticos aos anteriores).
                print(f"[{tag}] ...", flush=True)
                RESET[args.alvo](url)
                # D19: com auth, a ferramenta renova o login durante a execução
                # (o JWT do VAmPI vale 60 s; ver diário E22).
                refresh = (lambda u=url: AUTH[args.alvo](u)) if auth == "sim" else None
                headers = AUTH[args.alvo](url) if auth == "sim" else {}

                degraded, removed = degrade(spec, n, seed)
                run_dir = out / tag
                run_dir.mkdir(exist_ok=True)
                spec_path = run_dir / "spec_degradada.yml"
                spec_path.write_text(yaml.safe_dump(degraded, sort_keys=False), encoding="utf-8")
                (run_dir / "ground_truth.json").write_text(
                    json.dumps({"n": n, "seed": seed, "removidos": removed}, indent=2, ensure_ascii=False),
                    encoding="utf-8")

                rep = scan(url, str(spec_path), DEFAULT_WORDLISTS, headers, args.concurrency,
                           args.template_policy, "1", ("GET", "POST", "PUT", "PATCH", "DELETE"),
                           auth_refresh=refresh)
                diff = rep.pop("_diff")
                rep["metricas_brutas"] = evaluate(diff.shadow, removed)
                rep["metricas"] = m = evaluate(diff.shadow, removed, intr)
                (run_dir / "resultado.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False),
                                                        encoding="utf-8")
                tipos = m["revocacao_por_tipo"]
                row = {
                    "alvo": args.alvo, "n": n, "seed": seed, "auth": auth,
                    "vp": m["vp"], "fp": m["fp"], "fn": m["fn"],
                    "precisao": m["precisao"], "revocacao": m["revocacao"], "f1": m["f1"],
                    "fp_bruto": rep["metricas_brutas"]["fp"], "precisao_bruta": rep["metricas_brutas"]["precisao"],
                    "gt_caminho": tipos.get("caminho", {}).get("total", 0),
                    "vp_caminho": tipos.get("caminho", {}).get("encontrados", 0),
                    "gt_metodo": tipos.get("metodo", {}).get("total", 0),
                    "vp_metodo": tipos.get("metodo", {}).get("encontrados", 0),
                    "zombies": len(rep["zombie"]),
                    "requisicoes": rep["execucao"]["requisicoes"], "erros": rep["execucao"]["erros"],
                    "renovacoes_auth": rep["execucao"].get("renovacoes_auth", 0),
                    "segundos": rep["execucao"]["segundos"],
                    "fn_lista": "; ".join(m["lista_fn"]), "fp_lista": "; ".join(m["lista_fp"]),
                }
                rows.append(row)
                print(f"   P={m['precisao']} R={m['revocacao']} F1={m['f1']} FN={m['lista_fn']} FP={m['lista_fp']}",
                      flush=True)
                with open(out / "resultados.csv", "w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0]))
                    w.writeheader()
                    w.writerows(rows)
    print(f"CSV: {out / 'resultados.csv'}")


if __name__ == "__main__":
    main()
