## Tabela 1 — Fim-a-fim: bruta × ajustada (D9)

Bruta = sem excluir shadows intrínsecos. Ajustada = intrínsecos verificados excluídos do FP.

| Auth | N | Exec. | Precisão bruta | Precisão ajustada | F1 bruto | F1 ajustado | Revocação | FP bruto (soma) | FP ajustado (soma) |
|---|---|---|---|---|---|---|---|---|---|
| nao | 3 | 5 | 0.28 ± 0.05 | 1.00 ± 0.00 | 0.42 ± 0.07 | 0.88 ± 0.11 | 0.80 ± 0.18 | 30 | 0 |
| nao | 6 | 5 | 0.38 ± 0.14 | 1.00 ± 0.00 | 0.48 ± 0.19 | 0.76 ± 0.27 | 0.67 ± 0.29 | 30 | 0 |
| sim | 3 | 5 | 0.28 ± 0.05 | 1.00 ± 0.00 | 0.42 ± 0.07 | 0.88 ± 0.11 | 0.80 ± 0.18 | 30 | 0 |
| sim | 6 | 5 | 0.38 ± 0.14 | 1.00 ± 0.00 | 0.48 ± 0.19 | 0.76 ± 0.27 | 0.67 ± 0.29 | 30 | 0 |

## Tabela 2 — Decomposição da revocação (D17)

Revocação fim-a-fim = descoberta × diferencial. Somas sobre todas as execuções do grupo.

| Auth | N | Exec. | Removidos descobertos (descoberta) | Descobertos classificados shadow (diferencial) | Revocação fim-a-fim |
|---|---|---|---|---|---|
| nao | 3 | 5 | 12/15 (0.80) | 12/12 (1.00) | 12/15 (0.80) |
| nao | 6 | 5 | 20/30 (0.67) | 20/20 (1.00) | 20/30 (0.67) |
| sim | 3 | 5 | 12/15 (0.80) | 12/12 (1.00) | 12/15 (0.80) |
| sim | 6 | 5 | 20/30 (0.67) | 20/20 (1.00) | 20/30 (0.67) |

## Tabela 3 — Por caminho único × por (método, caminho)

| Auth | N | Exec. | Precisão (endpoint) | Precisão (caminho) | Revocação (endpoint) | Revocação (caminho) | F1 (endpoint) | F1 (caminho) |
|---|---|---|---|---|---|---|---|---|
| nao | 3 | 5 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.80 ± 0.18 | 0.80 ± 0.18 | 0.88 ± 0.11 | 0.88 ± 0.11 |
| nao | 6 | 5 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.67 ± 0.29 | 0.65 ± 0.27 | 0.76 ± 0.27 | 0.76 ± 0.25 |
| sim | 3 | 5 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.80 ± 0.18 | 0.80 ± 0.18 | 0.88 ± 0.11 | 0.88 ± 0.11 |
| sim | 6 | 5 | 1.00 ± 0.00 | 1.00 ± 0.00 | 0.67 ± 0.29 | 0.65 ± 0.27 | 0.76 ± 0.27 | 0.76 ± 0.25 |

## Tabela 4 — Revocação por tipo de remoção e custo

| Auth | N | Exec. | Rev. tipo caminho | Rev. tipo método | Requisições | Erros (soma) | Tempo (s) |
|---|---|---|---|---|---|---|---|
| nao | 3 | 5 | 9/12 (0.75) | 3/3 (1.00) | 41016.80 ± 7211.96 | 0 | 245.59 ± 43.54 |
| nao | 6 | 5 | 16/26 (0.62) | 4/4 (1.00) | 39683.80 ± 9320.74 | 0 | 233.97 ± 55.37 |
| sim | 3 | 5 | 9/12 (0.75) | 3/3 (1.00) | 41014.20 ± 7209.58 | 0 | 249.93 ± 46.44 |
| sim | 6 | 5 | 16/26 (0.62) | 4/4 (1.00) | 39683.80 ± 9320.74 | 0 | 238.90 ± 55.98 |

## FN por causa (endpoint: nº de execuções)

**Não descobertos (limite da descoberta/wordlist)**

- `GET /createdb`: 10
- `GET /users/v1/_debug`: 6
- `PUT /users/v1/{}/password`: 4
- `GET /books/v1`: 2
- `GET /books/v1/{}`: 2
- `POST /books/v1`: 2

**Descobertos mas não classificados como shadow (limite do diferencial)**

- nenhum

## Falsos positivos ajustados

- nenhum