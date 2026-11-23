"""Gerador de ground truth por degradação de especificação (seção 5 do briefing).

Ideia: partindo de uma spec COMPLETA, removemos N operações escolhidas
aleatoriamente (com semente fixa, para ser reprodutível). As operações removidas
continuam existindo na API real, mas não estão mais na spec degradada —
ou seja, são shadow endpoints CONHECIDOS. Rodando a ferramenta contra a spec
degradada, sabemos exatamente o que ela deveria encontrar e podemos calcular
precisão, revocação e F1.

Cada remoção é registrada com um "tipo":
- "caminho": o caminho inteiro sumiu da spec (nenhum método sobrou nele);
- "metodo":  o caminho continua na spec com outros métodos, só este método sumiu.
Os dois casos exigem estratégias de descoberta diferentes (wordlist vs. variação
de método), então vale medir o desempenho separadamente.

Uso:
    python -m shadowscan.ground_truth specs/vampi_openapi3.yml -n 4 --seed 1 -o runs/vampi_n4_s1
"""

from __future__ import annotations

import argparse
import copy
import json
import random
from pathlib import Path

import yaml

from shadowscan.spec_parser import HTTP_METHODS, Endpoint, base_path, load_spec, normalize_path


def list_operations(spec: dict) -> list[tuple[str, str]]:
    """Lista (caminho cru da spec, método minúsculo) — a forma usada para apagar do dict."""
    ops = []
    for raw_path, item in (spec.get("paths") or {}).items():
        for key in item or {}:
            if key.lower() in HTTP_METHODS:
                ops.append((raw_path, key))
    return sorted(ops)


def degrade(spec: dict, n: int, seed: int, exclude: set[str] | None = None) -> tuple[dict, list[dict]]:
    """Remove n operações da spec. Devolve (spec degradada, lista de removidos).

    `exclude`: caminhos que nunca devem ser removidos (ex.: "/" se a raiz
    for usada como referência). A spec original não é modificada.
    """
    exclude = exclude or set()
    candidates = [op for op in list_operations(spec) if op[0] not in exclude]
    if n > len(candidates):
        raise ValueError(f"n={n} maior que o número de operações candidatas ({len(candidates)})")

    rng = random.Random(seed)
    chosen = rng.sample(candidates, n)

    degraded = copy.deepcopy(spec)
    prefix = base_path(spec)
    removed = []
    for raw_path, method in chosen:
        del degraded["paths"][raw_path][method]
        removed.append({"method": method.upper(), "path": normalize_path(prefix + raw_path)})

    # Classifica o tipo DEPOIS de todas as remoções: se dois métodos do mesmo
    # caminho foram sorteados, o caminho pode ter sumido por completo.
    for raw_path in {p for p, _ in chosen}:
        remaining = [k for k in degraded["paths"][raw_path] if k.lower() in HTTP_METHODS]
        kind = "metodo" if remaining else "caminho"
        full = normalize_path(prefix + raw_path)
        for r in removed:
            if r["path"] == full:
                r["tipo"] = kind
        if not remaining:
            del degraded["paths"][raw_path]

    removed.sort(key=lambda r: (r["path"], r["method"]))
    return degraded, removed


def removed_as_endpoints(removed: list[dict]) -> set[Endpoint]:
    return {Endpoint(r["method"], r["path"]) for r in removed}


def main() -> None:
    ap = argparse.ArgumentParser(description="Gera spec degradada + ground truth de shadow endpoints")
    ap.add_argument("spec", help="spec OpenAPI completa (JSON ou YAML)")
    ap.add_argument("-n", type=int, required=True, help="número de operações a remover")
    ap.add_argument("--seed", type=int, default=0, help="semente do sorteio (reprodutibilidade)")
    ap.add_argument("--exclude", nargs="*", default=[], help="caminhos que não podem ser removidos")
    ap.add_argument("-o", "--out", required=True, help="diretório de saída")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    degraded, removed = degrade(spec, args.n, args.seed, set(args.exclude))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "spec_degradada.yml").write_text(
        yaml.safe_dump(degraded, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    meta = {
        "spec_original": str(args.spec),
        "n": args.n,
        "seed": args.seed,
        "exclude": args.exclude,
        "removidos": removed,
    }
    (out / "ground_truth.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Removidos ({len(removed)}):")
    for r in removed:
        print(f"  {r['method']:7} {r['path']}  [{r['tipo']}]")
    print(f"Saída em {out}/")


if __name__ == "__main__":
    main()
