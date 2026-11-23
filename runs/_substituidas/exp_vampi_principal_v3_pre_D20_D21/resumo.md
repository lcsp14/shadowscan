## Tabela 1 — Fim-a-fim: bruta × ajustada (D9)

Bruta = sem excluir shadows intrínsecos. Ajustada = intrínsecos verificados excluídos do FP.

| Auth | N | Exec. | Precisão bruta | Precisão ajustada | F1 bruto | F1 ajustado | Revocação | FP bruto (soma) | FP ajustado (soma) |
|---|---|---|---|---|---|---|---|---|---|
| nao | 3 | 4 | 0.29 ± 0.05 | 1.00 ± 0.00 | 0.43 ± 0.08 | 0.90 ± 0.12 | 0.83 ± 0.19 | 24 | 0 |

## Tabela 2 — Decomposição da revocação (D17)

Revocação fim-a-fim = descoberta × diferencial. Somas sobre todas as execuções do grupo.

| Auth | N | Exec. | Removidos descobertos (descoberta) | Descobertos classificados shadow (diferencial) | Revocação fim-a-fim |
|---|---|---|---|---|---|
| nao | 3 | 4 | 10/12 (0.83) | 10/10 (1.00) | 10/12 (0.83) |

## Tabela 3 — Por caminho único × por (método, caminho)

| Auth | N | Exec. | Precisão (endpoint) | Precisão (caminho) | Revocação (endpoint) | Revocação (caminho) | F1 (endpoint) | F1 (caminho) |
|---|---|---|---|---|---|---|---|---|
| nao | 3 | 4 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.83 ± 0.19 | 0.83 ± 0.19 | 0.90 ± 0.12 | 0.90 ± 0.12 |

## Tabela 4 — Revocação por tipo de remoção e custo

| Auth | N | Exec. | Rev. tipo caminho | Rev. tipo método | Requisições | Erros (soma) | Tempo (s) |
|---|---|---|---|---|---|---|---|
| nao | 3 | 4 | 8/10 (0.80) | 2/2 (1.00) | 39724.75 ± 7600.53 | 0 | 235.36 ± 45.65 |

## FN por causa (endpoint: nº de execuções)

**Não descobertos (limite da descoberta/wordlist)**

- `GET /createdb`: 1
- `PUT /users/v1/{}/password`: 1

**Descobertos mas não classificados como shadow (limite do diferencial)**

- nenhum

## Falsos positivos ajustados

- nenhum