# Diário de pesquisa

Registro cronológico e técnico de tudo o que foi feito no projeto: ações, motivos,
resultados, problemas encontrados e como foram resolvidos. Cada entrada tem um
identificador (E01, E02…) para ser citada nos outros documentos e no artigo.

Convenções:
- Horários no fuso local (UTC−3). Quando o horário veio do timestamp de um arquivo, isso é indicado.
- "Evidência" aponta o arquivo em `runs/` ou `docs/` que comprova a entrada.
- Decisões numeradas (D1…D17) estão em `decisoes.md`; ameaças à validade (A1…A9), em `protocolo_experimental.md`.

---

## 17/11/2026 (terça-feira)

### E01 — 09:30 · Início: briefing e preparação do repositório
- **Ação.** Leitura do briefing inicial (`docs/briefing_inicial.md`, depois substituído por
  `CLAUDE.md`, ver E15). O diretório `C:\dev\TCC` estava vazio.
- **Ambiente.** Python 3.14.4 e Docker 29.5.3 disponíveis. Criação de `.venv` com `httpx`,
  `PyYAML` e `rich` (as três dependências sugeridas no briefing §11, sem acréscimos).

### E02 — ~09:32 · VAmPI no ar e obtenção da spec
- **Ação.** `docker run -d --name vampi -p 5000:5000 erev0s/vampi:latest`. A imagem resolvida
  tem o digest `sha256:0a5a224b…e4ca12` (ver `ambiente_experimental.md` §4).
- A spec foi obtida de duas formas: em runtime (`GET /openapi.json` → `specs/vampi_openapi.json`)
  e do arquivo-fonte no container (`docker cp vampi:/vampi/openapi_specs/openapi3.yml`).
- **Resultado.** OpenAPI 3.0.1, `servers: [{url: ''}]` (sem prefixo), **14 operações em 12 caminhos**:
  `GET /`, `GET|POST /books/v1`, `GET /books/v1/{book_title}`, `GET /createdb`, `GET /me`,
  `GET /users/v1`, `GET /users/v1/_debug`, `POST /users/v1/login`, `POST /users/v1/register`,
  `GET|DELETE /users/v1/{username}`, `PUT /users/v1/{username}/email`,
  `PUT /users/v1/{username}/password`.
- **Observação.** A própria spec declara uma rota de debug (`/users/v1/_debug`). Ela não é
  shadow na spec original, mas pode virar ground truth quando sorteada.

### E03 — 09:33 · Módulo [1] parser e gerador de ground truth
- **Arquivos.** `shadowscan/spec_parser.py`, `shadowscan/ground_truth.py`.
- **Parser.** Lê JSON/YAML e percorre `paths`. Considera métodos só as chaves de `HTTP_METHODS`
  (`get put post delete options head patch trace`). Chaves como `parameters` e `summary` são
  ignoradas. O caminho fica **em forma de template** (D2). Normalização: barra inicial
  garantida, barra final removida, prefixo de `servers[0].url` somado (D3).
- **Ground truth.** `random.Random(seed).sample` sobre as operações ordenadas. A remoção é por
  operação, e o tipo (`caminho`/`metodo`) é decidido **depois** de todas as remoções (D4).
- **Verificação.** Parser no VAmPI = 14 endpoints. `ground_truth -n 4 --seed 1` removeu
  `GET /books/v1`, `POST /books/v1`, `GET /createdb`, `POST /users/v1/register`. A diferença
  entre os conjuntos parseados da spec original e da degradada foi **idêntica** à lista
  registrada.
- **Evidência.** `runs/vampi_n4_s1/ground_truth.json`, `spec_degradada.yml`.

### E04 — ~09:34 · Sondagem manual do comportamento do VAmPI
Antes de projetar a detecção de soft 404, o comportamento real do alvo foi medido com
`curl` (o banco ainda **não** estava populado):

| Requisição | Status | Corpo / observação |
|---|---|---|
| `GET /naoexiste123` | 404 | `application/problem+json`, "The requested URL was not found…" (205 B) |
| `GET /users/v1/naoexiste_zz` | 500 | Página HTML de erro do Werkzeug, `sqlite3.OperationalError: no such table: users` (44 KB) |
| `GET /books/v1/xyzabc` | 401 | "No authorization token provided" — a autenticação é checada **antes** da lógica |
| `GET /users/v1/_debug` | 500 | Mesmo erro de tabela inexistente (47 KB) |
| `GET /createdb` | 200 | `{"message": "Database populated."}` — **esta requisição populou o banco** |
| `GET /me` | 401 | igual ao `/books/v1/xyzabc` |
| `GET /users/v2`, `GET /api/v1` | 404 | 404 do framework |
| `POST\|PUT\|DELETE\|PATCH /users/v1` | 405 | "The method is not allowed…" (142 B) |
| `OPTIONS /users/v1` | 200 | corpo vazio, gerado automaticamente pelo Flask |

Conclusões que guiaram o projeto:
1. O VAmPI usa 404 e 405 "honestos" no nível do framework. Mas existem respostas 401 e 500
   que **não dizem nada** sobre a existência da rota. Classificar só por status geraria ruído.
2. Existe 404 **de aplicação** (usuário não encontrado), diferente do 404 do framework. Esse
   404 de aplicação prova que a rota existe. Daí a distinção literal × template (D6).
3. OPTIONS responde 200 para qualquer rota existente → OPTIONS fora dos métodos padrão (D11).
4. `GET /createdb` altera estado → reset do banco antes de cada execução da bateria (D15).

### E05 — 09:36–09:47 · Módulos [2], [3] e [4]
- **`responses.py` (soft 404, D5).** Comparação = status igual **e** similaridade ≥ 0,90
  (`difflib.SequenceMatcher.ratio`) depois de normalizar o corpo (eco do caminho → `{PATH}`,
  último segmento → `{SEG}`, números ≥ 4 dígitos e hex ≥ 8 → `{N}`), truncando em 4000
  caracteres. `quick_ratio()` serve de atalho barato (é um limite superior do `ratio`).
- **`discovery.py`.** Baselines globais (3 + 3 por método), fase A (caminhos vivos),
  fase B (métodos), fase C (rota-coringa, D12). Concorrência via `asyncio.Semaphore(10)`.
- **`diff.py` (D8).** Precedência: literal exato e depois template. O nome do parâmetro é
  ignorado (`canonical()` troca `{x}` por `{}`). Casos ambíguos são guardados à parte.
- **`classify.py`.** Quatro categorias do briefing, por segmento inteiro, sem distinguir
  maiúsculas e ignorando `_ - .` nas pontas.
- **`metrics.py`.** P, R e F1, revocação por tipo de remoção, listas nominais de VP, FP e FN.
- **`__main__.py`.** CLI com saída em tabela (`rich`) e JSON.

### E06 — 09:37–09:40 · Download da wordlist
- SecLists `Discovery/Web-Content/api/`: `objects.txt` (3133 linhas), `actions.txt` (224),
  `api-endpoints.txt` (295, não usada).
- **Verificação de presença** (feita **antes** de qualquer execução, para documentar que a
  wordlist não foi ajustada ao alvo):

  | Palavra | objects | actions |
  |---|---|---|
  | login | ✓ | |
  | register | ✓ | ✓ |
  | debug | ✓ | |
  | me | ✓ | |
  | admin, test | ✓ | ✓ |
  | `_debug`, `createdb`, `actuator` | ✗ | ✗ |

- **Decisão (D14).** A configuração padrão é objects ∪ actions, **sem edição**. Ficou
  previsto de antemão que `createdb` e `_debug` gerariam FN de descoberta se sorteados.

### E07 — 09:40 · Primeira execução com a spec completa (sanidade, fase A só com GET)
- **Comando.** `python -m shadowscan --url http://127.0.0.1:5000 --spec specs/vampi_openapi3.yml`
- **Resultado.** 23 289 requisições, 17 caminhos vivos, 140,45 s. **Zero zombies** (todo
  endpoint declarado foi visto respondendo). **6 shadows**:
  `GET|POST|PUT|PATCH|DELETE /console` (200) e `GET /ui` (308).
- **Verificação manual:**
  - `GET /console` → HTML com `<title>Console // Werkzeug Debugger</title>` e
    `CONSOLE_MODE = true`. É o **console interativo do Werkzeug**, exposto porque a aplicação
    roda com o modo debug ativo. Esse console permite executar código Python arbitrário no
    processo do servidor (o acesso é condicionado a um PIN, que não foi testado por estar fora
    do escopo). `DELETE /console` também → 200: o middleware do debugger ignora o método.
  - `GET /ui` → `308 PERMANENT REDIRECT` para `/ui/`. É o Swagger UI servido
    automaticamente pelo connexion. Header `Server: Werkzeug/2.2.3 Python/3.11.15`.
- **Interpretação.** Os dois são **shadow endpoints reais**: respondem na API e não estão na
  spec oficial. `/console` é um caso típico da categoria API9:2023 (rota de debug esquecida
  em produção) e é o **achado principal** do trabalho (QP4).
- **Consequência metodológica.** Esses endpoints apareceriam como FP em toda execução
  degradada. Daí o procedimento de shadows intrínsecos (D9), registrados em
  `specs/vampi_intrinsecos.json` às 09:43.
- **Evidência.** `runs/vampi_completa.json`.

### E08 — ~09:45 · Primeira execução degradada e descoberta de um defeito de projeto
- **Comando.** Spec de `runs/vampi_n4_s1` com ground truth. Ainda sem exclusão de intrínsecos.
- **Resultado.** P = 0,25, R = 0,50, F1 = 0,33. VP: `GET|POST /books/v1`.
  FN: `GET /createdb`, `POST /users/v1/register`. FP: os 6 intrínsecos.
- **Análise do FN `POST /users/v1/register`.** `register` **está** na wordlist. Rastreando a
  execução: o candidato `/users/v1/register` foi testado na fase A só com GET.
  `GET /users/v1/register` cai na rota `GET /users/v1/{username}` e responde "usuário não
  encontrado", **igual** ao baseline do pai (`/users/v1/<aleatório>`). Por isso o caminho foi
  considerado morto e nunca chegou à fase B, onde o POST seria testado.
  **Um template de GET "escondia" uma rota literal de outro método.**
- **Correção (D10).** A fase A passou a sondar GET **e** POST. Além disso, um 405 só prova
  que o caminho existe se for diferente do 405 do pai (senão o 405 vem do template).
  Custo: requisições da fase A × 2.
- **Análise do FN `GET /createdb`.** A palavra não está na wordlist (E06). É FN de
  cobertura, esperado e não corrigido (corrigir seria ajustar a wordlist ao alvo).

### E09 — 09:47 · Reexecução após a correção D10
- **Resultado.** 46 302 requisições, 16 caminhos vivos, 201,21 s, 0 erros.
  Com exclusão de intrínsecos: **P = 1,00, R = 0,75, F1 = 0,86** (VP = 3, FP = 0, FN = 1).
  `POST /users/v1/register` agora é encontrado (status 400 com corpo `{}`, diferente do
  baseline). O único FN restante é `GET /createdb`.
- Contador de erros de rede adicionado ao relatório (`execucao.erros`): uma execução com
  muitos erros deve ser descartada, porque endpoints não sondados viram FN espúrios.
- **Evidência.** `runs/vampi_n4_s1/resultado.json`.

### E10 — 09:47–09:50 · Execução de verificação com a spec completa (ramo descontinuado da sessão)
- **O que é.** `runs/vampi_completa_noauth.json` (timestamp 09:50:59). Execução da ferramenta já
  corrigida (fase A com GET+POST, campo `erros` presente), com a spec completa e sem autenticação.
- **Origem (apurada em E20).** Gerada pelo próprio assistente às 09:47:42, na sessão original do
  Claude Code (`f2f7e58a-8709-40bb-9b95-234d02dd6c9f`), com o objetivo declarado de *"confirmar a
  lista de shadows intrínsecos com a fase A nova (GET+POST)"*. Comando: `GET /createdb`, criação
  do token (registro e login de `tcc_scanner`) e `python -m shadowscan --url http://127.0.0.1:5000
  --spec specs/vampi_openapi3.yml -o runs/vampi_completa_noauth.json`.
  Às 09:51:47 a sessão foi bifurcada e retomada (`--fork-session --resume`, nova sessão
  `780eea92-e53a-4c0f-8a7e-68b080c92823`) a partir de um ponto **anterior** a esse comando. Por
  isso o ramo que continuou o trabalho não tinha registro da execução e a tratou como de origem
  desconhecida. **Não houve intervenção externa** nos arquivos do projeto.
- **Resultado.** 46 317 requisições, 0 erros, 17 caminhos vivos, 194,51 s. Shadows: os mesmos
  6 intrínsecos. Zero zombies. **É consistente com E07 e E12.**
- **Efeito colateral no alvo.** Esse comando criou o usuário `tcc_scanner` no VAmPI antes da
  bateria. Sem impacto nos dados: o runner reseta o banco antes de cada execução (D15) e
  recria o usuário quando autentica.

### E11 — ~09:52 · Testes unitários e runner de experimentos
- `tests/test_core.py`: 12 testes de funções puras (parser, casamento por template, política
  para casos ambíguos, independência do nome do parâmetro, prefixos e versões, eco do
  caminho no soft 404, classificação, reprodutibilidade do ground truth, métricas com
  intrínsecos). **12/12 passando.**
- `experiments/run_experiments.py`: para cada combinação (N, semente, auth), reseta o banco,
  autentica se for o caso, gera S', executa e grava `resultado.json` e uma linha no CSV.
- **Autenticação no VAmPI.** O runner registra o usuário comum `tcc_scanner` e faz login
  (`POST /users/v1/login` → `auth_token`). Header: `Authorization: Bearer <token>`.
  Verificado: `GET /me` → 200 com o token.

### E12 — 09:52–10:05 · Bateria N=0 (levantamento de intrínsecos)
- **Sem auth** (09:52–09:56) e **com auth** (09:56–10:05): nos dois casos, **nenhum shadow além
  dos 6 intrínsecos** (FP ajustado = []).
- **Interpretação.** A autenticação com usuário comum não revelou rotas adicionais no VAmPI.
- **Evidência.** `runs/exp_vampi_n0/`.

### E13 — 10:05–10:24 · Bateria principal do VAmPI (interrompida em E18, dados invalidados)
- 20 execuções: N ∈ {3, 6} × semente ∈ {1..5} × auth ∈ {não, sim}, cerca de 3,5–5 min cada.
- **Parciais até a redação desta entrada:**

  | Execução | G (removidos) | P | R | F1 | FN |
  |---|---|---|---|---|---|
  | n3_s1_nao | — | 1,00 | 1,00 | 1,00 | — |
  | n3_s2_nao | `GET /` [caminho], `GET /books/v1` [metodo], `PUT /users/v1/{username}/password` [caminho] | 1,00 | 0,33 | 0,50 | `GET /`, `PUT …/password` |

