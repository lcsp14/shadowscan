# Ambiente experimental

Registro exato do hardware, software e artefatos usados nos experimentos. Coletado em
17/11/2026, durante a bateria principal do VAmPI.

---

## 1. Máquina hospedeira

| Item | Valor |
|---|---|
| Sistema operacional | Microsoft Windows 11 Home Single Language, versão 10.0.26200, 64 bits |
| Processador | AMD Ryzen 7 7435HS — 8 núcleos físicos, 16 lógicos |
| Memória RAM | 31,7 GB |
| Docker | Engine 29.5.3 (cliente e servidor), Docker Desktop |
| Rede | Todo o tráfego em `127.0.0.1` (loopback). Nenhum alvo externo. |

**Observação de validade.** A máquina não era dedicada. Outros containers do autor rodavam
em paralelo (cinco containers sem relação com o experimento), sem tráfego gerado pelos experimentos. Isso pode afetar a métrica de
**tempo** de execução, mas não as métricas de acerto (precisão, revocação e F1), que não
dependem de temporização. Ver ameaça à validade A4 (Apêndice B).

---

## 2. Ferramenta (shadowscan)

| Item | Valor |
|---|---|
| Linguagem | Python 3.14.4 (ambiente virtual `.venv`) |
| Dependências diretas | `httpx==0.28.1`, `PyYAML==6.0.3`, `rich==15.0.0` |
| Dependências transitivas | anyio 4.16.0, certifi 2026.10.23, h11 0.16.0, httpcore 1.0.9, idna 3.20, markdown-it-py 4.3.0, mdurl 0.1.2, Pygments 2.21.0, typing_extensions 4.16.0 |
| Biblioteca padrão usada nos pontos críticos | `difflib.SequenceMatcher` (similaridade, D5), `random.Random` (sorteio do ground truth, D4), `asyncio` (concorrência) |

### 2.1 Hash dos arquivos que geraram os resultados (SHA-256, primeiros 16 hex)

Hashes da versão **final** do código, usada na bateria definitiva do VAmPI (diário E27, após
D18–D21). Versões anteriores e o motivo da substituição estão no diário (E18, E22, E27).

| Arquivo | SHA-256 (prefixo) |
|---|---|
| shadowscan/spec_parser.py | 760C1CBADE25D4D8 |
| shadowscan/responses.py | **1D29044E33F9F79E** |
| shadowscan/discovery.py | **78577DF56E68F215** |
| shadowscan/diff.py | **2327A3AC4EF6637C** |
| shadowscan/classify.py | D4FF0E35972E59DB |
| shadowscan/metrics.py | BE242347BCC18C79 |
| shadowscan/ground_truth.py | FB2CF49B5D7EFF63 |
| shadowscan/\_\_main\_\_.py | **E1236C2BE3210D09** |
| experiments/run_experiments.py | 75E8D7EEC1D091EB ¹ |
| experiments/analyze.py | 3CA868A46A551B75 ² |
| experiments/laravel_routes_to_openapi.py | CFB03B3FEF4FD847 |
| tests/test_core.py | 19 testes (após D21) |

¹ `run_experiments.py` ganhou o alvo `vapi` durante a bateria do VAmPI. A mudança só
acrescenta uma entrada de configuração e a regra "vAPI sem autenticação". Não altera nenhum
caminho de código executado para o VAmPI.

² `analyze.py` só lê resultados já gravados. Mudanças nele não afetam dados coletados.

### 2.2 Parâmetros padrão da ferramenta nos experimentos

| Parâmetro | Valor | Decisão |
|---|---|---|
| Limiar de similaridade | 0,90 | D5 |
| Caracteres comparados por corpo | 4000 | D5 |
| Baselines globais por método | 3 de 1 segmento + 3 de 2 segmentos | D5 |
| Baselines por pai e método | 2 | D6 |
| Métodos da fase A | GET, POST | D10 |
| Métodos da fase B | GET, POST, PUT, PATCH, DELETE | D11 |
| Valor de instanciação de `{param}` | `"1"` | D7 |
| Política para casos ambíguos | `declarado` | D8 |
| Concorrência máxima | 10 requisições simultâneas | — |
| Timeout por requisição | 10 s | — |
| Corpo de POST, PUT e PATCH | `{}` (JSON) | D13 |
| Seguir redirecionamentos | não | D13 |

---

## 3. Wordlists

| Arquivo | Origem | Linhas | SHA-256 (prefixo) |
|---|---|---|---|
| wordlists/seclists_objects.txt | SecLists, `Discovery/Web-Content/api/objects.txt`, branch `master`, baixado em 17/11/2026 | 3133 | FA11D0D745E27875 |
| wordlists/seclists_actions.txt | SecLists, `Discovery/Web-Content/api/actions.txt`, branch `master`, baixado em 17/11/2026 | 224 | 2F1954945FA0E2A2 |
| wordlists/seclists_api-endpoints.txt | SecLists, `Discovery/Web-Content/api/api-endpoints.txt` (baixado, **não usado** na configuração padrão) | 295 | 7860E451BEC345A0 |

