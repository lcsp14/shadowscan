"""Comparação de respostas HTTP — base da detecção de soft 404.

Problema: muitas APIs devolvem 200 (ou 401, 500...) com corpo de erro para
caminhos que não existem. Logo, "status != 404" NÃO significa "existe".

Estratégia adotada: comparar a resposta de um candidato com respostas de
REFERÊNCIA (baselines) obtidas pedindo caminhos aleatórios que certamente
não existem. Se o candidato "se parece" com um baseline, é tratado como
inexistente.

"Se parece" = mesmo status E corpo com similaridade textual >= LIMIAR,
depois de remover do corpo o próprio caminho pedido (muitas APIs ecoam o
caminho na mensagem de erro: "Rota /xyz não encontrada" — sem essa remoção,
cada resposta teria texto diferente).

Alternativas descartadas (ver docs/decisoes.md, D5):
- só status code: falha em soft 404, gera ruído massivo;
- igualdade exata de corpo: falha quando o erro ecoa o caminho ou tem timestamp;
- só tamanho do corpo: frágil; dois corpos diferentes podem ter o mesmo tamanho;
- só estrutura do JSON (conjunto de chaves): `{"message": "..."}` de sucesso e de
  erro teriam a mesma estrutura -> falso negativo.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

# Limiar de similaridade (0..1). Acima disso, duas respostas são "iguais".
SIMILARITY_THRESHOLD = 0.90
# Só os primeiros N caracteres entram na comparação (páginas de erro HTML
# podem ter dezenas de KB e o difflib é custoso). O início do corpo já
# carrega a mensagem/estrutura que diferencia as respostas.
MAX_COMPARE_CHARS = 4000

_HEX_OR_DIGITS = re.compile(r"\b(?:[0-9a-f]{8,}|\d{4,})\b", re.IGNORECASE)


@dataclass
class Resp:
    """Resumo de uma resposta HTTP (o que precisamos guardar dela)."""

    method: str
    path: str
    status: int
    content_type: str
    body: str

    @property
    def length(self) -> int:
        return len(self.body)


def normalize_body(body: str, paths: str | list[str]) -> str:
    """Remove do corpo o que varia entre requisições mas não indica rota distinta.

    `paths`: caminhos cujo eco deve ser neutralizado. Em `similarity`, recebe os caminhos
    das DUAS respostas comparadas, e a mesma normalização é aplicada aos dois corpos (D20).
    Normalizar cada corpo só com o próprio caminho falha quando o segmento pedido coincide
    com uma palavra do corpo de erro: `/users/v1/message` transformava a chave JSON
    "message" em "{SEG}" só no candidato, e a resposta passava por "diferente" do baseline
    (diário E27).
    """
    if isinstance(paths, str):
        paths = [paths]
    text = body[: MAX_COMPARE_CHARS * 2]
    # 1) eco dos caminhos e dos seus últimos segmentos (caminhos mais longos primeiro)
    for p in sorted(set(paths), key=len, reverse=True):
        text = text.replace(p, "{PATH}")
    for p in paths:
        last = p.rstrip("/").rsplit("/", 1)[-1]
        if len(last) >= 3:
            text = text.replace(last, "{SEG}")
    # 2) ids, timestamps, hashes (números longos e hex longos)
    text = _HEX_OR_DIGITS.sub("{N}", text)
    return text[:MAX_COMPARE_CHARS]


def similarity(a: Resp, b: Resp) -> float:
    # Normalização simétrica (D20): os segmentos de AMBOS os caminhos saem de AMBOS os corpos.
    both = [a.path, b.path]
    ta, tb = normalize_body(a.body, both), normalize_body(b.body, both)
    if ta == tb:
        return 1.0
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    # quick_ratio é um limite superior barato; se já está abaixo, nem calcula o ratio.
    if sm.quick_ratio() < SIMILARITY_THRESHOLD:
        return sm.quick_ratio()
    return sm.ratio()


def same_response(a: Resp, b: Resp) -> bool:
    """True se `a` e `b` são, para fins de existência, a mesma resposta."""
    return a.status == b.status and similarity(a, b) >= SIMILARITY_THRESHOLD