- **Análise dos FN de n3_s2** (feita a partir de `observados` em `resultado.json`):
  1. **`GET /` — falha na geração de candidatos.** A raiz nunca entra no conjunto de
     candidatos. `build_candidates` gera os caminhos declarados (`/` saiu de S'), os
     prefixos literais próprios (que nunca incluem a raiz) e `base + "/" + palavra` (para a
     base vazia isso gera `/palavra`, nunca `/`). Logo, se `GET /` for removido da spec, ele
     **não pode** ser descoberto. Classificação: **FN de descoberta causado por defeito**.
  2. **`PUT /users/v1/{username}/password` — limite da estratégia.** A wordlist só é aplicada
     sob prefixos **literais** (`/users`, `/users/v1`). Sob um prefixo com parâmetro
     (`/users/v1/{username}/`) nenhuma palavra é testada, e a fase C só infere um `{param}`
     por nível sob prefixos literais. Mesmo que `password` esteja na wordlist, o caminho
     `/users/v1/1/password` nunca é gerado. Classificação: **FN de descoberta, limitação de
     projeto**.
- **Achado positivo na mesma execução.** Três observações foram marcadas como **ambíguas**
  (colidem com o template `GET /users/v1/{username}`): `/users/v1/admin`, `/users/v1/message`
  e `/users/v1/status`. Elas responderam de forma diferente do baseline de usuário
  inexistente. Pelo menos `admin` é um usuário real do banco do VAmPI, populado pelo
  `/createdb`. Com a política padrão `declarado` (D8), nenhuma virou shadow. Com a política
  `shadow`, seriam **3 FP**. É evidência empírica a favor da escolha conservadora da D8.
- **Fase C funcionando.** Foram inferidas as rotas-coringa `GET /books/v1/{param}` (401),
  `GET /users/v1/{param}` (404 de aplicação) e `DELETE /users/v1/{param}` (401). Todas
  casaram com templates declarados, então nenhum falso shadow.

### E14 — 09:53 · Spec do vAPI derivada do roteador (D16)
- O vAPI (commit `67152695`) **não publica OpenAPI**, só uma coleção Postman.
  O prefixo `/vapi` vem de `RouteServiceProvider` (`Route::prefix('vapi')`), confirmado pelas
  URLs da coleção Postman (`http://{{host}}/vapi/api1/user`).
- `experiments/laravel_routes_to_openapi.py` extrai as rotas com a regex
  `Route::(?:[a-z]+\([^)]*\)->)*(get|post|put|patch|delete)\(\s*'([^']+)'`, ignorando linhas
  comentadas.
- **Resultado.** 33 operações em 29 caminhos. **33 = número de declarações `Route::` em
  `routes/api.php`**, contadas de forma independente com `grep -c`. A spec inclui
  `POST /vapi/api9/v1/user/login` e `POST /vapi/api9/v2/user/login` (duas versões, útil para a
  categoria "versão obsoleta").

### E15 — 10:08 · Novo briefing (CLAUDE.md) e métrica do diferencial isolado
- O autor substituiu o briefing por uma versão de execução: congelamento de escopo e
  **DATA FREEZE em 20/11**. O briefing antigo foi arquivado em `docs/briefing_inicial.md`.
- **D17 implementada** só em `experiments/analyze.py`. O pipeline de medição não mudou.
  - Revocação da descoberta = |G ∩ O| / |G|.
  - Revocação do diferencial isolado = |G ∩ O ∩ R| / |G ∩ O|.
  - Os FN agora saem separados em "não descobertos" e "descobertos mas não classificados".
  - Tabelas bruta × ajustada sempre lado a lado (D9). Métricas por caminho único também.
- **Teste com E09.** Descoberta 3/4 (0,75), diferencial **3/3 (1,00)**, fim-a-fim 3/4 (0,75).
- Criado `docs/trabalhos_futuros.md`.

### E16 — 10:14 · vAPI no ar
- `docker compose up -d --build` falhou: `Bind for 0.0.0.0:3306 failed: port is already
  allocated`. A porta estava em uso por um container de outro projeto do autor.
- **Solução.** `envs/vapi/docker-compose.override.yml` com `ports: !reset []` no serviço `db`.
  A aplicação (`www`) acessa o MySQL pela rede interna do compose (`DB_HOST: db`), então
  publicar a porta no host era desnecessário. O comportamento da API não muda.
  Conferido com `docker compose config`: só 8000 e 8001 são publicadas.
- **Sondagem manual do vAPI:**

  | Requisição | Status | Corpo |
  |---|---|---|
  | `GET /vapi/zzab12`, `/vapi/api1/zzab12`, `/vapi/api1/user/zz/zz`, `/zzroot` | **500** | `{}` (2 B) |
  | `GET /vapi/api9/v1/user/login` (rota só POST) | **500** | `{}` |
  | `GET /vapi/api9/v3/user/login` (inexistente) | **500** | `{}` |
  | `POST /vapi/api9/v1/user/login` com `{}` | 200 | — |
  | `GET /vapi/api1/user/1` | 403 | `{"success":"false","cause":"authHeaderNotSet"}` |
  | `GET /vapi/serversurfer` | 403 | `{"success":"false","cause":"url param not set"}` |
  | `GET /vapi` | 200 | página HTML (1,1 MB) |
  | `GET /` | 200 | página HTML (9,3 KB) |

- **Interpretação:**
  1. No vAPI, **"não encontrado" = HTTP 500 com corpo `{}`**, sempre igual. É um soft 404
     clássico: classificar por status trataria o 500 como "existe, mas com erro" ou como
     erro de servidor, nunca como "não existe". A estratégia de baseline (D5) é necessária.
  2. **GET em rota só POST também → 500 `{}`**, e não 405. Ou seja, no vAPI uma rota POST-only
     sondada só com GET é indistinguível de uma rota inexistente. A correção D10 (fase A com
     GET+POST) é **necessária** para o vAPI, não só para o VAmPI.
  3. `/` e `/vapi` são rotas web (`routes/web.php`), fora da spec de API. Previsão: vão
     aparecer como candidatos a intrínsecos no N=0 (D16).
- **Decisão operacional.** A bateria do vAPI **não** será rodada junto com a do VAmPI, para
  não distorcer a métrica de tempo (A4).

### E17 — 10:21 · Documentação de ambiente e protocolo
- `docs/ambiente_experimental.md`: hardware, versões, digests das imagens, commit do vAPI,
  hashes SHA-256 do código, das specs e das wordlists.
- `docs/protocolo_experimental.md`: QP1–QP4, fatores e níveis, fórmulas das métricas,
  procedimento reprodutível, escopo ético e ameaças à validade A1–A9.
- **Rastreabilidade do código medido.** Os arquivos de `shadowscan/` têm timestamp ≤ 09:47:36
  e a bateria começou às 09:52. Logo, a bateria inteira roda com o código cujos hashes estão
  em `ambiente_experimental.md` §2.1.

---

### E18 — 10:24 · Decisão Q1: corrigir o defeito da raiz e refazer a bateria
- O autor escolheu a opção (a) de Q1: corrigir e refazer.
- **Bateria interrompida** (`TaskStop`) durante a execução `n3_s5_auth-nao`. Resultados das 4
  execuções completas antes da interrupção, **invalidados** e arquivados em
  `runs/_invalidadas/exp_vampi_principal_v1_defeito_raiz/` (o N=0 correspondente está em
  `runs/_invalidadas/exp_vampi_n0_v1_defeito_raiz/`):

  | Execução | G | P | R | F1 | FN |
  |---|---|---|---|---|---|
  | n3_s1_nao | `GET /books/v1`, `POST /books/v1`, `POST /users/v1/register` | 1,00 | 1,00 | 1,00 | — |
  | n3_s2_nao | `GET /`, `GET /books/v1`, `PUT /users/v1/{username}/password` | 1,00 | 0,33 | 0,50 | `GET /`, `PUT …/password` |
  | n3_s3_nao | `GET /books/v1/{book_title}`, `POST /users/v1/login`, `POST /users/v1/register` | 1,00 | 1,00 | 1,00 | — |
  | n3_s4_nao | `GET /books/v1`, `GET /books/v1/{book_title}`, `GET /createdb` | 1,00 | 0,67 | 0,80 | `GET /createdb` |

- **Observação relevante (n3_s3):** o template removido `GET /books/v1/{book_title}` foi
  encontrado pela **fase C** (rota-coringa inferida `/books/v1/{param}`, D12). Nenhuma
  wordlist teria gerado esse caminho. É evidência de que a fase C cumpre o seu papel.
- **Correção aplicada (D18).** `/` passa a ser candidato fixo. Novo teste de regressão.
  Testes: **13/13 OK**. Novo hash de `discovery.py`: `F1B728CAF00FD73B`.
- Os dados invalidados **não** entram nas tabelas do artigo. Ficam só como registro histórico
  do defeito, e podem ser citados na discussão como exemplo do processo de validação.

### E19 — 10:24:36 → em andamento · Bateria do VAmPI refeita (versão válida)
- N=0 (sem e com auth) seguido da bateria principal: N ∈ {3, 6} × sementes 1–5 × auth ∈ {não, sim}.
- Código: hashes de `ambiente_experimental.md` §2.1 (discovery.py = `F1B728CAF00FD73B`).
- Saídas: `runs/exp_vampi_n0/`, `runs/exp_vampi_principal/`.

### E20 — ~10:45 · Apuração da origem de `vampi_completa_noauth.json`
- O autor confirmou que **não** executou nada. Investigação:
  1. `ListAgents`: três outras sessões do Claude Code na máquina, todas ociosas, iniciadas há
     6–13 dias, ligadas a outros projetos.
  2. Processos ativos (`Win32_Process`): às 09:51:46–47 surgiram processos do Claude Code com
     `--session-id 780eea92… --fork-session --resume` e `--session-id e027531d… --agent claude`.
  3. Busca nos registros locais de sessão (`~/.claude/projects/C--dev-TCC/*.jsonl`) pelo nome do
     arquivo: o comando que o criou está na sessão `f2f7e58a…`, às 09:47:42 (12:47:42 UTC).
- **Conclusão.** O arquivo foi gerado pelo assistente num ramo da conversa que foi descontinuado
  na bifurcação das 09:51. A entrada E10 foi corrigida.
- **Lição de processo.** Execuções avulsas fora do runner ficam sem registro estruturado. Daqui
  em diante, toda execução de medição passa pelo `run_experiments.py` e é registrada no diário.

### E21 — 10:53 · Primeiro rascunho do artigo
- **Entradas:**
  - `esqueleto-artigo.md` (estrutura de Wazlawick dentro do Anexo I do Manual de TCC);
  - `Guia_Escrita_Artigo_Wazlawick.pdf` (o que cada seção deve responder);
  - `Manual do TCC - Finalizado.pdf` (iCEV, set./2025): mínimo de 20 laudas para artigo, formatação, resumo de 150–500 palavras com abstract obrigatório, ABNT, revisão de Letras com comprovante anexado e roteiro de avaliação do Anexo III.
- **Saída:** `docs/artigo/artigo-rascunho-v1.md`, com cópia em Downloads. ≈ 7.100 palavras, 41 marcadores ⟦PENDENTE⟧ e 14 ⟦VERIFICAR⟧.
- **Seções em texto corrido:** Introdução, Referencial (1.1–1.5), Metodologia, Abordagem e Experimentos.
- **Seções com marcadores:**
  - Resultados — aguardam a bateria válida;
  - Trabalhos relacionados e o confronto com a literatura na Discussão — aguardam a busca bibliográfica.
- **Regras aplicadas:**
  - Nenhuma referência acadêmica citada como firme. Os candidatos ficam em lista separada, "ler e conferir antes de citar".
  - Nenhum número da bateria invalidada usado como resultado.
  - As observações preliminares (casos ambíguos, fase C) estão marcadas para confirmação com os dados válidos.

### E22 — ~10:50–10:57 · Defeito: o token de autenticação do VAmPI expira no meio da execução
- **Sintoma.** Na execução válida `n0_s1_auth-sim` (bateria E19):
  - **3162 caminhos vivos**, contra 17 sem autenticação;
  - 87 202 requisições e 531 s, contra 46 317 e 272 s;
  - ~3150 observações `GET /books/v1/<palavra>` com status 404 (`Book not found!`), todas marcadas como **ambíguas** com o template `/books/v1/{book_title}`.

  Nenhuma virou FP, porque a política conservadora (D8) as tratou como template.
- **Investigação:**
  1. Requisições manuais autenticadas: `/books/v1/<aleatório>` e `/books/v1/Admin` dão respostas **idênticas** (`404 Book not found!`). A lógica de comparação, reproduzida isoladamente (`Discoverer.path_alive`), classifica `/books/v1/Admin` corretamente como **inexistente**. Logo, o defeito não está no critério de soft 404.
  2. Payload do JWT emitido pelo VAmPI: `exp − iat = 60 s`.
  3. Teste com o mesmo token: `GET /me` → **200** em t=0 s e **401** `"Signature expired. Please log in again."` em t=65 s. `GET /books/v1/<x>` → 401 em t=65 s.
- **Causa-raiz.** O runner obtém o token **uma vez** e a execução dura de 270 a 530 s. Depois de 60 s, toda requisição é feita com credencial expirada. Mecanismo do sintoma:
  - os ~3300 candidatos `GET /books/v1/<palavra>` entraram na fila do semáforo **antes** do pedido do baseline do pai (que só é emitido depois da primeira resposta de um candidato);
  - por isso foram atendidos com o token ainda válido (404 `Book not found`);
  - o baseline do pai foi atendido depois da expiração (401 `Signature expired`);
  - nenhuma resposta casou com o baseline, e todos os candidatos foram considerados vivos.
- **Alcance:**
  - **todas as execuções com autenticação** (fator "auth = sim") estão comprometidas: só o primeiro minuto de cada uma é autenticado;
  - as execuções sem autenticação **não** são afetadas.
- **Achado metodológico.** A vida útil da credencial é um parâmetro do experimento que precisa ser controlado. Um scanner que autentica uma só vez mede, na prática, uma mistura de "autenticado" e "credencial expirada". Vai para as ameaças à validade (nova A10).

### E23 — 10:58–10:59 · Decisão Q3 e correção D19
- O autor escolheu a opção (a) de Q3: corrigir e refazer **só** as execuções com autenticação.
- **Implementado (D19):** `auth_refresh` com `refresh_every = 45 s` em `Discoverer`; headers por requisição; contador `renovacoes_auth` no relatório; o runner passa o login do VAmPI como provedor.
- **Testes:** **15/15 OK**, incluindo `test_sem_provedor_headers_fixos`, que prova que sem auth nada muda, e `test_com_provedor_renova_quando_vence`.
- **Arquivada como inválida:** `runs/_invalidadas/exp_vampi_n0_v2_token_expirado/n0_s1_auth-sim`. O `resultados.csv` de `runs/exp_vampi_n0/` ainda tem a linha dela. A fonte de verdade para análise são os diretórios de execução, não esse CSV.
- **Operação da bateria E19.** As 10 execuções sem auth seguem rodando com o código anterior à D19, válido para elas. Um vigia em background encerra o processo da bateria assim que a primeira execução com auth começar. Em seguida: teste de integração da renovação contra o VAmPI real, N=0 com auth e as 10 execuções com auth, com o código D19.

### E24 — 11:07 · Revisão externa do rascunho v1.1 (via Claude Desktop) e incorporação
Quatro apontamentos recebidos. Cada um foi conferido nos dados e no código antes de ser incorporado:
1. **Classificador não avaliado → procede, com correção factual.** A revisão afirmava que nenhuma operação sorteável é de depuração, administrativa ou de versão. Simulando a ocultação de cada operação declarada, a afirmação é **falsa em sentido estrito**:
   - VAmPI: `GET /users/v1/_debug` → `rota_debug` (1/14);
   - vAPI: `POST /vapi/api9/v1|v2/user/login` → `versao_obsoleta`, `GET /vapi/dashboard/flag` → `administrativo` (3/33).

   A conclusão se mantém (amostra mínima, sem rótulo de referência). Texto ajustado para "raramente". Novo achado: `dashboard/flag` (envio de flag de CTF) rotulado como administrativo é um erro da heurística. Intrínsecos: `/console` → administrativo, `/ui` → não classificado. Registrada a **A11**.
2. **Circularidade dos intrínsecos → procede.** O argumento foi reforçado: a inspeção manual é insuficiente para **falsos negativos**, mas adequada para julgar itens **reportados**, que é só o que o procedimento faz. Somado ao argumento de escala.
3. **Enquadramento do `/console` → procede e é necessário.** O código-fonte do VAmPI confirma que o modo debug é **intencional** (`/vampi/app.py:15` "start the app with port 5000 and debug on!"; `:17` `vuln_app.run(host='0.0.0.0', port=5000, debug=True)`). O achado passa a ser enquadrado como divergência de inventário, que independe de intenção. O ⟦VERIFICAR⟧ sobre comunicação responsável foi resolvido: não se aplica.
4. **Identidade descoberta × diferencial → procede.** A nota que a revisão dava como existente **não estava** no rascunho. Foi acrescentada a condição R ∩ G ⊆ G_O, válida por construção.
- **Artefatos:** rascunho v1.2; A11 em `protocolo_experimental.md`; nova entrada em `trabalhos_futuros.md`; este script (`experiments/_aplicar_revisao_e24.py`).

### E25 — 11:14 · Segunda revisão externa: consistência das ameaças à validade
- **Apontado:**
  - A10 fora de ordem no Apêndice B;
  - A11 citada em 3.7, 4.6 e 7.7, mas ausente da tabela do apêndice.
- **Verificação:** procede, e a causa estava **na origem**. Em `protocolo_experimental.md`, a ordem era A8, **A11, A10**, A9, porque cada ameaça nova foi inserida "antes da A9" em vez de no fim. O Apêndice B do rascunho tinha sido gerado antes da A11 existir.
- **Correção estrutural:** `experiments/sincronizar_apendices.py`. O script:
  - ordena a tabela de ameaças na fonte;
  - regenera os apêndices A, B e D a partir de `docs/`, que não devem mais ser editados à mão;
  - valida que toda A# e D# citada no corpo do artigo está definida no apêndice;
  - sincroniza a cópia em Downloads.

  Resultado: A1–A11 e D1–D19 consistentes, ordem OK.
- **Regra de processo:** rodar `python -m experiments.sincronizar_apendices` depois de qualquer alteração em `decisoes.md`, `protocolo_experimental.md` ou `ambiente_experimental.md`.
- Lembrete inserido na §7.7 do rascunho: discutir as ameaças à luz dos resultados, sem repetir a tabela.

### E26 — 11:14–11:19 · Regras de fonte única e trava contra sobrescrita
- **Apontado pelo autor:** revisão de tom nos apêndices feita no artigo seria apagada pelo próximo sync, e um sync esquecido no fim entregaria apêndice desatualizado.
- **Verificação:** procede. Identificado um segundo risco do mesmo tipo: o sync **copiava o rascunho por cima da cópia em Downloads**, o que apagaria edições feitas nela (pelo autor ou via Claude Desktop).
- **Regras fixadas:**
  1. **Apêndices:** a fonte única é `docs/` (`decisoes.md`, `protocolo_experimental.md`, `ambiente_experimental.md`). Toda revisão, inclusive de tom, é feita lá. A nota no topo dos apêndices do artigo passou a dizer isso.
  2. **Corpo do artigo:** a fonte única é `docs/artigo/artigo-rascunho-v1.md`. A cópia em Downloads é só para leitura e envio.
  3. **`diario_de_pesquisa.md` não é revisado por tom:** é registro histórico, e só recebe novas entradas ou correções explicitamente marcadas (como a E10).
- **Trava implementada:** o script grava o SHA-256 da cópia em Downloads (`docs/artigo/.ultimo_sync`) e **aborta** se ela mudou desde o último sync (`--forcar` descarta as edições conscientemente). **Testado:** com a cópia editada, abortou e preservou a edição; depois de restaurada, sincronizou.
- **Checklist:** a execução do sync como **última etapa antes da conversão para Word (27/11)** foi incluída na tabela de pendências do rascunho e na §18 (verificação final) do `esqueleto-artigo.md` (cópia do projeto e original em Downloads). Depois da conversão para Word, o script não alcança o documento.

### E27 — 11:19–11:20 · Fim das execuções sem auth (código pré-D19) e dois defeitos novos
- **Parada da bateria E19.** O vigia disparou no início de `n3_s1_auth-sim` e encerrou os processos (PIDs 25920 e 39392). O código de saída 255 é efeito do encerramento. A pasta parcial `n3_s1_auth-sim`, sem resultado, foi arquivada em `runs/_invalidadas/exp_vampi_principal_v2_token_expirado/`.
- **Anomalia.** FPs `GET /users/v1/admin`, `/message` e `/status` em n3_s5, n6_s1, n6_s2 e n6_s5 (precisão de 0,50 a 0,62). Todas são execuções em que o sorteio ocultou `GET /users/v1/{username}`.
- **Investigação (dados e requisições diretas):**
  - `/users/v1/message` e `/users/v1/status` → `404 {"status": "fail", "message": "User not found"}`, **idêntico** ao de um nome aleatório. **Não são usuários.**
  - Reprodução em `normalize_body`: o segmento `message` virava `{SEG}` dentro da chave JSON, só no candidato. → **defeito da D5**, corrigido pela **D20** (normalização simétrica).
  - `/users/v1/admin` → `200 {"username": "admin", …}`: usuário **real**. Era reportado ao lado da rota-coringa inferida `/users/v1/{param}`, que também é reportada. É o mesmo endpoint contado duas vezes. → corrigido pela **D21** (agrupamento em template observado).
- **Hipótese anterior refutada.** Antes da investigação, eu tinha dito ao autor que suspeitava de um defeito *da métrica*. Era um defeito da *comparação de respostas* (D20) mais uma lacuna do *diff* (D21). A métrica estava correta.
- **n6_s4 (R = 0,17) — limitação, não defeito.** G incluía todos os caminhos sob `/books` (`GET|POST /books/v1`, `GET /books/v1/{book_title}`). Nenhuma observação sob `/books` existe. Sem prefixo declarado, a ferramenta só testa `/books` (da wordlist), que não existe como rota, e nunca gera `/books/v1`. Registrado em `trabalhos_futuros.md`. Entra na discussão da A3.
- **Testes:** **19/19 OK** (4 novos: D20 ×2, D21 ×2).
- **Impacto da D21 medido offline** (só o diff recalculado sobre as observações gravadas): precisão 1,00 nas 10 execuções. A D20 afeta a descoberta e só pode ser medida com nova execução.
- **Decisão do assistente** (autor havia pedido vigilância máxima contra perda de nota): **refazer a bateria inteira do VAmPI** com o código final (D19 + D20 + D21). Motivo: manter as execuções sem auth com código anterior à D20 e as com auth com código posterior criaria a objeção "versões diferentes do código entre condições". O custo é só tempo de máquina, e os dados anteriores foram preservados em `runs/_substituidas/` (não são inválidos, foram substituídos por versão posterior).
- **Bateria definitiva iniciada (11:20:25):** N=0 (sem e com auth) e depois N ∈ {3, 6} × sementes 1–5 × auth ∈ {não, sim}. A N=0 com auth serve como **teste de integração da D19**: espera-se `renovacoes_auth > 0` e cerca de 17 caminhos vivos (contra 3162 no defeito E22).
- Hashes do código final em `ambiente_experimental.md` §2.1.

### E28 — 11:30 · Correção de horários do próprio diário e teste de integração da D19
- **Erro de registro identificado pelo assistente:** os horários de E21 a E27 tinham sido escritos como **estimativas**, sem consultar o relógio, e estavam adiantados em até 1h10 (ex.: E27 anotada como ~12:30; real 11:19). Corrigidos com base nos timestamps dos arquivos produzidos em cada etapa:

  | Entrada | Anotado | Real | Evidência |
  |---|---|---|---|
  | E21 | ~11:00 | 10:53 | criação de `docs/artigo/artigo-rascunho-v1.md` |
  | E22 | ~11:15 | ~10:50–10:57 | teste de expiração disparado às 10:55:16 |
  | E23 | ~11:25 | 10:58–10:59 | `shadowscan/discovery.py` 10:58:24; vigia 10:58:58 |
  | E24 | ~11:50 | 11:07 | `experiments/_aplicar_revisao_e24.py` |
  | E25 | ~12:00 | 11:14 | `experiments/sincronizar_apendices.py` |
  | E26 | ~12:10 | 11:14–11:19 | `docs/artigo/.ultimo_sync` (11:14:29) e arquivos de E27 |
  | E27 | ~12:30 | 11:19–11:20 | `responses.py` 11:19:37, `diff.py` 11:19:52, bateria 11:20:25 |

  Os cabeçalhos do rascunho (v1.1–v1.3) e o status em Downloads tinham o mesmo erro e também foram corrigidos.
- **Regra de processo:** daqui em diante, todo horário do diário é **lido do relógio** (`date`) ou de timestamp de arquivo. Nunca estimado.
- **Teste de integração da D19 (bateria definitiva, N=0):**

  | Execução | Requisições | Renovações de auth | Caminhos vivos | Tempo |
  |---|---|---|---|---|
  | n0_s1_auth-nao | 46 291 | 0 | 15 | 266,8 s |
  | n0_s1_auth-sim | 46 291 | **7** | **15** | 289,1 s |
  | *(defeito E22, para comparação)* | 87 202 | — | 3162 | 531,4 s |

  A renovação funcionou: 7 renovações em 289 s, compatível com 1 a cada 45 s. Os caminhos vivos com auth caíram de 3162 para 15 e são **iguais** aos sem auth. **Achado:** com credencial válida e renovada, a autenticação de usuário comum **não revela nenhum caminho adicional** no VAmPI.
- **Efeito da D20 visível no N=0:** caminhos vivos passaram de **17 para 15** em relação à versão anterior do código. `/users/v1/message` e `/users/v1/status` deixaram de ser falsamente considerados vivos.

### E29 — 12:50–12:53 · Bateria definitiva do VAmPI concluída e verificações de validade
- **Execução:** 11:20:25–12:50. N=0 (2 execuções) mais 20 execuções (N ∈ {3, 6} × sementes 1–5 × auth ∈ {não, sim}). Código final (D19–D21, hashes em `ambiente_experimental.md`). **0 erros de rede** nas 20. Renovações de auth: 4–7 por execução com login.
- **Resultados (`runs/exp_vampi_principal/resumo.md`, gerado por `analyze.py`):**

  | Auth | N | P ajustada | P bruta | R | F1 ajustado | Descoberta | Diferencial |
  |---|---|---|---|---|---|---|---|
  | não/sim | 3 | 1,00 ± 0,00 | 0,28 ± 0,05 | 0,80 ± 0,18 | 0,88 ± 0,11 | 12/15 (0,80) | 12/12 (1,00) |
  | não/sim | 6 | 1,00 ± 0,00 | 0,38 ± 0,14 | 0,67 ± 0,29 | 0,76 ± 0,27 | 20/30 (0,67) | 20/20 (1,00) |

  - Revocação por tipo: `caminho` 25/38 (0,66); `metodo` 7/7 (1,00).
  - FN, todos de **descoberta**: `GET /createdb` (10 execuções), `GET /users/v1/_debug` (6), `PUT /users/v1/{username}/password` (4), subárvore `/books` (n6_s4, 3 endpoints × 2).
  - FP ajustados: **nenhum**. A precisão bruta baixa (0,28–0,38) vem dos 6 intrínsecos (`/console` × 5 e `/ui`), repetidos em toda execução.
  - Custo: ~40 mil requisições e ~240 s por execução.
- **Verificação 1 — com auth = sem auth em todas as métricas. A autenticação estava efetiva?** Sim. Comparando os status por endpoint em n3_s1:
  - `GET /me` 401 → 200;
  - `GET /books/v1/{book_title}` 401 → 404;
  - `POST /books/v1` 401 → 400;
  - `PUT …/email` e `PUT …/password` 401 → 400.

  A credencial mudou as respostas, mas **não o conjunto de endpoints existentes**. No VAmPI, todo endpoint protegido responde 401 sem credencial, e esse 401 já difere do "não encontrado" do framework (404). A existência é detectável sem autenticação. **Conclusão para QP3:** neste alvo, autenticação de usuário comum não altera a superfície detectada. Não se generaliza a alvos em que o middleware de auth responde igual para rotas existentes e inexistentes (A2).
- **Verificação 2 — divergência entre pares equivalentes.** Os conjuntos de observações com e sem auth são idênticos em 9 de 10 pares. Em n3_s1, `GET /users/v1/admin` foi observado só sem auth (sem efeito em métrica: o caminho é absorvido pelo template declarado). Causa: **a varredura chama `GET /createdb`** (endpoint declarado), que executa `drop_all()`/`create_all()` (`/vampi/api_views/main.py:6–8`) enquanto outras 9 requisições estão em curso. Nos logs do VAmPI: 64 chamadas a `/createdb` no período, **3 com status 500** e **2 erros `no such table`**. Explica também o `GET /createdb` 200 (sem auth) × 500 (com auth) em n3_s1, que é colisão de timing e não efeito da autenticação: em série, a chamada com auth responde 200. → nova ameaça **A12**.
- **Verificação 3 — o diferencial isolado em 1,00 é trivial?** Os 32 removidos descobertos (sem auth) chegaram ao diferencial por cinco mecanismos: wordlist 12, prefixo 7, método variado em caminho declarado 7, raiz 3, rota-coringa 3. Todos foram classificados corretamente, inclusive os três templates ocultados encontrados só pela fase C. **Porém, o caso difícil não foi exercitado.** O único removido literal que colidiria com um template declarado é `GET /users/v1/_debug` sob `/users/v1/{username}` (n6_s3 e n6_s4), e ele **nunca foi descoberto** (`_debug` fora da wordlist). Se fosse, a política conservadora D8 o absorveria no template, e ele seria um **FN do diferencial**. Portanto, o 1,00 vale para os mecanismos exercitados e **não demonstra ausência do ponto cego da D8**, que é conhecido e previsto. Isso deve constar do artigo (§7.4/§7.5).

### E30 — 12:52–13:22 · vAPI inviável por lentidão do servidor: diagnóstico e correção de infraestrutura
- **Sintoma.** A bateria do vAPI, iniciada às 12:52:42, continuava na **primeira** execução (N=0) às 13:15, sem resultado gravado. Uma execução do VAmPI leva ~4 min.
- **Medições:**
  - log do container: ~1 linha/s, com "Accepted" e "Closing" por requisição, ou seja, ~0,5 req/s;
  - requisição isolada, depois de parar a bateria e reiniciar o container: **~2,2 s cada** (`/vapi/zzab12` 2,24 s; `/vapi/api1/user/1` 2,30 s);
  - com a fila da bateria, uma requisição manual passava de 120 s sem resposta: o servidor (`php artisan serve`) atende **uma requisição por vez**.

  Projeção: ~46 mil requisições × 2,2 s ≈ **28 h por execução**, ~300 h para a bateria. Inviável.
- **Causa:** o `docker-compose.yml` original monta o código a partir do disco do Windows (`./vapi:/var/www/html/vapi`). No Docker Desktop para Windows, montagens desse tipo têm I/O lento, e o Laravel lê centenas de arquivos PHP por requisição. Somava-se o atendimento serial.
- **Restrição descoberta ao planejar a remoção da montagem:** o `Dockerfile` executa `artisan config:cache` no build, **sem** as variáveis de ambiente, o que fixa o banco em `127.0.0.1`. Hoje a montagem esconde esse cache, porque `bootstrap/cache` do host não tem `config.php`. Removê-la sem `config:clear` quebraria o acesso ao banco.
- **Correção (infraestrutura, código da aplicação intocado):** no override, remover a montagem, executar `config:clear` antes de `artisan serve` e definir `PHP_CLI_SERVER_WORKERS=10`. Detalhes em `ambiente_experimental.md` §5.
- **Verificação de equivalência:**
  - repetição das sondagens da E16: mesmos status e tamanhos de corpo (`500 {}` 2 B para inexistentes e para GET em rota POST-only; 403 de 47 B e 46 B; `/vapi` 1 153 179 B; `/` 9 295 B; `POST api9/v1/user/login {}` 200);
  - escrita no banco: `POST /vapi/api1/user` → **201** (efeito colateral: usuário `tcc_probe_e30`, id 5, criado no vAPI, que não tem reset);
  - latência isolada: **0,065 s** (~35× menor);
  - 20 requisições paralelas em 0,47 s.
- **Dados:** a tentativa interrompida (N=0 sem resultado) foi arquivada em `runs/_invalidadas/exp_vapi_n0_v1_servidor_lento/`.
- **Bateria do vAPI reiniciada às 13:22:06**, com N=0 e depois N ∈ {3, 6} × sementes 1–5, sem auth.
- **Observação metodológica:** o tempo de execução é métrica de custo. Os tempos do vAPI refletem esta configuração de servidor (10 workers, código dentro da imagem) e **não são comparáveis** aos do VAmPI (Flask com o servidor de desenvolvimento do Werkzeug). Reportar o custo por alvo, sem comparação direta.

### E31 — 13:23–13:26 · Defeito no gerador de apêndices e rascunho v1.5
- **Defeito encontrado na leitura do rascunho:** `sincronizar_apendices.py` rebaixava em dois níveis toda linha iniciada por `#`, **inclusive dentro de blocos de código**. Os comentários de shell do procedimento (Apêndice B: `# 1. Ambientes…`) viravam títulos (`### 1. Ambientes…`), o que corrompia o bloco. Corrigido: linhas dentro de blocos ``` são preservadas. Verificado no rascunho: as linhas 926–938 voltaram a ser comentários.
- **Rascunho v1.5** (`experiments/_artigo_v15.py`), com tudo o que os dados do VAmPI sustentam:
  - **Resumo e Abstract:** resultados do VAmPI (P 1,00; R 0,80/0,67; todos os FN de descoberta; autenticação sem efeito). Resumo com 381 palavras, sem contar marcadores (limite 500).
  - **§4.4:** limiar fixado a priori; sensibilidade como trabalho futuro.
  - **§4.5:** remissão à §7.5.
  - **§5.1 e §5.2:** ajuste de infraestrutura do vAPI e a não comparabilidade de tempos entre ambientes. **§5.4:** execução do VAmPI.
  - **§7.1:** respostas às QP1–QP4 para o VAmPI.
  - **§7.5:** quantificação da política conservadora. Único caso ambíguo: `GET /users/v1/admin`, em 19 de 20 execuções (11 contra o template declarado, 8 contra o inferido, D21). A política alternativa somaria 19 FP.
  - **§7.7:** reescrita à luz dos resultados, separando ameaças manifestadas e medidas (A1, A3, A10, A12), não manifestadas (A2, A8) e limitantes (A4, A5, A6, A7, A9, A11).
  - **§7.8:** fronteiras de generalização.
  - **Considerações finais:** tabela de objetivos com a evidência do VAmPI.
- **Afirmações conferidas contra os dados:**
  - "16 dos 26 FN" (createdb 10 + _debug 6, num total de 26 = 10 + 6 + 4 + 6);
  - "1 divergência em 10 pares";
  - "19 ambíguos";
  - "32 por condição de autenticação (12 + 20)". A redação dessa última foi corrigida, porque estava ambígua.
- **Pendências restantes:** 42 marcadores no rascunho, agrupados em três bloqueios: dados do vAPI, Seção 2 (literatura) e os ⟦VERIFICAR⟧.

### E32 — 13:29–13:34 · Terceira revisão externa: erosão de âncoras (A13) e mecanismo da A12
**1. A revocação cai com N por efeito do método → procede, com uma calibragem.** Decomposição dos FN das execuções sem auth:

| N | Removidos | FN por limite fixo (createdb, _debug, …/password) | FN por perda de âncora (/books) | Revocação | Revocação sem o efeito de âncora |
|---|---|---|---|---|---|
| 3 | 15 | 3 (0,20) | 0 (0,00) | 0,80 | 0,80 |
| 6 | 30 | 7 (0,23) | 3 (0,10) | 0,67 | 0,77 |

Dos 0,13 pontos de queda, 0,10 vêm da perda de âncora e 0,03 do sorteio de endpoints difíceis. O diferencial isolado fica em 1,00 nas duas condições, sem ser afetado. Registrada a **A13** (construto).
- **Calibragem do assistente:** a revisão afirmava que N alto "não corresponde a nada real" e que a revocação "subestima o desempenho realista". Isso não foi adotado sem ressalva, porque subárvores inteiras não documentadas existem em APIs reais e são o caso difícil. Formulação adotada: com N alto, a revocação fim a fim **mistura** a dificuldade do alvo com a degradação da especificação, e deve ser lida junto com a decomposição.

**2. O `/createdb` como confundidor → procede, e foi verificado em log** (`docker logs vampi`, horário UTC = local + 3 h). Janelas reconstruídas a partir do timestamp e da duração de cada `resultado.json`:
- `n3_s1_auth-nao` (14:29:45–14:34:24 UTC): `GET /createdb` da varredura → **200** às 14:29:45; `GET /users/v1/admin` → **200** às 14:31:23.
- `n3_s1_auth-sim` (15:09:49–15:14:38 UTC): `GET /createdb` da varredura → **500** às 15:09:50; `GET /users/v1/admin` → **404** às 15:11:34.

Cadeia causal: a recriação do banco feita pela própria varredura falhou por concorrência, o banco ficou sem os usuários padrão e o admin não existia no momento da sondagem. **Não foi efeito da autenticação.** A12 atualizada com o mecanismo. O artigo liga os dois fatos: §6.5 traz os fatos do log, e §7.7 a interpretação.

**3. Menor (22 × 20 execuções) → procede.** A §5.4 agora explicita: 20 da bateria (tabelas) + 2 com N = 0 (intrínsecos).

**Artefatos:** A13 e A12 em `protocolo_experimental.md`; rascunho v1.6 (§3.7, §5.4, §6.5, §7.1, §7.4, §7.7, Considerações).

### E33 — 13:56 · Estimativa do vAPI e retomada de bateria interrompida
- **Custo do vAPI:** 27 prefixos-base da wordlist, contra 5 no VAmPI, dão ~95 mil candidatos na fase A. Como o vAPI responde `500 {}` a GET em qualquer caminho, o POST também é sempre sondado, o que dá ~190 mil requisições por execução (VAmPI: ~46 mil). Vazão medida: ~89 req/s. Resultado: ~36 min por execução e ~6,5 h para as 11 (início 13:22:06).
- **Decisão:** não aumentar a concorrência (10) só para o vAPI. Seria desvio de protocolo entre alvos, e a A12 mostrou que a concorrência interage com o estado do alvo.
- **Interrupção prevista:** o autor informou que a máquina ficará indisponível até ~18:00. Execuções interrompidas ficam sem `resultado.json`.
- **`--retomar`** em `run_experiments.py`: pula execuções que já têm `resultado.json` e refaz do zero as interrompidas. Spec e ground truth são regenerados pela semente, idênticos aos anteriores. Não altera nada na medição.
  - O `resultados.csv` de uma bateria retomada só contém as execuções do processo atual.
  - A fonte de verdade da análise são os diretórios de execução, lidos por `analyze.py`.
- **Comando de retomada:**
  `python -m experiments.run_experiments --alvo vapi --n 0 --seeds 1 --out runs\exp_vapi_n0 --retomar` e depois
  `python -m experiments.run_experiments --alvo vapi --n 3 6 --seeds 1 2 3 4 5 --out runs\exp_vapi_principal --retomar`.

### E34 — 14:39–14:41 · vAPI N=0: intrínsecos verificados e zombies falsos por colapso de erros
- **Contexto:** a máquina não foi desligada como previsto em E33, e a bateria do vAPI seguiu sem interrupção. No log aparece um `ConnectionResetError` (WinError 10054) em `_ProactorBasePipeTransport._call_connection_lost`: é um aviso conhecido do `asyncio` no Windows quando o servidor fecha a conexão, registrado mas não fatal. Contador de erros da execução: 0.
- **Execução `n0_s1_auth-nao` (vAPI):** 191 390 requisições, **0 erros**, 32 caminhos vivos, 2 214,97 s (~37 min).
- **Candidatos a intrínsecos (7), todos verificados manualmente:**
  - `GET /` (200, `text/html`, 9 295 B) e `GET /vapi` (200, 1 153 179 B): rotas de `routes/web.php` (linhas 16 e 20), páginas HTML `<title>vAPI</title>`, fora da API. Previsto na D16.
  - `/favicon.ico` em GET/POST/PUT/PATCH/DELETE (200, `image/x-icon`, 0 B): arquivo estático `public/favicon.ico`, servido pelo servidor embutido do PHP para qualquer método.
  - Registrados em `specs/vapi_intrinsecos.json`.
- **Zombies: `POST /vapi/api7/user` e `GET /vapi/user`.** São rotas declaradas no roteador, portanto existentes por construção, mas não observadas. Investigação:
  - ambas respondem `500 {}` (2 B), **idêntico** a `GET /vapi/zzinexistente` e a `POST /vapi/api7/zzinexistente`, com ou sem `Accept: application/json`;
  - `POST /vapi/api7/user`: `API7UsersController::store` (linhas 38–44) faz `json_decode` do corpo e lê `$user['username']` sem validação. Com o corpo `{}` da sondagem (D13), lança exceção;
  - `GET /vapi/user`: rota com `middleware('auth:sanctum')`; sem credencial, lança `AuthenticationException`;
  - **causa comum:** `app/Exceptions/Handler.php:37–39` registra `renderable(function (Throwable $e, $request) { return response(json_encode($e),500)… })`. Toda exceção vira `500` com corpo `json_encode` do objeto de exceção, ou seja, `{}`. Não encontrado, não autenticado e erro de aplicação **colapsam na mesma resposta**.
- **Interpretação:** não é defeito da ferramenta. É o **limite informacional** de uma abordagem que decide existência pela resposta: quando o alvo colapsa todos os erros numa resposta única, uma rota que lança exceção com a entrada da sondagem é indistinguível de uma inexistente. A **A2** se manifestou no vAPI, de forma mais geral que a prevista (não só autenticação, mas qualquer exceção). **Consequências:**
  1. o relatório de **zombies** não é confiável nesse tipo de alvo (2 zombies falsos);
  2. se essas rotas forem sorteadas no ground truth, serão FN de descoberta inevitáveis.
- **Mitigação possível (fora do escopo congelado → trabalho futuro):** sondar com corpos derivados dos esquemas da especificação, em vez de `{}`. Não resolveria a rota protegida.

### E35 — 21:15–21:17 · Bateria do vAPI concluída: replicação do diferencial e causas dos FN
- **Execução:** 13:22:06–21:15:49. N=0 mais 10 execuções (N ∈ {3, 6} × sementes 1–5, sem auth), ~158–191 mil requisições cada. Código final, o mesmo do VAmPI.
- **Resultados (`runs/exp_vapi_principal/resumo.md`):**

  | N | P ajustada | P bruta | R | F1 ajustado | Descoberta | Diferencial isolado |
  |---|---|---|---|---|---|---|
  | 3 | 1,00 ± 0,00 | 0,28 ± 0,03 | 0,93 ± 0,15 | 0,96 ± 0,09 | 14/15 (0,93) | **14/14 (1,00)** |
  | 6 | 1,00 ± 0,00 | 0,33 ± 0,03 | 0,57 ± 0,09 | 0,72 ± 0,07 | 17/30 (0,57) | **17/17 (1,00)** |

  - Revocação por tipo: `caminho` 26/40; `metodo` 5/5.
  - FP ajustados: **nenhum**. Os FP brutos são os 7 intrínsecos verificados em E34.
- **Replicação.** O diferencial isolado em 1,00 se repetiu num alvo com especificação derivada do roteador (completa por construção), outro framework (Laravel) e soft 404 de outra natureza (500 `{}`). A conclusão da QP2 deixa de depender de um único alvo.
- **Erros de rede:** 39, concentrados em n3_s1 (13), n3_s3 (9) e n3_s5 (17). São as mesmas execuções com tempo anômalo (3124–4156 s, contra ~1900–2330 s nas demais). As três tiveram **revocação 1,00 e nenhum FP**, então os erros (timeouts de 10 s num período de máquina mais lenta) não produziram nenhum FN observável.
- **Causa de cada FN (14 no total)**, verificada por requisição direta com corpo `{}` e checagem da wordlist:
  - **A13, perda de âncora (8):**
    - `GET /vapi/api10/user/flag` (4) responde 200 `{"message": …}`;
    - `GET /vapi/dashboard/flag` (2) responde 200 `{"success":"true"}`;
    - `api8/user/secret` + `api8/user/login` (n6_s5, 1 + 1).

    Cada um era o único endpoint sob seu prefixo (`/vapi/api10`, `/vapi/dashboard`, `/vapi/api8`). Ocultá-lo apaga a subárvore da especificação, e `api10`, `dashboard` e `api8` não estão na wordlist. **Experimento natural:** `GET /vapi/api8/user/secret` ocultado sozinho (n3_s2, n3_s3, n6_s4) **foi encontrado**, porque `POST /vapi/api8/user/login` continuava declarado e ancorava `/vapi/api8/user`. Ocultado junto com o login (n6_s5), foi perdido.
  - **A2, colapso de erros (3):** `GET /vapi/user` responde `500 {}`, idêntico a um caminho inexistente (E34).
  - **A3, cobertura da wordlist (3):**
    - `POST /vapi/api4/otp/verify` (2) responde 403 `Invalid OTP`, distinto do inexistente, mas `otp` não está na lista (o prefixo `/vapi/api4` continua declarado);
    - `GET /vapi/serversurfer` (1) responde 403 distinto, mas `serversurfer` não está na lista.
- **Efeito de N, decomposto por causa:**

  | N | Removidos | FN A13 (âncora) | FN A2 (colapso) | FN A3 (wordlist) | Revocação | Revocação sem A13 |
  |---|---|---|---|---|---|---|
  | 3 | 15 | 1 (0.07) | 0 (0.00) | 0 (0.00) | 0.93 | 1.00 |
  | 6 | 30 | 7 (0.23) | 3 (0.10) | 3 (0.10) | 0.57 | 0.80 |

  No vAPI, a erosão de âncoras é **ainda mais forte** que no VAmPI. A estrutura do alvo (dez sub-APIs, várias com um único endpoint) faz com que ocultar uma operação frequentemente apague um prefixo inteiro. A A13 está replicada.
- **Tempo:** ~36 min por execução nas não anômalas. Não comparável com o VAmPI (servidores diferentes, §5.2).

- **Rascunho v1.8** (`experiments/_artigo_v18.py`), com os resultados do vAPI:
  - Resumo e Abstract;
  - §5.4;
  - Tabelas 1b e 3b; FN por causa e custo do vAPI (§6.5–6.7);
  - §7.1 reescrita para os dois alvos; §7.3 quantificada; §7.4 com a replicação da A13 e o experimento natural do `api8`; §7.7; §7.8;
  - Considerações finais.

  Números conferidos contra os dados antes da inserção. O Resumo ficou com 458 palavras sem os marcadores (limite 500: **sem folga para crescer**). Restam 26 marcadores, quase todos de literatura (Seção 2 e confrontos) e ⟦VERIFICAR⟧.

### E36 — 00:49 (18/11) · Quarta revisão externa: timeout, controle negativo e rótulo contrafactual

Revisão colada pelo autor, conferida nos dados antes de aceita.

1. **Política de timeout → procede, com correção.** `discovery.py:223` não repete a requisição: conta o erro e devolve `None`. A revisão não detalhava o efeito; a conferência no código mostrou que ele **não é só FN**. Baselines que falham são descartados em silêncio (`discovery.py:239`, `:249`), e o baseline do pai fica em cache vazio se as duas requisições falharem, o que **pode, em princípio, produzir FP**. Nenhum limite de invalidação foi fixado a priori. Nas 3 execuções do vAPI com erros (39 no total), revocação 1,00 e 0 FP: efeito nulo observado. **Documentado como limitação, sem alterar código** (regra do freeze). Texto: §5.3 (novo parágrafo "Falhas de rede") e §6.7.
2. **Controle negativo → procede.** O N = 0 já cumpria o papel (G = ∅), sem o nome. Nomeado na §3.3. Na §6.1, registrado com honestidade que o controle **não saiu limpo quanto a zombies no vAPI** (2 zombies falsos, A2/E34).
3. **Rótulo nos contrafactuais → procede.** "Seria 0,77/0,80" estava no tom de valor medido (§7.1, §7.4, A13). Rotulado como estimativa contrafactual, com o cálculo: (VP + FN por âncora)/G = (20 + 3)/30 no VAmPI e (17 + 7)/30 no vAPI.
4. **Não procedeu:** a revisão dizia "amanhã, dia 18" (já era 18/11) e repetia "até 2,5 pontos" do esqueleto, que é inconsistente (itens 4 + 8 + 6 = 3,5; o 2,5 só fecha com os itens 4 + 6).

### E37 — 00:55 (18/11) · Fontes primárias conferidas: ⟦VERIFICAR⟧ resolvidos e anos das referências

Cada item foi conferido na fonte, buscada em 18/11/2026.

- **OWASP API9:2023 → corrigida uma afirmação falsa do rascunho.** O texto atribuía à categoria "endpoints de depuração ainda acessíveis". A página oficial (api-security.owasp.org/editions/2023/en/0xa9-improper-inventory-management) **não menciona depuração**. Fala de versões antigas, de endpoints deixados sem correção, de documentação desatualizada e do *documentation blindspot* ("there is no documentation or the existing documentation is not updated"). §1.2 reescrita a partir do texto oficial, com a ressalva explícita de que o enquadramento do `/console` decorre da divergência documentação × superfície e não de menção explícita. Citação no corpo corrigida de (OWASP, 2023) para (OWASP FOUNDATION, 2023), para casar com a entrada da lista. A URL antiga redireciona (308) para api-security.owasp.org.
- **Werkzeug:** a documentação (3.1.x) confirma "Inside the interactive consoles you can execute any kind of Python code", "The debugger must never be used on production machines" e "The debug console is protected by a PIN". O VAmPI roda o **Werkzeug 2.2.3** (`pip show` no container). A documentação da 2.2.x redireciona para a 3.1.x; o PIN existe nas duas. Entrada PALLETS (2024; a versão 3.1.0 foi publicada no PyPI em 31/10/2024).
- **difflib:** `ratio()` = 2M/T; o algoritmo "predates, and is a little fancier than" o *gestalt pattern matching* de Ratcliff/Obershelp. Citada a documentação da versão usada (Python 3.14.4). O artigo original de Ratcliff/Obershelp **não** foi citado, por não ter sido lido.
- **Manning et al. (2008):** P, R e F (média harmônica ponderada; F1 com β = 1) estão na **seção 8.3**, conferida na edição online (cópia do Internet Archive; o servidor de Stanford recusou a conexão). A página impressa não foi conferida e por isso não foi citada.
- **Kiterunner:** o README confirma que as listas foram montadas "by collating a dataset of Swagger specifications", coletadas de várias fontes, inclusive "an internet wide scan".
- **OpenAPI:** adotada a 3.0.3 (20/02/2020), conforme a preferência registrada no rascunho, por ser da mesma linha 3.0.x das specs usadas (VAmPI 3.0.1, vAPI 3.0.0).
- **"Predominante" (Introdução):** sem fonte, a afirmação foi suavizada para "amplamente adotado".
- **Anos das referências de software (ano da versão usada):** VAmPI 2026 (imagem de 07/04/2026); vAPI 2025 (commit `67152695`, 09/01/2025); SecLists 2026 (master baixada em 17/11/2026); Kiterunner 2021 (v1.0.2, 11/04/2021). Datas obtidas pela API do GitHub.

- **Ferramentas (Introdução):** o complemento OpenAPI do ZAP "allows you to spider and import OpenAPI (Swagger) definitions"; o nuclei usa as especificações "to generate HTTP requests and test them against the target". Nenhuma das duas páginas descreve comparação spec × superfície. Os READMEs do ffuf e do gobuster não contêm "openapi", "swagger" nem "specification". O texto afirma só o que as documentações dizem, sem afirmar que a função não existe. Ano de cada entrada = última versão publicada na data do acesso.

**⟦VERIFICAR⟧ restantes:** termo *shadow endpoint* (§Introdução), uso de "zombie", origem de *soft 404* (as três aguardam a busca bibliográfica) e a página do Wazlawick (exige o livro físico).

### E38 — 01:13 (18/11) · Busca bibliográfica, blocos 2.1 e 2.2: dois trabalhos próximos e reformulação da lacuna

Relatórios completos em `docs/literatura/bloco_2_1_teste_rest.md` e `docs/literatura/bloco_2_2_inferencia_conformidade.md`. Todos os DOIs desses relatórios foram reconferidos no Crossref (e os pré-prints no arXiv) pelo assistente, e todos existem.

**1. Amoruso, Amoruso, Broqi e Zou (ISNCC 2026, p. 1–7, DOI 10.1109/ISNCC70543.2026.11693891), "Zombie APIs: Detecting Runtime-Reachable but Deprecated Endpoints".** Lido só o resumo (OpenAlex):
- descoberta ativa a partir da URL alvo (mutação de método, enumeração de versões, sondagem por cabeçalhos) com "differential response analysis";
- descoberta de 90–100% e FP de 0–15%;
- parte da mesma premissa do shadowscan: as ferramentas "assume that published specifications are complete".

Consequência: **a lacuna "ausência de método publicado que meça a acurácia" deixa de valer.** As diferenças, segundo o resumo: o trabalho funciona "without relying on complete specifications" (não faz o diferencial O\D contra a OpenAPI), não constrói ground truth por degradação e não separa descoberta de diferencial. Isso precisa ser **confirmado no texto completo** antes de entrar no artigo. A tentativa de download automático foi bloqueada; o autor baixa pelo IEEE Xplore (doc. 11693891). Há também conflito de termo: para eles, *zombie* = endpoint obsoleto, não documentado ou oculto ainda acessível; no shadowscan, *zombie* = D\O.

**2. Yandrapally, Sinha, Tzoref-Brill e Mesbah (ICSE 2023, DOI 10.1109/ICSE48619.2023.00167), APICARV.** O texto completo (arXiv 2305.14692v1) foi conferido pelo assistente:
- inferência de endpoints com "98% precision and 56% recall against the ground truth of existing API specifications";
- "one API endpoint found through probing [...] provides a health-check for the service despite being absent in the specification, a potential inconsistency": a precisão de caminho cai de 1,0 para 0,98;
- sondas OPTIONS/HEAD derrubam a precisão de operações de 85% para 48%, porque "are not handled correctly in any of the subjects".

**Usos no artigo:**
- (a) é o mesmo fenômeno do `/console`, contado lá como FP contra uma spec suposta correta. Isso sustenta a D9 e o par bruta × ajustada;
- (b) dá evidência externa para a D11 (OPTIONS e HEAD fora dos métodos padrão);
- (c) eles *inferem* templates por similaridade, enquanto o shadowscan *recebe* os templates da spec e só casa (argumento para D3/D8).

**3. Lacuna reformulada (proposta, a confirmar depois da leitura de Amoruso et al.):** não foi encontrado, nas buscas feitas, trabalho que use o diferencial entre a superfície observada por descoberta ativa caixa-preta e a especificação OpenAPI declarada como mecanismo principal de detecção, avaliado com ground truth controlado que separe a contribuição da descoberta da do diferencial.

**4. Protocolo de busca:** o DBLP bloqueou as consultas automáticas e **não pode** ser declarado como base consultada. As bases efetivas foram Semantic Scholar, OpenAlex, Crossref e arXiv, com limites de taxa registrados nos relatórios. Google Scholar, IEEE Xplore e ACM DL não foram consultados.

### E39 — 01:20 (18/11) · Seção 2 redigida, confronto com a literatura na Discussão, ⟦VERIFICAR⟧ de termos

**Fontes conferidas no texto original pelo assistente:**
- **NIST SP 800-228-upd1** (Chandramouli; Butcher, 2026), PDF: p. 7, "Rogue or shadow APIs: APIs that are defined for internal use (e.g., debugging, testing, ad hoc solutions [...]) may not be appropriately documented"; p. 20, "reconciliation between declared specifications, and live traffic [...] including shadow, orphan, and zombie API endpoints".
- **Bar-Yossef et al. (2004)**, PDF do autor: "We call such non-existent pages [...] 'soft-404 pages'"; hard-404 = "403, 404, or 410, or any code of the form 5xx"; o método requisita a página-pai + "25 random characters" e usa timeout de 10 s. Consequência: o 500 `{}` do vAPI **não** é soft 404 na definição original. A §1.4 agora diz que o trabalho **generaliza** o conceito.
- **Ware, Klein e Nelson (2011)**, arXiv 1102.0930: Jaccard "above 0.9" como critério de soft 404, precedente do limiar 0,90 (D5), com outra medida de similaridade.
- O OWASP API9:2023 não usa "shadow" nem "zombie" (confirmado em E37).

**Mudanças no artigo:**
- §1.3: termo *shadow* com fonte (NIST). As definições foram declaradas operacionais, com a divergência de *zombie* explicitada (NIST, Amoruso et al.). ⟦DECIDIR⟧ para o autor: manter ou renomear D\O.
- §1.4: origem do termo e do método, com a generalização declarada.
- **Seção 2 reescrita por inteiro:** protocolo de busca (Tabela 1), três blocos e síntese (Tabela 2), com a lacuna reformulada como **metodológica**. Os marcadores ⟦CONFERIR⟧ dependem da leitura integral de Amoruso et al.
- **Tabelas renumeradas:** as antigas 1, 1b, 2, 3 e 3b passaram a 3, 3b, 4, 5 e 5b.
- **Confronto com a literatura** em §7.2 (NIST, APICARV, RESTler), §7.4 (APICARV R = 0,56; Castagnaro et al.) e §7.8 (Bar-Yossef 5xx; APICARV OPTIONS/HEAD).
- §7.6: retirado o marcador sobre a vida útil da credencial. A busca não visou esse ponto, e afirmar ausência na literatura não seria sustentável.
- Introdução: lacuna de avaliação reescrita com Yandrapally et al. e Amoruso et al. ⟦CONFERIR⟧.

**Referências:** 9 entradas acadêmicas novas, com dados tirados do Crossref. Golmohammadi et al. foi citado como 2024 (fascículo impresso de 31/01/2024; online em 24/11/2023). A conferência cruzada citações × referências bate. A citação do Kiterunner, perdida na substituição da Seção 2, foi restaurada.

**Não usado, por não ter sido lido além do título ou do resumo, ou por ser periférico:** Mazhar et al. (2026, mutação de specs; candidato a reforçar a Metodologia depois de lido), RESTSpecIT, Prieto et al., Meneses et al. e a revisão da Computer Science Review 2026 (não conferida).

### E40 — 01:54 (18/11) · Auditoria independente das citações, correções e fechamento das pendências de texto

**Auditoria.** Um agente auditor, que recebeu só o artigo e nenhuma conclusão anterior, conferiu cada citação contra a fonte e cada entrada da lista contra o Crossref. Relatório em `docs/literatura/auditoria_citacoes.md`. Resultado: 58 verificações, nenhuma referência inexistente, lista ABNT correta e conferência cruzada fechando. **Todos os apontamentos foram reconferidos nos dados e nas fontes antes de aceitos.**

**Não procederam:**
- **Item 18:** o texto diz "cerca de 35 min nas demais"; a média das sete execuções sem erro do vAPI é 35,3 min.
- **Item 19:** a colisão `_debug` × `{username}` ocorreu 2 vezes, e não 3. O diferencial casa por (método, template) (`diff.py:97`), e na semente 1 o `GET /users/v1/{username}` também foi removido, então não havia template GET para colidir.
- **Item 29:** já resolvido.
- **Item 23 (parte):** a heurística *autojunk* não atua, porque o código usa `autojunk=False` (`responses.py:86`). O texto agora declara isso.

**Procederam e foram corrigidos (só texto e análise, nenhum código de medição):**
- **Castagnaro et al.:** "confirma a limitação de cobertura, origem de todos os FN" estava errado. O trabalho trata de eficiência, e a wordlist não é a única causa de FN. "Mostram" virou "partem da constatação".
- **Âncora (A13), afirmação errada em Resumo, Abstract, §7.1, §7.7 e Considerações:** "a queda decorre em sua maior parte" vale só para o VAmPI. Recalculado sem arredondamento: VAmPI 0,100/0,133 = **75%**; vAPI 0,167/0,367 ≈ **45%**. Os 77% do auditor vinham de valores arredondados.
- **D2Spec:** reescrito conforme o resumo do MSR ("in an evaluation on 64 APIs with pre-existing API specifications, D2Spec revealed many inconsistencies"). O número 21 do auditor vem da versão arXiv, que é outro texto.
- **A12:** "divergência em 10 pares" virou "em 1 de 10 pares".
- **Tabela 2:** EvoMaster = Sim (usa a definição OpenAPI); APICARV = descoberta parcial, guiada pela interface; Respector = subproduto.
- **§7.8:** "a literatura indica que não é raro" virou "o problema tem paralelos na literatura".
- **OPTIONS/HEAD:** os autores do APICARV tratam o caso como inconsistência da especificação. O texto diz isso e relaciona o comportamento à D11 sem chamá-lo de "respaldo externo".
- **Amoruso et al.:**
  - "não estava em acesso aberto" virou "não pôde ser obtido para esta análise". O OpenAlex marca acesso híbrido; o NSF PAR anuncia acesso livre em 01/09/2027; o download pela IEEE foi bloqueado nesta sessão.
  - "o único" passou a valer só entre os trabalhos revisados por pares, e os dois pré-prints sobre inferência a partir de tráfego estão declarados como não incluídos.
  - Os três ⟦CONFERIR⟧ foram removidos, e as afirmações se limitam ao resumo. **Correção de um exagero do assistente:** "detecção feita sem a especificação" virou "independente de especificações completas", que é o que o resumo diz.
- **APICARV:** "especificações tomadas como completas/verdade" virou "usadas como referência".
- **Contagem:** "dois endpoints reais" virou "dois caminhos (seis endpoints, contados por método)", conforme a D1.
- **Tabela 11 (vAPI, bruta × ajustada)** acrescentada, como a D9 exige: P bruta 0,28/0,33; F1 bruto 0,44/0,41; FP bruto 35 = 7 intrínsecos × 5.
- **Remissões:** zombies falsos remetem à §7.7, e não à §6.5; "ver abaixo" virou "ver acima"; A2 deixou de aparecer como "não manifestada".
- **Tabelas (ABNT):** todas as 18 tabelas do corpo foram numeradas em sequência (sem "b"), com título e linha de fonte.
- **difflib:** o algoritmo é "anterior e um pouco mais elaborado" que o de Ratcliff/Obershelp, e não "variante" dele.

**Referências:**
- **NIST:** citado como 2025 (o próprio documento: "June 2025, includes updates as of 03-13-2026").
- **Wazlawick:** a 3ª ed. (LTC) é de **2020**, conforme a ficha ABNT da Minha Biblioteca e a data da Amazon (10/11/2020). Estava 2021. Página omitida: em citação indireta, a NBR 10520 a torna opcional.
- **OWASP:** acrescentada a URL da página da API9.
- **Nuclei:** URL final após o redirecionamento.
- **Ware et al.:** marcado como relatório técnico.
- **Werkzeug:** o código do VAmPI (2.2.3, no contêiner) contém o mecanismo de PIN (`get_pin_and_cookie_name`, `WERKZEUG_DEBUG_PIN`). O texto declara a diferença de versão.
- **SecLists:** commit `6b19c2f5088c` identificado a posteriori. Os SHA-256 de `objects.txt` e `actions.txt` nesse commit coincidem com os registrados. Registrado em `ambiente_experimental.md`.

**Tabela 1 (protocolo):**
- O OpenAlex foi refeito com o filtro único `title_and_abstract.search` às 01h46. "undocumented endpoint" passou de 32 (outro modo de busca) para 8; nenhum dos 8 é relevante.
- O arXiv estava indisponível (HTTP 500) na repetição; as contagens são da primeira rodada, o que está declarado no texto.
- Criado `docs/protocolo_busca.md` como fonte do novo **Apêndice E**.

**Outras pendências fechadas:**
- Abstract final.
- §4.1 com parágrafo de abertura (o texto foi conferido contra `build_candidates`: candidatos = declarados, raiz, prefixos, variações de versão e wordlist aplicada à raiz e aos prefixos).
- Diagrama em texto substituído pela Figura 1.
- **Considerações finais escritas** (808 palavras, sem dados ou citações novos). "Implementação aberta" **não** foi afirmada, porque o código não está publicado.
- **Apêndice C** gerado do CSV por `sincronizar_apendices.py`. Só formata; as médias recalculadas a partir dele batem com todas as tabelas da Seção 6.

**Título (decisão do autor, 18/11):** as três opções originais foram julgadas longas. A escolhida é "Detecção de endpoints não documentados em APIs REST por análise diferencial: avaliação por degradação de especificação" (15 palavras: método, objeto e contribuição metodológica). Removida a legenda de marcadores do topo do rascunho; **nenhum marcador restante no texto**.

### E41 — 02:29 (18/11) · Conversão para Word adiantada

**Mudança de cronograma.** A conversão estava marcada para 27/11 e foi antecipada a pedido do autor. O arquivo gerado é `docs/artigo/artigo-tcc.docx`, com cópia em Downloads. O conversor e as instruções estão em `docs/artigo/ferramentas/`. O .md continua sendo a fonte única: o .docx é regenerado a partir dele.

**Formatação aplicada (manual, Anexo I):**
- A4, margens 3/3/2/2;
- Times New Roman 12, espaçamento 1,5, justificado, recuo de 1,25 cm;
- Resumo e referências em espaçamento simples;
- tabelas em fonte 10, espaçamento simples (padrão ABNT/IBGE), com legenda acima e fonte abaixo;
- número de página no canto superior direito.

**Verificações:**
- O validador de esquema do docx passou.
- O texto extraído do .docx não tem resíduo de Markdown nem marcadores.
- Os títulos de seção 1–7 e os apêndices A–E estão na ordem.

**Verificação visual feita depois que o autor instalou o LibreOffice.** O .docx foi convertido em PDF (`docs/artigo/artigo-tcc.pdf`, com cópia em Downloads) e as páginas foram inspecionadas em imagem.

Defeitos encontrados e corrigidos no conversor:
- colunas estreitas quebravam palavras ("A1/2", "Intern/a"). Agora cada coluna tem largura mínima suficiente para a maior palavra;
- legendas de tabela podiam ficar separadas da tabela. Agora ficam presas ao cabeçalho.

Corrigida também uma remissão errada na §6.2: a divergência de observação aponta agora para A12 e §7.7, e não para a §6.5.

**Contagem real (LibreOffice):**

| Parte | Páginas |
|---|---|
| Corpo (título → Considerações finais) | pp. 1–38 |
| Referências | pp. 39–40 |
| Apêndices | pp. 41–65 (65 no total) |

A estimativa geométrica anterior (~28 no corpo) ficou abaixo do real.

**Ajuste ao modelo do manual.** O autor estranhou o visual, e o Manual do TCC (`Downloads/Manual do TCC - Finalizado.pdf`) foi lido na fonte.
- **O formato está confirmado:** coluna única, Times/Arial 12, espaçamento 1,5, margens 3/3/2/2, no mínimo 20 laudas e Abstract obrigatório. É o modelo institucional, por isso difere de artigos de periódico.
- **O que divergia do modelo visual do Anexo I e foi corrigido:**
  - a abertura passou a ter título em caixa alta com subtítulo, nomes à direita e os rótulos "Resumo:", "Palavras-chave:", "Abstract:" e "Keywords:";
  - os elementos pré-textuais ficaram sem numeração ("devem ser numeradas a partir da primeira página da Introdução");
  - a Introdução passou a começar em página nova;
  - os títulos de seção seguem o estilo do modelo.
- **Contagem nova:** 67 páginas no total. Corpo nas pp. 1–39 (Introdução na p. 3), referências nas pp. 40–41, apêndices nas pp. 42–67.

**Estimativa de páginas** (geometria do layout, margem de cerca de ±15%):

| Parte | Páginas |
|---|---|
| Corpo (título → Considerações finais) | ~28 |
| Referências | ~2 |
| Apêndices (não contam nas 20 laudas) | ~22 |

### E42 — 02:52 (18/11) · Visual do Word e redução de páginas sem corte de conteúdo avaliado

**Pedido do autor:** visual "nada profissional" e 67 páginas, contra cerca de 35 esperadas. **Restrição:** não tirar nada que possa afetar a nota, só redundâncias e o que for desnecessário.

**Visual (só no conversor; o texto não muda):**
- Caminhos e trechos técnicos em fonte normal, em vez de Courier no meio das frases.
- Negrito de ênfase no meio dos parágrafos removido. Ficou só nos rótulos curtos de abertura, de até 5 palavras ("Problema.", "Comparação."), e nos cabeçalhos de tabela.

**Redundância medida, não estimada:**
- Os parágrafos foram comparados dois a dois entre seções, por similaridade de Jaccard acima de 0,42.
- **Nenhuma repetição dentro do corpo do artigo.**
- Todos os 7 pares quase idênticos estavam entre o **Apêndice B** e as Seções 3 e 5: questões de pesquisa, método, variáveis, métricas e escopo ético.

**Cortes:**
- **Apêndice B:** o corpo o cita apenas para o procedimento reprodutível (§5.4) e para as ameaças (§7.7). O apêndice passou a conter só essas duas partes ("Procedimento e ameaças à validade"), via `secoes()` em `sincronizar_apendices.py`. A validação A1–A13 continua fechando. `docs/protocolo_experimental.md` fica inteiro.
- **Apêndice E:** 76 linhas viraram 16, agrupadas por base, com todos os termos e totais preservados. A tabela inflada tinha sido montada pelo assistente.

**Resultado:** 57 páginas.

| Parte | Páginas |
|---|---|
| Artigo (abertura, corpo e referências) | pp. 1–41 |
| Apêndices | pp. 42–57 |

**O que não foi cortado:** o corpo, porque não tem repetição interna e qualquer corte ali mexe em conteúdo avaliado. Também os Apêndices A, C e D, todos citados pelo corpo (D1–D21, resultados por execução, hashes e verificação de equivalência).

### E43 — 03:00 (18/11) · Revisão externa do .docx: quatro defeitos, todos corrigidos

Revisão colada pelo autor e conferida no texto antes de aceita.

1. **Numeração da §4.3, que recomeçava em 1 nos itens 3 e 4.** No .md a lista estava certa (1–4). O defeito era do conversor: o parágrafo recuado depois do item 2 era tratado como parágrafo solto e reiniciava a numeração. Corrigido no `md2docx.js`: parágrafos recuados depois de um item viram continuação do item, e as listas começam no número escrito no .md.
2. **Apêndice E com 32 e 15, Tabela 1 com 8 e 1 ("undocumented endpoint", "zombie API").** A diferença vem dos modos de busca do OpenAlex (geral × título e resumo). Acrescentada nota explicativa em `docs/protocolo_busca.md`.
3. **A8 remetia à "seção 4.3".** Era a seção do protocolo original, que saiu do Apêndice B no enxugamento (E42). Agora remete à "Seção 3.5 do artigo", em `docs/protocolo_experimental.md`.
4. **Notação misturada.** A revisão dizia que só havia "§" em dois pontos; a contagem real era de 28 "§" contra 37 "Seção" no corpo. Tudo padronizado para "Seção".

**Resultado:** 57 páginas, sem mudança. Validação do docx OK. A §4.3 foi conferida em imagem.

### E44 — 03:33 (18/11) · Revisão guiada pelas práticas do vídeo de pesquisa: calibragem da precisão e confronto do soft 404

Aplicação ao artigo das práticas extraídas de `docs/video_claude_pesquisa_transcricao.md`, agora empacotadas na skill de projeto `.claude/skills/tcc/` (modos `referencias`, `revisar`, `banca`, `literatura`).

1. **Conferência citações × referências (item 8 do Anexo III).** Feita por script: os 28 itens da lista são citados no corpo, toda citação autor-data tem item correspondente, e os anos coincidem. Nenhuma correção necessária. Confirma o resultado de E40.
2. **Calibragem da precisão.** As Considerações finais (objetivo 3 e resposta à QP1) e o Resumo/Abstract (frase do vAPI) diziam "precisão de 1,00" sem "ajustada". A §7.1 já distinguia bruta e ajustada; o desencontro abria uma arguição fácil sobre D9. Corrigido para "precisão ajustada", com a faixa bruta (0,28–0,38) nas Considerações. Resumo passou a 478 palavras (limite 500).
3. **Confronto com a literatura na §7.3 (item 6 do Anexo III).** Acrescentado parágrafo: Bar-Yossef et al. (2004) tratam 5xx como *hard-404* e reservam a comparação com URL aleatória às respostas sem código de erro; no vAPI essa convenção descartaria rotas reais que falham com 500. Conferido em `docs/literatura/bloco_soft404_inventario.md` (texto completo lido, citação literal da definição de hard-404). A primeira redação dizia "o caso em que o servidor responde 200"; foi estreitada para "respostas sem código de erro", porque o algoritmo original também trata redirecionamentos.
4. **Verificado e mantido:** os números da Discussão e das Considerações (26 FN no VAmPI, 16 por wordlist; 32 e 31 endpoints no diferencial isolado; 6 ameaças manifestadas; 9 de 10 pares coincidentes) conferem com as seções de resultados. A parcela de ~45% da queda no vAPI atribuída a A13 e o contrafactual de 0,80 são grandezas distintas e ambas estão corretas no texto.

### E45 — 10:11 (18/11) · Formatação do artigo pelo modelo `main.pdf` (só estrutura)

Pedido do autor: adotar no .docx e no .pdf a estrutura de `main.pdf`, artigo de TCC do iCEV em abnTeX2 (outro tema, sem relação com este trabalho). Só a forma foi copiada, nenhum conteúdo. O modelo substitui o visual do Anexo I do Manual que o conversor seguia desde E41. Cópia de tudo como estava antes: `docs/artigo/_antes_modelo_main/`.

**Medido no `main.pdf`** (PyMuPDF, posições e fontes): logo do iCEV de 1,9 cm centralizada no cabeçalho de todas as páginas; título em negrito 18 pt e caixa alta; autores em 14 pt à direita, com notas de rodapé; resumo em 1,5 (passo de 18 pt); seção primária "1 INTRODUÇÃO" em 18 pt e caixa alta, secundária "2.1 Título" em 14 pt; legenda "Tabela N – ..." em 12 pt sem negrito; fonte da tabela centralizada em 10 pt; número de página no rodapé central a partir da página 2; Referências com título centralizado em página nova; Declaração de uso de IA depois das referências; anexos em página nova, com título em caixa alta.

**Mudanças:**
1. **Renumeração das seções** (decisão do autor): Introdução = 1, …, Discussão = 8, Considerações finais = 9. Feita por script: 117 alterações (títulos e remissões "Seção/Seções N.M", com S maiúsculo). Notas que remetem a outros documentos (CLAUDE.md, protocolo) foram puladas. "seção 8.3" de Manning ficou intacta. Também foram atualizadas as remissões ao artigo nas fontes dos apêndices: `protocolo_experimental.md` (Seção 3.5 → 4.5), `protocolo_busca.md` (Seção 2 → 3) e `sincronizar_apendices.py` (Seção 6 → 7). O roteiro da Introdução agora nomeia a Seção 9.
2. **Notas de rodapé dos autores** com a estrutura do modelo. E-mail e titulação do orientador ficam como `[PREENCHER]`, pois esses dados não estão no repositório.
3. **Declaração de uso de inteligência artificial**: rascunho factual para revisão do autor. Os modelos e a data ficam como `[PREENCHER]`. A nota de redação que pede a conferência não vai para o Word.
4. **`md2docx.js` reescrito** para o novo layout: logo, rodapé, títulos, notas de rodapé `[^id]`, legendas, filetes, apêndices em página nova. O título guarda-chuva "Apêndices" saiu, porque o modelo não tem. Um parágrafo terminado em ":" agora fica na mesma página da lista ou tabela que anuncia (havia um órfão na página 15). Detalhes em `docs/artigo/ferramentas/LEIAME.md`.

**Resultado:** 59 páginas (antes, 57). Os apêndices em página nova e os títulos maiores somam mais páginas do que a Introdução, agora sem quebra de página, poupa. Restam 5 campos `[PREENCHER]` no PDF. Sync dos apêndices OK (A1–A13 e D1–D21 sem pendência). O PDF foi conferido em imagem página a página contra o `main.pdf`. Nenhuma mudança em código de medição nem em dados.

**Correção (20/11):** as legendas das Tabelas 8, 9, 12 e 13 têm texto depois do negrito, como "(5 sementes por linha)". O padrão de legenda do conversor exigia que a linha terminasse no negrito, então essas quatro saíam como parágrafo de corpo, com "—" e sem centralizar. O padrão foi corrigido e as quatro agora seguem o modelo. Também ficou registrado, a corrigir no texto: as Tabelas 2 a 18 não são chamadas no corpo ("Tabela N"), só a Tabela 1.

**Ajuste fino pelas métricas do modelo (20/11).** Pedido do autor: reproduzir o `main.pdf` até nos detalhes. Medições lado a lado (PyMuPDF), modelo × nosso PDF:

| Elemento | Antes | Agora | `main.pdf` |
|---|---|---|---|
| Passo de linha do corpo e do resumo | 20,7 pt (1,5 do Word) | 18,0 pt | 17,9 pt (1,5 do abnTeX2) |
| Passo das referências / espaço entre itens | 13,8 / 25,8 pt | 14,5 / 24,0 pt | 14,5 / 23,8 pt |
| Passo do título / dos autores | 27,5 / 22,1 pt | 26,7 / 20,8 pt | 26,7 / 20,8 pt |
| Título de seção → texto (topo a topo) | 38,5 pt | 34,6 pt | 34,3 pt |
| Texto → título de seção | 45 pt | 40 pt | 40,2 pt |
| "Resumo:" → texto | 25,8 pt | 28 pt | 29,9 pt |
| Palavras-chave → "Abstract:" | 32 pt | 18 pt | 17,8 pt |
| Marca de nota junto ao nome do autor | 7 pt | 9,9 pt | ~10 pt |
| Nota de rodapé: marca na margem, texto recuado | marca colada ao texto | marca em x = 85, texto em x = 99 | idem |
| Número de página (topo da linha) | y = 803 | y = 816 | y = 817 |

Também: palavras-chave com inicial maiúscula e sem itálico, como no modelo. As informações que faltam passaram de `[PREENCHER]` para "(pendente)", a pedido do autor (5 ocorrências: e-mail do autor; titulação e e-mail do orientador; modelos de IA e data na Declaração). As marcas de nota usam 10 pt junto ao nome, 9 pt no corpo e 7,4 pt no rodapé. A biblioteca `docx` não expõe esse tamanho, então o ajuste é feito no XML gerado (via JSZip). **Resultado: 53 páginas** (antes, 59), por causa do passo de linha de 18 pt. A versão do conversor anterior a este ajuste está em `_antes_modelo_main/md2docx_v2_20nov.js`.

**Declaração de IA reescrita (20/11).** O autor perguntou se algo do `main.pdf` tinha sido copiado. A primeira versão da Declaração de uso de IA reproduzia quase literalmente a do modelo. Foi reescrita com redação própria e fatos deste trabalho: Claude Code e aplicativo Claude; código do `shadowscan`, testes e *scripts*; revisão do texto; conferência das referências; geração do documento. Também fica dito o que é do autor: pergunta de pesquisa, desenho, ambientes e interpretação. Verificação por script, com sequências de 8 palavras em comum entre os dois PDFs: restam só a fórmula institucional da nota do autor ("Graduando em Engenharia de Software pelo Instituto de Ensino Superior iCEV - PI. E-mail:") e o título da tese de Fielding (2000), referência que os dois trabalhos citam.

**Modelos na Declaração de IA (20/11).** O autor informou o Claude Opus 5. Os registros de todas as sessões do Claude Code neste projeto (`~/.claude/projects/C--dev-TCC/*.jsonl`) trazem um único identificador de modelo, `claude-opus-5-5` (Claude Opus 5.5), em 3.555 respostas. A Declaração cita os dois: "Claude Opus 5 e Claude Opus 5.5". O uso do Opus 5 no aplicativo Claude não pôde ser conferido em registro; a fonte é a informação do autor.

**Diferenças mantidas de propósito:** (1) referências em ABNT (sobrenome em caixa alta), embora o `main.pdf` use "Belcak, P."; (2) listas numeradas "1." em vez das alíneas "a)" do modelo, porque o texto remete a itens por número (ex.: "etapas 1 e 2" na Seção 5.1); (3) a fonte é Times New Roman, e o modelo usa Nimbus Roman, clone do Times no LaTeX. Por isso há pequenas diferenças de quebra de linha.

### E46 — 23/11 · Revisão do orientador: Tabela 2 vazia no PDF e nome do orientador

O orientador revisou o PDF e pediu que a revisão se concentrasse nas inconsistências do texto e na apresentação dos resultados. Esta entrada trata das duas primeiras correções pedidas.

1. **Tabela 2 aparecia só com os cabeçalhos (pp. 11–12).** As 8 linhas estavam no .md e no .docx: o `document.xml` tem os 9 `<w:tr>`, com RESTler a Respector. Quem as descartava era o LibreOffice, na conversão para PDF. A tabela começava no pé da página 11, as linhas tinham `cantSplit` (não se partem entre páginas) e o cabeçalho se repetia. Nessa combinação, o LibreOffice imprimia o cabeçalho na página 11, deixava as linhas de fora e abria a página 12 já na "Fonte". Isolamento por variantes do conversor, cada uma convertida e lida no PDF:
   - sem `cantSplit`: as linhas voltam, mas o próprio cabeçalho se parte entre as páginas 11 e 12;
   - sem cabeçalho repetido: as linhas continuam ausentes;
   - **adotado:** `keepNext` nos parágrafos de todas as linhas menos a última. A tabela fica num bloco só e, se não cabe no fim da página, vai inteira para a seguinte. Todas as 18 tabelas têm no máximo 12 linhas e cabem numa página.

   **Verificação:** um script comparou cada célula das 18 tabelas do .md com o texto do PDF. A Tabela 2 era a única com linhas ausentes, e com a correção nenhuma célula falta; os únicos alertas foram células com escapes de Markdown, que também batem no PDF anterior. A Tabela 2 foi conferida em imagem: completa na página 12, com legenda, cabeçalho, as 8 linhas, a fonte e a nota ¹.
2. **Nome do orientador:** corrigido para "Keoma de Sousa Coelho" (antes "Keoma De Sousa Coêlho"). É a única ocorrência no texto do artigo. A titulação e o e-mail continuam "(pendente)", a pedido do autor, para serem preenchidos ao final.

Nenhuma mudança em código de medição nem em dados.

### E47 — 23/11 · Revisão do orientador: critério de escopo (superfície HTTP × operações da API)

**Apontamento do orientador:** no VAmPI, `/console` e `/ui` eram apresentados como parte da API, enquanto as páginas HTML e o arquivo estático do vAPI eram ditos externos a ela. Ele pede que o texto diga se a análise abrange toda a superfície HTTP ou só as operações da API, e que o critério seja o mesmo nos dois ambientes.

**Diagnóstico:** a inconsistência estava só no texto. A medição já usava um critério único.
- A ferramenta não filtra nada: todo par (método, caminho) observado na URL base entra em O.
- Os intrínsecos dos dois alvos estão em `specs/vampi_intrinsecos.json` (6) e `specs/vapi_intrinsecos.json` (7) e são excluídos da mesma forma (Tabelas 10 e 11).
- O texto, porém, chamava `/console` e `GET /ui` de "caminhos da própria API", quando nenhum dos dois é rota da aplicação: o primeiro é servido pelo depurador do Werkzeug e o segundo pelo connexion. Ao mesmo tempo, dizia que os do vAPI ficavam "fora da API".
- Pela regra que se aplicava ao vAPI, os do VAmPI também ficariam fora. Pela que se aplicava ao VAmPI, os do vAPI ficariam dentro.

**Critério adotado:** a análise cobre a **superfície HTTP na origem da API** (esquema, host e porta da URL base). A origem de cada intrínseco (rota de API, rota web, componente do framework, arquivo estático) é descritiva e não muda o tratamento. Justificativas, no novo parágrafo "Escopo da análise" da Seção 4.3:
- a análise é caixa-preta, e separar o que "é API" do que não é exigiria julgamento manual do conteúdo de cada resposta;
- o risco da API9:2023 e do NIST está na exposição sem inventário, não no componente que serve a rota;
- o critério independe de a especificação ter sido escrita à mão ou derivada do roteador.

A alternativa, restringir o escopo às operações da API, foi descartada. Ela poria fora do escopo os 13 intrínsecos dos dois alvos, inclusive o `/console`, e exigiria um filtro que a ferramenta não tem. Os números medidos não correspondem a esse critério.

**Consequência para a QP4:** o enunciado ficou mais preciso, e o achado se mantém.
- Nos dois alvos, a descoberta não encontrou rota de API da aplicação ausente da especificação. A divergência está na superfície servida fora dessas rotas, na mesma origem da API.
- No VAmPI, a divergência inclui o console do depurador, com execução de código. No vAPI, são duas rotas web e um arquivo estático.
- A especificação do vAPI passa a ser descrita como "completa, por construção, quanto às rotas de API", e não como "completa".

**Alterações:**
- **Artigo:** Resumo e Abstract (frase do vAPI); Seção 4.3 (novo parágrafo de escopo); Seção 5 (naturezas das especificações); Seção 7.1 (VAmPI e vAPI); Seção 8.1 (QP2 e QP4); Considerações finais (objetivo 1).
- **Documentos:** `docs/decisoes.md` (D9 lista os intrínsecos dos dois alvos e o escopo; D16 deixa de dizer "não são API") e `docs/protocolo_experimental.md` (seção 2.1).

Nenhuma mudança em código nem em dados, e nenhum número do artigo se altera.

### E48 — 23/11 · Revisão do orientador: alcance do *ground truth* e afirmações sobre o `/console`

**1. "*Ground truth* exato".** A expressão sugeria que o procedimento conhece todos os shadows do alvo. Ele não conhece: G contém só as operações removidas da especificação. Os endpoints naturalmente não documentados ficam fora de G e só são tratados pelo levantamento com N = 0, que se limita ao que a descoberta observa. Um natural fora da cobertura não entra em G nem em I, e sua ausência do relatório não conta como FN.
- **Removida em 4 pontos:** Introdução, Seção 3.4 (comparação com Amoruso et al.), Seção 3.5 (lacuna, item 2) e contribuição 1. Nos quatro, passou a "conjunto de referência conhecido, formado pelas operações removidas da especificação".
- **Parágrafo novo na Seção 4.2,** "Alcance do conjunto de referência":
  - a revocação é medida sobre as operações removidas, não sobre todos os shadows do alvo;
  - os naturais seguem o tratamento da Seção 4.3;
  - as operações removidas podem não representar os shadows reais (A6).
- **Ajustes:**
  - a Seção 4.1 diz qual é o conjunto de referência;
  - o objetivo 2 das Considerações finais diz o que o conjunto não abrange;
  - na lacuna, "medir com exatidão" passou a "medir sobre um conjunto de referência conhecido".

**2. `/console`.** O experimento constatou que a interface do console do depurador está exposta (HTTP 200 e `<title>Console // Werkzeug Debugger</title>` aos cinco métodos). Não demonstrou execução de código, porque o PIN não foi testado. Afirmações que davam a execução como fato foram reescritas: o recurso de execução passa a ser atribuído à documentação (PALLETS, 2024), e o texto diz explicitamente que a execução não foi demonstrada.
- **Resumo e Abstract.** Para manter o resumo no limite, "e sem nenhuma remoção" saiu da frase do N = 0, e o Abstract foi ajustado em paralelo. O resumo ficou com 499 palavras pela contagem do script, que conta "—" como palavra.
- **Seção 7.1:** descrição do `/console`.
- **Seção 8.1:** QP4.
- **Seção 8.2:** parágrafo de abertura, que distingue exposição de exploração; o caso de Yandrapally et al. passa a "impacto potencial muito menor".
- **Considerações finais:** objetivo 1, QP4 e contribuição 3. A QP4 das Considerações também ficou coerente com E47: nenhuma especificação omitia rota de API, e nenhuma declarava toda a superfície.

Nenhuma mudança em código nem em dados.

### E49 — 23/11 · Revisão do orientador: perda de âncoras como estimativa contrafactual; "zombie" → "operação declarada não observada"

**1. Perda de âncoras (A13).** As porcentagens (cerca de 75% da queda no VAmPI e cerca de 45% no vAPI) eram apresentadas como efeito medido ("o efeito é mensurável", "0,10 decorre de", "respondeu por", "causou 8 dos 14 FN"). Na verdade, dependem de uma suposição não testada: a de que os endpoints ocultados junto com seu prefixo teriam sido encontrados se o prefixo permanecesse declarado.
- **O que se mediu:** quais FN ocorreram em endpoints cujo prefixo inteiro foi ocultado (3 no VAmPI, na semente 4 com N = 6; 8 dos 14 no vAPI).
- **O que se estimou:** a revocação contrafactual e a parcela da queda.
- **Apoio direto à suposição:** só o experimento natural de `api8/user/secret`.
- **Reescrito:** Resumo e Abstract; QP3 (Seção 8.1); Seção 8.4 (VAmPI e vAPI); Seção 8.7; QP3 das Considerações finais; A13 em `docs/protocolo_experimental.md`. Os números são os mesmos. O resumo não cresceu.

**2. "Zombie endpoint".** A definição operacional (D \ O, declarado e não observado) é o inverso do sentido das referências citadas: no NIST e em Amoruso et al. (2026), *zombie* designa algo obsoleto que **ainda responde**.
- **Novo termo:** "operação declarada não observada" em todo o texto próprio: Seção 2.3 (título, definição e justificativa), Seção 4.3, Seção 5 (etapas e falhas de rede), Seção 7.1, Seção 8.7, Discussão e Considerações finais. No protocolo: estrutura de `resultado.json` e A2.
- **Mantido:** as menções da literatura (NIST, Amoruso et al., título da Seção 3.4) e os termos de busca da Tabela 1 e do Apêndice E, porque usam o termo no sentido dos autores.
- **Código e dados:** ficam com o rótulo `zombie` (campo de `resultado.json`, saída do `shadowscan`) por causa do data freeze. O texto informa que é só o rótulo interno.

Nenhuma mudança em código nem em dados.

### E50 — 23/11 · Revisão do orientador: sentido do efeito do `/console` na precisão bruta, origem das ameaças e erros de rede

1. **"Precisão bruta, inflada pelos cinco métodos do `/console`" (Seção 8.7).** O sentido estava invertido. Os cinco métodos somam cinco FP na avaliação bruta, o que aumenta a contagem de FP e **reduz** a precisão. Corrigido.
2. **"Ameaças definidas a priori" (Seções 4.7 e 9).** Não procedia para todas. Pelo diário:
   - **A1–A9:** registradas no protocolo em E17 (17/11, 10:21), antes da bateria válida do VAmPI (E19, 10:24:36) e, portanto, antes de todos os dados usados no artigo;
   - **A10:** E22, defeito durante a coleta;
   - **A11:** E24, revisão do texto;
   - **A12:** E29, nos resultados;
   - **A13:** E32, nos resultados.

   **Correções:**
   - a Seção 4.7 separa as previstas das identificadas durante o desenvolvimento, com a origem de cada uma;
   - o objetivo 5 das Considerações finais diz que, das seis manifestadas, três são previstas (A1, A2, A3) e três (A10, A12, A13) foram identificadas justamente por terem se manifestado;
   - o protocolo, Seção 7 (Apêndice B), ganhou a mesma cronologia.
3. **Erros de rede (Seção 7.7).** Conferido em `runs/exp_vapi_principal/metricas_recalculadas.csv`:
   - os 39 erros estão em `n3_s1` (13), `n3_s3` (9) e `n3_s5` (17);
   - as três execuções têm revocação 1,00 e FP ajustado 0; os 7 FP brutos são os intrínsecos;
   - os tempos são 3124 s, 4119 s e 4156 s.

   **Problema no texto:** ele dizia "os erros não alteraram nenhuma métrica", o que vai além do que os dados mostram.

   **Nova redação:** as execuções mantiveram revocação 1,00 e nenhum FP ajustado na avaliação das operações removidas. Isso não permite afirmar ausência de efeito: uma requisição perdida pode ter reduzido a cobertura fora de G ou empobrecido a referência de soft 404. Na Seção 6.3, "seu efeito, verificado" passou a "seu reflexo nas métricas, verificado".

Nenhuma mudança em código nem em dados.

### E51 — 23/11 · Revisão do orientador: contagens da busca e alcance da completude da spec do vAPI

1. **Contagens da busca.** As bases (OpenAlex, arXiv, Semantic Scholar, Crossref) são atualizadas continuamente, então repetir uma consulta não garante o mesmo total. Removidas as afirmações "Repetir a consulta reproduz a contagem" (`docs/protocolo_busca.md`, Apêndice E) e "o que permite repetir cada consulta e obter a mesma contagem" (Seção 3.1). Agora o texto diz que o procedimento pode ser repetido, que os totais correspondem à data da consulta e que podem diferir em uma repetição. A Tabela 1 já trazia a data no título.
2. **Completude da spec do vAPI.** A spec foi gerada de `routes/api.php` (D16). Ela coincide, por construção, com as rotas desse arquivo, e não com "todas as rotas de API" nem com "o roteador" como um todo: rotas registradas por outros meios e o restante da superfície ficam fora.
   - **Artigo:** Resumo ("as rotas do arquivo que a originou"); Abstract; Seção 5 (naturezas das especificações, com a ressalva explícita de que a completude não se estende ao restante da aplicação); Seção 7.1; QP2 na Seção 8.1. A QP4 das Considerações finais deixou de afirmar que "nenhuma especificação omitia rota de API" e passou ao que foi observado: "a descoberta não encontrou rota de API da aplicação ausente".
   - **Documentos:** D16 em `docs/decisoes.md`; natureza da spec em `docs/ambiente_experimental.md` (Apêndice D).

Nenhuma mudança em código nem em dados.

### E52 — 23/11 · Revisão final do orientador: resumo, apêndices, referências, declaração de IA, disponibilidade e alcance das conclusões

Pedido do orientador: corrigir os pontos abaixo, sem nova bateria de experimentos, e garantir que as conclusões digam exatamente o que foi demonstrado.

1. **Resumo e Abstract enxugados** (limite do Manual: 150–500 palavras). Passaram de 495 para cerca de 320 palavras. Foram mantidas as ressalvas das revisões anteriores:
   - conjunto de referência = operações removidas;
   - precisão ajustada ≠ detecção completa;
   - perda de âncoras como estimativa contrafactual;
   - `/console`: exposição constatada, PIN não testado.

   Entrou "Não houve comparação experimental com outras ferramentas". Saíram, por economia, a autenticação e a contagem de caminhos intrínsecos, que continuam no corpo.
2. **Orientação interna removida dos apêndices**, nas fontes, porque o sync sobrescreve o artigo:
   - `decisoes.md`: "Vai direto para a Metodologia… perguntas prováveis da banca"; "(explicitado em 23/11, E47)"; "(escopo congelado)"; "(E13, FN 2)";
   - `protocolo_experimental.md`: "ver ambiente_experimental.md"; "Seção 4.5 do artigo";
   - `ambiente_experimental.md`: "Alimenta a subseção… deve gerar nova entrada no diário"; remissão a `protocolo_experimental.md`; "briefing §4";
   - `protocolo_busca.md`: "Fonte do Apêndice E (sincronizado por…)"; "mantido pelo autor e pode ser apresentado à banca", que passou a remeter ao repositório.
3. **Referências.** Conferência por script nos dois sentidos: os 28 itens da lista são citados no corpo, e toda citação autor-data tem item com o mesmo ano. Os 4 "sem item" apontados pelo script são coautores de citações com vários autores (BUTCHER, G0TMI1K, MAURER, POLISHCHUK), lidos isoladamente pelo parser. Nenhuma correção necessária.
4. **Modelos da declaração de IA.** Os 6 registros de sessão do Claude Code neste projeto (`~/.claude/projects/C--dev-TCC/*.jsonl`) trazem um único identificador, `claude-opus-5-5` (Claude Opus 5.5), em 2.214 respostas. O E45 contava 3.555, provavelmente com registros que já não estão na pasta. O Claude Opus 5 continua por informação do autor e não pode ser conferido em registro. A declaração passou a mencionar também a preparação do repositório.
5. **Disponibilidade.**
   - **Repositório:** git inicializado em `C:\dev\TCC`, para publicação como repositório público no GitHub (decisão do autor).
   - **`.gitignore`:** exclui ambiente local, ferramentas internas (`.claude/`, `CLAUDE.md`, `graphify-out/`), arquivos de contexto, status e briefing, a transcrição de vídeo, o artigo (até a defesa), os scripts de uso único `experiments/_*.py` e `sincronizar_apendices.py`, e o clone do vAPI. O override do vAPI foi copiado, idêntico (hash conferido), para `envs/vapi_config/`.
   - **Generalizado antes da publicação:** os nomes de containers de outros projetos do autor (`ambiente_experimental.md`, este diário) e um caminho temporário com o nome de usuário (`docs/literatura/bloco_2_2_inferencia_conformidade.md`).
   - **Tokens:** os `eyJ…` em `spec_degradada.yml` são o token de exemplo da própria spec do VAmPI.
   - **README:** reescrito com o conteúdo do repositório e os passos de reprodução (VAmPI por digest; vAPI pelo commit + override).
   - **Artigo:** Seção 6.5 nova, com o conteúdo e o modo de recalcular as tabelas sem tocar nos alvos. O URL fica como marcador até o repositório ser criado.
   - **Testes:** 19/19 OK.
   - **Publicado:** https://github.com/lcsp14/shadowscan (público, branch `main`, commit `43bd205`, 214 arquivos). Os commits usam o e-mail *noreply* do GitHub (`user.email` configurado só neste repositório), a pedido do autor, para não expor o e-mail pessoal. O URL entrou na Seção 6.5.
6. **Alcance das conclusões.**
   - **QP1 (Seções 8.1 e 9) e objetivo 3:** "precisão 1,00" passou a "precisão ajustada", com a explicação de que significa ausência de FP ajustados, e não detecção completa.
   - **Seção 8.2:** "a etapa diferencial não é redundante com as ferramentas existentes" virou argumento analítico explícito: nenhuma outra ferramenta foi executada nos mesmos alvos.
   - **Seção 8.8 e Limitações:** declaram que não há comparação experimental nem superioridade estabelecida.

Nenhuma mudança em código de medição nem em dados.

### E53 — 23/11 · Remissão de todas as tabelas no corpo e data da declaração de IA

1. **Tabelas 2 a 18 sem remissão no corpo.** A falha já estava registrada em E45 (20/11): só a Tabela 1 era chamada no texto, e a ABNT pede que toda tabela seja referida. Não foi apontada pelo orientador; entra no pedido geral dele de corrigir "inconsistências do texto e apresentação dos resultados". Cada tabela recebeu remissão:
   - **Frase de abertura** nas seções que começavam direto pela tabela: 3.5 (Tabela 2), 6.3 (Tabela 6), 7.2 (Tabelas 8 e 9), 7.3 (10 e 11), 7.4 (12 e 13), 7.6 (16) e 7.7 (17 e 18).
   - **Remissão no parágrafo que anuncia a tabela:** Tabelas 3, 4, 5, 7, 14 e 15.

   **Verificação:** script confirma que as 18 tabelas são chamadas no corpo. Nenhum número mudou.
2. **Data da declaração de IA:** "17 de novembro" passou a "23 de novembro de 2026", data da versão final.

Permanece pendente só a nota do orientador (formação, titulação e e-mail), que o autor preencherá.

### E54 — 23/11 · Nota de rodapé do orientador

Nota do orientador preenchida com os dados que ele forneceu: graduações, especializações, MBA, mestrado em andamento (UFPI) e e-mail institucional. Segue o formato do `main.pdf` (formação, depois e-mail). Instituição e ano das graduações e especializações não foram informados, então não aparecem. Saem as marcações "(pendente)". O PDF tem 58 páginas.

Revisto no mesmo dia: o orientador pediu só "Esp. Keoma de Sousa Coelho" na linha de autoria, sem nota de rodapé. A nota foi retirada, e o artigo fica com uma única nota, a do autor.

### E55 — 25/11 · Resumo e Abstract: endpoints da API × superfície HTTP exposta

**Pedido:** diferenciar, no Resumo e no Abstract, os endpoints da API da superfície HTTP exposta.

**Conferência:** procede. O corpo já separa as duas coisas:
- **Seção 4.3 e D9:** o escopo é a superfície HTTP na origem da API (esquema, host e porta), não só as rotas de API;
- **D16:** a spec do vAPI cobre só `routes/api.php`;
- **QP4 e Considerações finais:** nenhuma rota de API da aplicação ficou fora das specs; a divergência está fora dessas rotas.

O Resumo falava só em "superfície exposta" e apresentava o `/console` sem dizer que é componente do framework, o que permitia ler o achado como rota de API não declarada. Além disso, "endpoints não declarados já presentes nas especificações originais" se contradiz: os intrínsecos respondem no alvo e não constam da spec.

**Alterações, no Resumo e no Abstract:**
1. **Primeira frase:** define a superfície HTTP exposta na origem da API como as rotas da API mais rotas web, componentes do framework e arquivos estáticos.
2. **Precisão:** "endpoints não declarados já presentes nas especificações originais" passou a "endpoints que já respondiam nos alvos sem constar das especificações originais".
3. **Achado:** antes dele entra o resultado da QP4 (nenhuma rota de API não declarada nos dois alvos; a divergência está fora dessas rotas). O console do Werkzeug passa a ser qualificado como componente do framework.

**Tamanho:** o Resumo passou para 363 palavras e o Abstract para 341, dentro do limite de 150–500.

Nenhuma mudança em código, dados ou números.

### E56 — 25/11 · Ameaça A14: aperfeiçoamento da ferramenta durante os experimentos

**Pedido:** reconhecer na Metodologia, como limitação, o aperfeiçoamento da ferramenta durante os experimentos.

**Conferência:** procede. A Seção 8.6 apresentava as correções D10, D18, D19, D20 e D21 só como mérito ("a validação como instrumento de detecção de defeitos"), sem registrar o custo. Todas foram motivadas por erros observados em execuções do VAmPI (E08, E13/E18, E22, E27), e a bateria definitiva do VAmPI foi refeita depois delas, no mesmo alvo. Nenhuma ameaça entre A1 e A13 cobria isso.

**Verificações:**
- **Código congelado antes do vAPI:** os SHA-256 atuais dos 9 arquivos de `shadowscan/` coincidem com a tabela de `ambiente_experimental.md` §2.1 (código final da bateria do VAmPI, E27). O vAPI (E35) rodou com esse código, e nada mudou depois.
- **Dimensão do ajuste**, medida nos dados substituídos (`runs/_substituidas/exp_vampi_principal_v3_pre_D20_D21/resultados.csv`, sem auth, código anterior a D20 e D21):
  - 4 de 10 execuções com FP ajustados (n3_s5: 2; n6_s1, n6_s2 e n6_s5: 3 cada; 11 no total);
  - precisão ajustada de 0,50 a 0,62, média de 0,83 (versão final: 1,00 em todas);
  - revocação idêntica (12/15 com N = 3 e 20/30 com N = 6, as mesmas da versão final em `runs/exp_vampi_principal/resultados.csv`).
- **Correções de regra geral:** nenhuma usa caminho, palavra ou resposta próprios do VAmPI. A exceção é o intervalo de 45 s da D19, escolhido pela validade de 60 s do token do VAmPI, que só atua com auth (o vAPI não usa auth).

**Alterações:**
1. **`protocolo_experimental.md`:** nova ameaça **A14** (interna), com as mitigações (correções gerais, uma única versão do código, vAPI como replicação com código congelado), a dimensão medida do ajuste e o efeito residual. O texto de abertura passa a "A10–A14". O Apêndice B é regenerado pelo sync.
2. **Artigo, Seção 4.7:** "as quatro seguintes" passa a "as cinco seguintes", com um parágrafo sobre a A14.
3. **Artigo, Seção 8.6:** frase final remete o lado negativo à A14.
4. **Artigo, Seção 8.7:** novo item em "Ameaças que limitam o alcance", com a dimensão medida e o papel do vAPI.
5. **Artigo, Seção 9, objetivo 5:** "treze ameaças… quatro identificadas" passa a "quatorze… cinco".

Nenhuma mudança em código, dados ou resultados reportados. A dimensão do ajuste vem de dados já coletados.

### E57 — 25/11 · Discussão da A1 nos dois ambientes

**Pedido:** corrigir a discussão da ameaça A1 (Seção 8.7), considerando os dois ambientes.

**Conferência:** procede. O item tratava só do VAmPI ("dois caminhos reais (seis endpoints)… precisão bruta 0,28–0,38") e estava sob "se manifestaram e foram medidas", sem citar o vAPI. Na Seção 7.3 e na Tabela 11, porém, a A1 também se manifesta no vAPI. Como o vAPI tem especificação derivada do roteador, a omissão sugeria que a A1 seria problema só de spec escrita à mão, e isso é falso.

**Verificação em `runs/exp_*_principal/metricas_recalculadas.csv`:**

| Alvo | N | Execuções | FP bruto por execução | FP ajustado | P bruta (média) | P ajustada |
|---|---|---|---|---|---|---|
| VAmPI | 3 | 10 | 6 em todas | 0 | 0,283 | 1,00 |
| VAmPI | 6 | 10 | 6 em todas | 0 | 0,381 | 1,00 |
| vAPI | 3 | 5 | 7 em todas | 0 | 0,284 | 1,00 |
| vAPI | 6 | 5 | 7 em todas | 0 | 0,325 | 1,00 |

A diferença entre FP bruto e ajustado é exatamente o número de intrínsecos de cada alvo (`specs/vampi_intrinsecos.json`: 6; `specs/vapi_intrinsecos.json`: 7) em todas as execuções.

**Alterações:**
1. **Artigo, Seção 8.7, item da A1:** reescrito para os dois alvos, com as precisões brutas de cada um. Diz que a divergência está na superfície HTTP na origem da API, e não em rotas de API, e que o vAPI mostra que a ameaça independe de a spec ser escrita à mão (D16).
2. **`protocolo_experimental.md`, A1:** acrescentado onde ela se manifestou nos dois alvos (no mesmo formato da A2). O Apêndice B é regenerado pelo sync.

Nenhuma mudança em código, dados ou números.

### E58 — 25/11 · Considerações finais: "APIs reais" → "aplicações de referência"

**Pedido:** substituir "APIs reais" por "aplicações de referência" na conclusão.

**Conferência:** procede. Na contribuição 1 da Seção 9 constava que o método "produz, a partir de APIs reais, um conjunto de referência conhecido". Os dois alvos são aplicações deliberadamente vulneráveis e didáticas (A5), e a Seção 8.8 nega expressamente afirmações sobre APIs reais. A frase prometia mais do que foi demonstrado. Ficou "a partir de aplicações de referência", coerente com o título da Seção 6.1 ("Ambientes de referência").

**Outras ocorrências conferidas e mantidas:**
- **Seção 1:** "o conjunto verdadeiro de shadow endpoints de uma API real é desconhecido";
- **Seção 8.4 e A13:** "em uma API real, são independentes";
- **Seção 8.8:** "não sustentam afirmações sobre a prevalência… em APIs reais".

Nas três, "API real" designa justamente o que *não* foi testado (API em produção, em contraste com a degradação controlada), e o uso está correto.

Nenhuma mudança em código, dados ou números.

### E59 — 25/11 · Commit da versão final no GitHub (tag `v1.0-tcc`)

**Pedido:** identificar o commit do GitHub que corresponde à versão final do trabalho.

**Conferência:** procede. A Seção 6.5 citava só o URL do repositório, e `main` continua recebendo commits (E52–E58). Sem um commit fixo, quem clonar depois da defesa não tem garantia de ver a versão que acompanha o artigo.

**Defeitos encontrados no Apêndice D ao conferir os hashes do commit contra `ambiente_experimental.md` §2.1:**
1. **`run_experiments.py` com hash desatualizado.** A tabela trazia `75E8D7EEC1D091EB`, gravado em E27. O arquivo mudou em 17/11 às 13:56 (opção `--retomar`, E33), já durante a bateria do vAPI. A versão final, que é a publicada, tem `694B780D896B0C2C` na cópia de trabalho. A mudança não altera a medição, e a nota ¹ agora a registra.
2. **Fim de linha.** `__main__.py` e `run_experiments.py` estão com CRLF na cópia de trabalho (Windows, `core.autocrlf=true`), e o Git os guarda com LF. Em um clone, os hashes são `57E7883E75FAA620` e `FA55E47BCC969365`. O conteúdo é idêntico após normalizar o fim de linha (conferido byte a byte). A nova nota ³ registra isso.

Os outros 9 arquivos da tabela têm o mesmo hash na tabela, no disco e no commit.

**Verificações:** 19/19 testes OK (`python -m unittest discover tests`).

**Alterações:**
- **`ambiente_experimental.md` §2.1:** notas ¹ (`--retomar`) e ³ (CRLF/LF).
- **Artigo, Seção 6.5:** passa a citar o hash completo do commit e a tag `v1.0-tcc`, com a observação de que o código da ferramenta nesse commit é o mesmo que gerou as execuções.
- **Tag anotada `v1.0-tcc`** criada no commit que contém esta entrada e publicada no GitHub. O hash fica registrado no artigo (Seção 6.5) e na tag, e não aqui, porque esta entrada faz parte do próprio commit.

Nenhuma mudança em código, dados ou números.

### E60 — 25/11, 09:56 · Revisão de referências, ortografia e padronização

**Pedido:** revisar referências, ortografia e padronização do documento.

**Método:** a conferência das referências foi feita por script descartável. A leitura de ortografia e padronização foi dividida em três trechos (Seções 1–4, Seções 5–9, declaração e apêndices), por leitores independentes que só reportaram. Cada apontamento foi conferido no arquivo e no PDF antes de ser aplicado. Os erros dos apêndices foram corrigidos nos arquivos-fonte, e o sync regenerou os apêndices.

**1. Referências.** Os 28 itens da lista são citados no corpo, e toda citação autor-data tem item correspondente, com o mesmo ano. Os nomes fora da lista que o script encontrou são categorias OWASP (API1, API3, API7), nome de ferramenta (APICARV) e a forma narrativa "Bar-Yossef et al.". Os itens estão em ordem alfabética, no formato NBR 6023. Única correção: no item do `difflib`, o subtítulo passou a ser separado por dois-pontos, e não por travessão. O subtítulo interno "Referências conferidas" e a nota de redação não saem no Word (conferido no PDF).

**2. Ortografia e gramática (corpo):**
- "micro-média" passou a "micromédia";
- "desvio padrão" passou a "desvio-padrão", forma do VOLP (também em `protocolo_experimental.md`);
- regência: "os frameworks os respondem" passou a "respondem a eles";
- "classificá-lo errado" passou a "classificá-lo incorretamente";
- "Três delas são previstas" passou a "haviam sido previstas";
- "e mostrou que" passou a "e mostra que", para concordar no tempo verbal;
- ordem das palavras: "trabalhos revisados por pares localizados" passou a "trabalhos localizados que foram revisados por pares";
- "pré-prints" passou a "preprints";
- hífen com espaços passou a meia-risca em "iCEV – PI" e "Teresina – PI";
- dois parágrafos de texto final que estavam inteiros em itálico (Seção 8.2, "Com esse enquadramento…"; abertura da 8.7) passaram a redondo;
- **Abstract:** "the API9:2023 category of", "on VAmPI… on vAPI… operations removed, respectively" e "discovery and differential components".

**3. Ortografia e linguagem interna (fontes dos apêndices):**
- `decisoes.md`:
  - "não-admin" passou a "não administrador";
  - "fim-a-fim" passou a "fim a fim";
  - artigo acrescentado em "O vAPI é executado";
  - caixa-alta usada como ênfase (NOME, MESMO, E, DECLARADOS, NÃO, REAIS) passou a negrito;
  - "≥4 dígitos e hex ≥8" escrito por extenso;
  - "nº" passou a "número";
  - "~3.300" passou a "cerca de 3 300";
  - "33 operações = 33 declarações" passou a frase;
  - "sem auth" passou a "sem autenticação";
  - "offline" passou a "sem nova execução";
- `protocolo_experimental.md`:
  - "multi-método" passou a "multimétodo";
  - "pegam o banco no meio da recriação" passou a "encontram o banco em recriação";
  - "→ trabalho futuro" passou a "fica como trabalho futuro";
  - "auth" passou a "autenticação";
  - "fim-a-fim" passou a "fim a fim";
- `protocolo_busca.md`:
  - "anti-robô" passou a "antirrobô";
  - saiu "(item visto no resultado da #16)";
  - a linha de buscas dirigidas com termos truncados e "(n/a)" foi reescrita por extenso;
- `ambiente_experimental.md`:
  - "(ver diário, E07)" passou a "(diário de pesquisa, E07)";
  - "16 hex" passou a "16 caracteres hexadecimais";
- `experiments/sincronizar_apendices.py`, Apêndice C (o CSV não foi alterado):
  - o valor "nao" passou a "não";
  - o cabeçalho "Auth" passou a "Autent.", com a legenda explicando;
  - separador de milhar nas requisições e no tempo.

**4. Padronização:**
- **Notação:** "N=0" passou a "N = 0" nos apêndices, como no corpo (blocos de código mantidos).
- **Separador de milhar com espaço**, como no corpo ("46 291"): "4000" passou a "4 000"; "3291" passou a "3 291"; e 22 totais do Apêndice E, que usavam ponto, passaram a usar espaço.
- **Siglas expandidas na primeira ocorrência do corpo:** REST (*Representational State Transfer*), NIST, OWASP, BOLA e BOPLA. A expansão repetida na Seção 2.1 saiu.
- **Tabelas da Seção 7:**
  - a nota sobre "±" e somas, antes repetida de forma desigual em algumas legendas, virou uma frase única no início da 7.2, com as legendas limpas;
  - Tabelas 12 e 13 com o mesmo título e os mesmos cabeçalhos;
  - "Erros de rede (soma)" nas Tabelas 17 e 18;
  - o pseudotítulo "**Custo no vAPI**" virou frase;
  - "**vAPI:**" passou a "**vAPI.**", como nos demais blocos.
- **Itálico** (decisão do autor: termos técnicos sem itálico):
  - endpoint, shadow, zombie, template, wordlist, baseline, framework, token, hash, commit, script, timeout, digest, proxy, middleware, threads, workers, tag, flag, soft 404, hard-404 e ground truth ficam em redondo (61 ocorrências alteradas no corpo; as fontes dos apêndices já estavam assim);
  - latinismos em itálico (*a priori*, *a posteriori*);
  - trechos citados em inglês continuam em itálico (*rogue or shadow APIs*, *zombie or deprecated APIs*, *soft-404 pages*);
  - a convenção está declarada em nota de rodapé na definição de shadow endpoints (Seção 1).

**Não alterado, por decisão fundamentada:**
- "em um/uma" × "num/numa": as duas formas são corretas;
- "(MANNING; RAGHAVAN; SCHÜTZE, 2008, seção 8.3)": a localização por seção identifica o trecho numa obra sem paginação única online;
- "rota-coringa": grafia registrada;
- formato de horários nos apêndices (10:21): é o registro técnico do diário.

**Páginas:** o PDF tinha 59. A primeira versão desta revisão foi a 61, por causa das notas repetidas nas legendas e dos cabeçalhos longos copiados para a Tabela 13. A nota única na Seção 7.2 e os cabeçalhos curtos devolveram o corpo à página 40 (Referências na 41).

Nenhuma mudança em código de medição, dados ou números.

### E61 — 25/11 · Tag `v1.0-tcc` movida para a versão de entrega

O autor confirmou que E55–E60 encerram as exigências para a entrega. A tag `v1.0-tcc` (E59) apontava para um commit anterior à revisão E60, que alterou os arquivos-fonte dos Apêndices A, B, D e E. A tag foi movida para o commit que contém esta entrada, e o hash na Seção 6.5 do artigo foi atualizado. Pelo mesmo motivo de E59, o hash não é registrado aqui, porque esta entrada faz parte do próprio commit. O código da ferramenta e os dados de `runs/` são os mesmos (hashes do Apêndice D conferidos em E59, sem alteração desde então).

### E62 — 25/11, 15:25 · Trabalho reformatado como monografia (Anexo II do Manual)

O autor foi informado de que o trabalho, pelo tamanho, deve ser entregue como **monografia**, e não como artigo. O Manual do TCC aceita os dois formatos: artigo com no mínimo 20 laudas, monografia com no mínimo 40 laudas contando os elementos pré-textuais. Modelo seguido: "Modelo Monografia TCC 2025.2.doc" (Anexo II).

Mudanças de formato, feitas por um conversor novo, `docs/artigo/ferramentas/md2docx_monografia.js`, que gera `monografia-tcc.docx`/`.pdf` em duas passadas com `gerar_monografia.ps1`. O conversor do artigo, `md2docx.js`, continua igual. O .md continua sendo a fonte única.

- **Elementos pré-textuais**, sem número de página: capa, folha de rosto, folha de aprovação, Resumo e Abstract em páginas próprias e Sumário.
  - A folha de rosto diz: "Bacharel em Engenharia de Software da Escola de Tecnologia Aplicada do Instituto de Ensino Superior - iCEV" (escola informada pelo autor).
  - O orientador é o Esp. Keoma de Sousa Coelho.
  - Na folha de aprovação a data fica em branco, para ser preenchida na defesa.
- **Resumo e Abstract**: espaço simples, rótulo centralizado; palavras-chave em itálico, como pede o modelo.
- **Sumário**: números de página medidos no PDF da primeira passada por `paginas_sumario.py`.
- **Corpo**:
  - Times 12, espaçamento 1,5 do Word, sem espaço entre parágrafos, recuo de 1,25 cm, margens 3/3/2/2;
  - cada capítulo começa em página nova, com o título no formato "1. INTRODUÇÃO" (negrito, 14 pt) e os subtítulos como "2.1. Título";
  - a faixa do iCEV do modelo vai no cabeçalho;
  - o número de página segue a ABNT (NBR 14724), a pedido do autor: canto superior direito, a 2,45 cm da borda, logo abaixo do símbolo do iCEV na faixa, a partir da Introdução, contando desde a capa.
- A nota de rodapé do autor (formação e e-mail) saiu, porque esses dados estão na capa e na folha de rosto.

Mudanças de texto, todas de designação:

- "neste/este artigo", "O artigo está organizado" e "tabelas deste artigo" passaram a "trabalho" (Seções 1, 4.7, 6.5 e 9);
- nas fontes dos Apêndices B e E (`protocolo_experimental.md` e `protocolo_busca.md`), "no artigo" e "do artigo" passaram a "neste trabalho" e "deste trabalho". Os apêndices foram ressincronizados.

**Páginas:** 75 no total. A Introdução começa na página 8, as Considerações finais terminam na 53 e as Referências começam na 54 (corpo: 46 páginas). O mínimo de 40 laudas foi atendido com folga.

Nenhuma mudança em código de medição, dados ou números.

**Tag.** Com autorização do autor, a tag `v1.0-tcc` foi movida para o commit que contém esta entrada, porque os arquivos-fonte dos Apêndices B e E mudaram. O hash na Seção 6.5 foi atualizado. Como em E59 e E61, o hash não é registrado aqui. Código e dados de `runs/` não mudaram.

### E63 — 26/11, 14:00 · Correções de forma apontadas por avaliação independente

Um avaliador independente (subagente que recebeu só o PDF da monografia e o Roteiro de Avaliação) estimou a parte escrita em 7,1 de 8,0, a mesma estimativa da avaliação anterior. Cada apontamento foi conferido no texto antes de ser aceito.

**Aplicado:**
- Referência **MENESES, FURUTA e SHIPMAN (2012)** incluída na lista: o item era citado no Apêndice E sem constar das Referências. Só os metadados confirmados em `literatura/bloco_soft404_inventario.md` (autores, título, evento, editora, p. 197-208, DOI); local do evento e volume da série ficaram de fora por não terem sido conferidos em registro bibliográfico. No Apêndice E (`protocolo_busca.md`), "NIST SP 800-228" passou a ser citado como Chandramouli e Butcher (2025).
- Convenção D## (Apêndice A) e A## (Apêndice B) explicada no último parágrafo da Introdução, porque os códigos aparecem a partir da Seção 2.
- Ressalva do PIN retirada da Seção 8.1 (QP4) e do item 3 das contribuições (Seção 9). Permanece no Resumo, no Abstract, na Seção 7.1, na Seção 8.2 e no objetivo 1 das Considerações finais.
- Conversor (`md2docx_monografia.js`): em tabela mais larga que a mancha, colunas estreitas mantêm a largura mínima e só as largas encolhem. Corrige a quebra "A1/0" na coluna Id da tabela de ameaças (Apêndice B).

**Não aceito:** "p. 748758" (o hífen existe; some só na extração de texto do PDF); Ratcliff e Obershelp sem referência (a menção já é atribuída à documentação do `difflib`, PYTHON SOFTWARE FOUNDATION, 2026); folha de aprovação sem banca e ficha catalográfica (o modelo do iCEV não as traz).

Monografia regenerada: 75 páginas, Introdução na p. 8. Nenhuma mudança em código de medição, dados ou números.

### E64 — 26/11, 14:03 · Citações no texto com sobrenome em maiúsculas e minúsculas

A pedido do autor, as citações autor-data no corpo e nos apêndices passaram da forma em caixa alta (SILVA, 2026) para a forma com só a inicial maiúscula (Silva, 2026), como manda a NBR 10520:2023. Foram 65 trocas dentro de parênteses com ano. Siglas e nomes próprios em sigla ficaram como estão (OWASP Foundation, ZAP, APICARV, OpenAPI Initiative, ProjectDiscovery). A lista de Referências mantém o sobrenome em caixa alta, conforme a NBR 6023. Monografia regenerada: 75 páginas. Nenhuma mudança em código, dados ou números.

**Tag.** Com autorização do autor, a tag `v1.0-tcc` foi movida para o commit que contém esta entrada, que inclui as mudanças de E63 (Apêndice E) e E64. O hash na Seção 6.5 foi atualizado. Como em E59, E61 e E62, o hash não é registrado aqui. Código e dados de `runs/` não mudaram.

### E65 — 27/11, 15:19 · Correções da professora na monografia revisada

A professora devolveu a monografia (PDF "monografia- Lucas - Revisado") com 8 comentários digitados e marcas manuscritas nas páginas 8 a 52. As marcas foram transcritas página a página e cada uma conferida no texto-fonte antes de aplicada.

**Forma (no conversor `md2docx_monografia.js`):** sem ponto depois do indicativo numérico das seções ("2.2 OWASP", "1 INTRODUÇÃO"), conforme a NBR 6024; listas com marcador ou número passaram a alíneas a), b), c).

**Texto (cerca de 50 trechos):**
- travessões de intercalação marcados trocados por vírgulas;
- siglas HTTP, URI, JSON e YAML com o nome por extenso na primeira ocorrência;
- conectivos e sujeitos explícitos acrescentados ("Convém notar que", "Já o", "Além disso", "Em suma", "Essa circularidade", "Os autores relatam", "Contudo");
- tempo verbal ("requisitaram", "compararam");
- datas por extenso na Seção 3.1 ("18 de novembro de 2026, à 1h46");
- seis parágrafos divididos onde ela indicou;
- os dois resultados do APICARV passaram de lista a parágrafos;
- a nota da Tabela 2 passou a "Nota:";
- "tipo metodo" passou a "tipo método";
- a frase "A precisão reportada é a ajustada." foi retirada da Seção 8.1;
- as definições de precisão e revocação foram reescritas com a redação sugerida por ela;
- o itálico de health check, testbed e gateways foi retirado, conforme a nota 1; "potential inconsistency" passou a itálico, por ser citação em língua estrangeira.

**Rótulo "Comparação.":** ela perguntou se era um marcador textual. Depois de esclarecida a função (abre o trecho em que o trabalho se compara com os autores apresentados), disse ao autor que o rótulo pode ficar como estava; foi mantido.

Monografia regenerada: 75 páginas, Introdução na p. 8. Nenhuma mudança em código, dados ou números.

### E66 — 27/11, 15:33 · Declaração de IA ajustada; anexos com as declarações assinadas

**Declaração de uso de IA.** Por decisão do autor, "como apoio à revisão da clareza e da coesão textual" passou a "como apoio à redação e à revisão do texto", para descrever com exatidão o uso das ferramentas na redação. O restante da declaração não mudou.

**Anexos.** O Manual do TCC exige anexar ao trabalho o comprovante da revisão ortográfica e gramatical. Entraram, digitalizados a partir dos PDFs assinados digitalmente pelo gov.br:
- ANEXO A – Declaração de revisão gramatical (revisora formada em Letras, 26/11);
- ANEXO B – Autorização do orientador para defesa (27/11).

O conversor acrescenta os anexos depois dos apêndices, quando as imagens existem em `docs/artigo/figuras/`. Eles ficam fora do `.md` porque a região dos apêndices é sobrescrita pelo `sincronizar_apendices`. Monografia regenerada: 77 páginas. Nenhuma mudança em código, dados ou números.

## Decisões em aberto

| # | Questão | Opções | Recomendação |
|---|---|---|---|
| ~~Q1~~ | **Resolvida em E18 → opção (a), D18.** FN `GET /` (E13): defeito na geração de candidatos | (a) corrigir (incluir `/` como candidato) e **refazer** a bateria do VAmPI antes do freeze de 20/11; (b) manter e documentar como limitação | (a). É defeito, não limitação. A correção é de uma linha, a bateria leva ~75 min e o freeze ainda não chegou. |
| Q3 | Defeito E22 (token expira em 60 s): como corrigir e o que refazer | (a) renovar a credencial durante a execução e refazer só as execuções com auth (N=0 e as 10 da bateria); (b) idem, refazendo a bateria inteira para uniformizar a versão do código | **Resolvida em E23 → opção (a), D19.** |
| Q2 | **Encaminhada como limitação** (`trabalhos_futuros.md`). FN `PUT …/{username}/password` (E13): wordlist não aplicada sob prefixos com parâmetro | (a) estender a descoberta; (b) documentar como limitação e trabalho futuro | (b). É ampliação de cobertura, vetada pelo congelamento de escopo (CLAUDE.md §2). A D17 já separa esse efeito como FN de descoberta. |
