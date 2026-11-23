## Tabela 1 — Fim-a-fim: bruta × ajustada (D9)

Bruta = sem excluir shadows intrínsecos. Ajustada = intrínsecos verificados excluídos do FP.

| Auth | N | Exec. | Precisão bruta | Precisão ajustada | F1 bruto | F1 ajustado | Revocação | FP bruto (soma) | FP ajustado (soma) |
|---|---|---|---|---|---|---|---|---|---|
| nao | 3 | 5 | 0.28 ± 0.03 | 1.00 ± 0.00 | 0.44 ± 0.06 | 0.96 ± 0.09 | 0.93 ± 0.15 | 35 | 0 |
| nao | 6 | 5 | 0.33 ± 0.03 | 1.00 ± 0.00 | 0.41 ± 0.05 | 0.72 ± 0.07 | 0.57 ± 0.09 | 35 | 0 |

## Tabela 2 — Decomposição da revocação (D17)

Revocação fim-a-fim = descoberta × diferencial. Somas sobre todas as execuções do grupo.

| Auth | N | Exec. | Removidos descobertos (descoberta) | Descobertos classificados shadow (diferencial) | Revocação fim-a-fim |
|---|---|---|---|---|---|
| nao | 3 | 5 | 14/15 (0.93) | 14/14 (1.00) | 14/15 (0.93) |
| nao | 6 | 5 | 17/30 (0.57) | 17/17 (1.00) | 17/30 (0.57) |

## Tabela 3 — Por caminho único × por (método, caminho)

| Auth | N | Exec. | Precisão (endpoint) | Precisão (caminho) | Revocação (endpoint) | Revocação (caminho) | F1 (endpoint) | F1 (caminho) |
|---|---|---|---|---|---|---|---|---|
| nao | 3 | 5 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.93 ± 0.15 | 0.93 ± 0.15 | 0.96 ± 0.09 | 0.96 ± 0.09 |
| nao | 6 | 5 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.57 ± 0.09 | 0.57 ± 0.09 | 0.72 ± 0.07 | 0.72 ± 0.07 |

## Tabela 4 — Revocação por tipo de remoção e custo

| Auth | N | Exec. | Rev. tipo caminho | Rev. tipo método | Requisições | Erros (soma) | Tempo (s) |
|---|---|---|---|---|---|---|---|
| nao | 3 | 5 | 12/13 (0.92) | 2/2 (1.00) | 188753.40 ± 5895.62 | 39 | 3202.51 ± 916.55 |
| nao | 6 | 5 | 14/27 (0.52) | 3/3 (1.00) | 172917.40 ± 10822.33 | 0 | 2039.96 ± 126.31 |

## FN por causa (endpoint: nº de execuções)

**Não descobertos (limite da descoberta/wordlist)**

- `GET /vapi/api10/user/flag`: 4
- `GET /vapi/user`: 3
- `GET /vapi/dashboard/flag`: 2
- `POST /vapi/api4/otp/verify`: 2
- `GET /vapi/api8/user/secret`: 1
- `GET /vapi/serversurfer`: 1
- `POST /vapi/api8/user/login`: 1

**Descobertos mas não classificados como shadow (limite do diferencial)**

- nenhum

## Falsos positivos ajustados

- nenhum