Wordlist efetiva (objects ∪ actions, após o filtro de `load_wordlist`) = **3291 palavras únicas**.
O filtro descarta linhas vazias, comentários (`#`), entradas com `%` (ex.: `lost%2Bfound`)
e a entrada `@`.

Fonte: https://github.com/danielmiessler/SecLists. **Commit identificado a posteriori (18/11/2026, diário E40):** `6b19c2f5088c45b5dadb4d8918d2ab4f7efb03a9` (master de 17/11/2026, 11:10 UTC). Os SHA-256 de `objects.txt` e `actions.txt` nesse commit coincidem com os da tabela acima. Como o download foi feito da branch
`master`, os hashes acima fixam o conteúdo exato que foi usado.

---

## 4. Alvo 1 — VAmPI

| Item | Valor |
|---|---|
| Imagem | `erev0s/vampi@sha256:0a5a224b6e14ae7da6a6ea265178ff71286ff903aec74adee98f660bb0e4ca12` |
| Data de criação da imagem | 2026-04-07 |
| Container | `vampi`, porta 5000 → 5000 |
| Runtime interno | Python 3.11.15 |
| Frameworks | Flask 2.2.2, connexion 2.14.2, Werkzeug 2.2.3, SQLAlchemy 2.0.2, Flask-SQLAlchemy 3.0.3 |
| Banco | SQLite (interno ao container), populado por `GET /createdb` |
| Spec usada | `specs/vampi_openapi3.yml`, copiada do container (`/vampi/openapi_specs/openapi3.yml`). OpenAPI 3.0.1. 14 operações em 12 caminhos. SHA-256 35200F354F9C9968 |
| Spec servida em runtime | `specs/vampi_openapi.json`, obtida em `GET /openapi.json`. Mesmas 14 operações. SHA-256 76B07B181769482B |
| Natureza da spec | **escrita à mão** pelos autores do VAmPI. Não é derivada do código, e o experimento N=0 mostrou que está incompleta (ver diário, E07). |

---

## 5. Alvo 2 — vAPI

| Item | Valor |
|---|---|
| Código | https://github.com/roottusk/vapi, commit `67152695b0acf13dd424905729080fbc80d5a593` (09/01/2025, "Merge pull request #48 from SamuraiWTF/master"), clonado com `--depth 1` em `envs/vapi` |
| Imagem da aplicação | `vapi-www:latest`, construída localmente a partir do `Dockerfile` do repositório. Id `sha256:4b5adcd7…a2ee8f739ff`, criada em 17/11/2026 |
| Runtime | PHP 7.4.33, Laravel Framework 8.57.0, servidor `php artisan serve` |
| Banco | `mysql@sha256:7dcddc01f13bab2f15cde676d44d01f61fc9f99fe7785e86196dfc07d358ae2b` (MySQL Community 8.0.46) |
| Auxiliar | `phpmyadmin/phpmyadmin@sha256:16d0f09c…3d0c6d9b` (porta 8001, não usado nos experimentos) |
| Portas | 8000 → 80 (aplicação). A 3306 **não é publicada** (ver abaixo). |
| Alterações locais (só infraestrutura; nenhuma no código da aplicação) | `envs/vapi/docker-compose.override.yml`: (1) **3306 não publicada** — conflitava com outro container do autor, sem relação com o experimento; a aplicação acessa o banco pela rede interna (E16). (2) **Montagem `./vapi:/var/www/html/vapi` removida** — a montagem do disco do Windows no Docker Desktop deixava cada requisição em ~2,2 s, com atendimento serial; passa a valer a cópia idêntica do código já presente na imagem (`COPY ./vapi`) (E30). (3) **`artisan config:clear` na inicialização** — sem a montagem, valeria o cache de configuração gerado no build sem variáveis de ambiente (banco em `127.0.0.1`); com o clear, o Laravel lê as variáveis do compose, como antes. (4) **`PHP_CLI_SERVER_WORKERS=10`** — o servidor embutido do PHP 7.4 atende até 10 requisições em paralelo. **Equivalência verificada** (E30): mesmos status e tamanhos de corpo da sondagem E16 e escrita no banco funcionando. Latência: 2,2 s → 0,065 s. |
| Spec usada | `specs/vapi_openapi3.yml`, **gerada** de `vapi/routes/api.php` por `experiments/laravel_routes_to_openapi.py`. Prefixo `/vapi`. 33 operações em 29 caminhos. SHA-256 D39BA94756E2E071 |
| Natureza da spec | **derivada do roteador** do framework: coincide, por construção, com as rotas declaradas em `routes/api.php` (D16). Não cobre rotas registradas por outros meios nem o restante da superfície da aplicação (rotas web, arquivos estáticos). |
