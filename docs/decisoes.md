# Registro de decisões que afetam o resultado medido

Uma entrada por decisão de projeto que afeta o resultado medido, com a justificativa e, quando
houver, a alternativa descartada. As menções a entradas E## remetem ao diário de pesquisa,
disponível com o código e os dados (Seção 6.5).

## D1 — Endpoint = (método HTTP, caminho-template)
Dois endpoints são o mesmo se têm o mesmo método e o mesmo caminho. `GET /users` e
`DELETE /users` são endpoints distintos. Consequência: um caminho que responde a 5
métodos conta como 5 endpoints (ver `/console` no VAmPI).

## D2 — Caminhos mantidos em forma de template no conjunto D
O parser não expande `{param}`. O casamento observado × template é feito no módulo 3.

## D3 — Normalização de caminho
- Barra inicial garantida; barra final removida (exceto em `/`).
- Prefixo de `servers[0].url` (só o componente de caminho) é somado aos caminhos da spec.
- Sem normalização de maiúsculas/minúsculas (caminhos HTTP são case-sensitive).
- O NOME do parâmetro é ignorado na comparação: `/u/{id}` ≡ `/u/{user_id}` ≡ `/u/{param}`.

## D4 — Unidade de remoção no ground truth = operação
Cada remoção apaga um par (método, caminho). Se todos os métodos de um caminho forem
removidos, o caminho some da spec (tipo `caminho`); senão, tipo `metodo`.
Sorteio com `random.Random(seed)` — toda execução é reprodutível pela semente.

## D5 — Soft 404: existência por comparação com baselines (`responses.py`)
Uma resposta é "não encontrado" se tiver o MESMO status de um baseline E similaridade
textual ≥ **0,90** (difflib `SequenceMatcher.ratio`) com ele.
Antes de comparar, o corpo é normalizado: o caminho pedido e seu último segmento viram
`{PATH}`/`{SEG}`; números ≥4 dígitos e hex ≥8 caracteres viram `{N}` (ids, timestamps).
Só os primeiros 4000 caracteres entram na comparação (custo do difflib).

Alternativas descartadas:
| Critério | Por que não |
|---|---|
| Só status code | Falha em soft 404 (200 com corpo de erro) — ruído massivo |
| Igualdade exata de corpo | Erros que ecoam o caminho ou trazem timestamp nunca são iguais |
| Só tamanho do corpo | Corpos diferentes podem ter o mesmo tamanho; ecos mudam o tamanho |
| Só estrutura do JSON | `{"message": ...}` de sucesso e de erro têm a mesma estrutura |

Baselines: para cada método, 3 caminhos aleatórios de 1 segmento + 3 de 2 segmentos (globais).

## D6 — Baseline do pai para candidatos literais
Candidato montado por wordlist (`/users/v1/admin`) também é comparado com
`/users/v1/<aleatório>`. Se a resposta for igual, é o template `{username}` respondendo,
não uma rota nova. Instâncias de templates DECLARADOS (`/users/v1/1`) NÃO são comparadas
com o pai — para elas, "usuário não encontrado" é justamente a prova de que a rota existe.
**Limitação:** uma rota literal que responde igual ao template (ex.: ambas dão 401 antes de
qualquer lógica) é indistinguível → falso negativo.

## D7 — Valor de instanciação de parâmetros = `"1"`
`/users/v1/{username}` é sondado como `/users/v1/1`. Fixo e configurável (`--param-value`).

## D8 — Precedência no casamento (motor diferencial)
1. literal exato; 2. por template (`{param}` casa exatamente 1 segmento; mesmo nº de segmentos).
Caso 2 é ambíguo (`/users/v1/admin` pode ser usuário "admin" ou rota escondida).
Política padrão `declarado` (conservadora: assume template); alternativa `shadow`.
Casos ambíguos são sempre listados no relatório.

## D9 — Shadows intrínsecos excluídos do FP
A spec "completa" do alvo pode não ser completa. Rodando a ferramenta com a spec original
(N=0), o que aparece são shadows REAIS do alvo. Após verificação manual, são listados em
`specs/<alvo>_intrinsecos.json` e retirados do conjunto reportado antes de contar FP.
Métricas brutas (sem a exclusão) também são registradas.
VAmPI: `/console` (Werkzeug Debugger, 5 métodos) e `GET /ui` (Swagger UI, 308).
vAPI: `GET /` e `GET /vapi` (rotas web, `routes/web.php`) e `/favicon.ico` (arquivo estático, 5 métodos).
Escopo: a análise cobre a superfície HTTP na origem da API
(esquema, host e porta da URL base), não só as rotas de API. A origem do intrínseco (rota de
API, rota web, componente do framework, arquivo estático) é descritiva e não muda o
tratamento. Nos dois alvos, nenhum intrínseco é rota de API da aplicação.

## D10 — Fase A sonda GET e POST
Só GET não basta: se `GET /users/v1/{username}` existe, `GET /users/v1/register`
responde "usuário não encontrado" e esconde `POST /users/v1/register`. Achado na 1ª execução
(FN corrigido). Custo: dobra as requisições da fase A. Configurável (`--probe-methods`).
Um 405 só prova que o caminho existe se o 405 do pai for diferente.

## D11 — OPTIONS e HEAD fora dos métodos padrão
Frameworks (Flask, Express, Laravel) respondem OPTIONS/HEAD automaticamente para
qualquer rota existente. Incluí-los dobraria a contagem de shadows com endpoints que
não são implementados pelo desenvolvedor. Pode ser reativado com `--methods`.

## D12 — Rota-coringa inferida (fase C)
Se `/books/v1/<aleatório>` não responde como o "não encontrado" global, existe uma rota
com parâmetro sob `/books/v1`. Registrada como `/books/v1/{param}` (casa com qualquer
nome de parâmetro, D3). Permite detectar templates removidos da spec, que nenhuma
wordlist encontraria.

## D13 — Corpo das requisições
POST/PUT/PATCH enviam `{}` (JSON vazio). Sem corpo, muitas APIs respondem 415 antes do
roteamento. Redirecionamentos não são seguidos (3xx é resposta válida, ex.: `/ui` → 308).

## D14 — Wordlist padrão
SecLists `Discovery/Web-Content/api/objects.txt` + `actions.txt`, sem edição
(~3.300 palavras únicas). Aplicada na raiz e sob cada prefixo literal da spec.
**Não** foi ajustada ao alvo: palavras ausentes (ex.: `createdb`, `_debug` no VAmPI)
geram FN, reportados como limitação de cobertura de wordlist.

## D15 — Estado do alvo
Antes de cada execução da bateria, o banco do alvo é resetado (`GET /createdb` no VAmPI).
Execução autenticada usa um usuário comum (não-admin) criado pelo script.

## D16 — Spec do vAPI derivada das rotas do Laravel
O vAPI não publica OpenAPI (só coleção Postman). A spec foi gerada de
`vapi/routes/api.php` (`experiments/laravel_routes_to_openapi.py`), com prefixo `/vapi`
(de `RouteServiceProvider`). 33 operações = 33 declarações `Route::` do arquivo.
Rotas de `routes/web.php` (`/`, `/vapi` — páginas HTML) ficam fora da spec, que reproduz
só `routes/api.php`. A completude da spec vale para as rotas desse arquivo, não para toda a
superfície da aplicação. Continuam no escopo da análise (superfície HTTP na origem da API, D9):
se a ferramenta encontrá-las, entram como shadows intrínsecos após verificação, como no VAmPI.
vAPI é executado só sem autenticação (cada sub-API tem esquema próprio).

## D17 — Decomposição da revocação: descoberta × diferencial
A degradação de spec mede descoberta e diferencial juntos. Para isolar a contribuição
central, `experiments/analyze.py` reporta (só análise, sem nova execução):
- **Revocação da descoberta** = removidos presentes em O / removidos. Um removido está em O
  se alguma observação do mesmo método tem a mesma chave canônica (inclui `{param}` da
  fase C) ou é um caminho concreto que casa com o template removido.
- **Revocação do diferencial isolado** = removidos em O classificados como shadow / removidos em O.
- Revocação fim-a-fim = descoberta × diferencial.
Também reporta métricas por caminho único (ignorando método), além de por (método, caminho),
e sempre as versões bruta e ajustada (D9) em tabelas adjacentes.

## D18 — A raiz `/` é sempre candidata (correção de defeito)
**Defeito (diário E13).** `build_candidates` nunca gerava `/`: prefixos literais próprios não
incluem a raiz, e a wordlist sob a base vazia gera `/palavra`. Se o sorteio removesse `GET /`
da spec, a ferramenta não tinha **nenhuma** forma de descobri-lo (FN garantido).
**Correção.** `/` entra como candidato fixo (origem `raiz`) em toda execução, tratado como
candidato literal (comparado aos baselines global e do pai; o pai de `/` é a raiz, cujo
baseline coincide com o global). Teste de regressão: `test_raiz_sempre_candidata`.
**Impacto nos dados.** A bateria do VAmPI iniciada às 10:05 foi **interrompida e
invalidada** (4 execuções completas, arquivadas em `runs/_invalidadas/`) e refeita do zero
com o código corrigido, incluindo o N=0.
**Não corrigido:** a wordlist não é aplicada sob prefixos com parâmetro
(`/users/v1/{username}/<palavra>`). Fica como limitação e trabalho futuro (diário E13).

## D19 — Renovação periódica da credencial de autenticação (correção de defeito)
**Defeito (diário E22).** O JWT emitido pelo VAmPI vale 60 s. Uma execução dura de 4 a 9 min,
e a credencial era obtida uma só vez. Depois do primeiro minuto, todas as requisições
seguiam com token expirado (`401 Signature expired`). Isso fazia duas coisas:
- invalidava o fator "autenticado";
- tornava inconsistentes os baselines obtidos em momentos diferentes (antes e depois da expiração).

**Correção.** `Discoverer` aceita `auth_refresh` (função que refaz o login e devolve headers
novos) e o chama a cada `refresh_every` = **45 s** (margem de 15 s sobre a validade de 60 s),
sob um lock, antes de cada requisição em que o intervalo venceu. Os headers passaram a ser
enviados por requisição, e não fixados no cliente HTTP, para que a renovação valha
imediatamente. O número de renovações é registrado em `execucao.renovacoes_auth`.

**Invariância sem autenticação.** Sem `auth_refresh` (todas as execuções sem auth e a CLI com
header fixo), `maybe_refresh_auth` retorna imediatamente e os headers enviados são os mesmos
de antes. Isso é coberto pelo teste `test_sem_provedor_headers_fixos`. Por isso, as execuções
sem autenticação da bateria E19, feitas antes da D19, permanecem válidas.

**Alternativa descartada.** Aumentar a validade do token no VAmPI: alteraria o alvo do
experimento.

## D20 — Normalização simétrica dos corpos na comparação de respostas (correção de defeito)
**Defeito (diário E27).** A D5 substituía o último segmento do caminho pedido por `{SEG}` só no corpo
da própria resposta. Quando a palavra testada coincide com um termo do corpo de erro, a substituição
deforma apenas o candidato. Exemplo: `/users/v1/message`, corpo `{"status": "fail", "message": "User not found"}`
→ `{"status": "fail", "{SEG}": "User not found"}`. A similaridade com o baseline caía abaixo de 0,90 e um
caminho inexistente passava por vivo. Atingia qualquer palavra da wordlist presente na mensagem de erro
(`status`, `message`, `fail`, `found`, …).
**Correção.** Em `similarity(a, b)`, os ecos dos caminhos de **ambas** as respostas são removidos de
**ambos** os corpos. Assim, uma palavra só some se sumir dos dois lados. Testes de regressão:
`test_segmento_igual_a_chave_json` e `test_resposta_realmente_diferente_continua_diferente`.
**Alternativa descartada.** Restringir a substituição a ocorrências "entre aspas" ou "após /": continua
frágil quando o eco aparece em outras formas.

## D21 — Caminho literal que casa com template observado (não declarado) é agrupado nele
**Problema (diário E27).** Quando o template `GET /users/v1/{username}` é ocultado, a fase C o infere
como `/users/v1/{param}` (acerto). Mas `/users/v1/admin`, que é usuário **real** e responde diferente
do baseline, era reportado **também** como shadow separado. Era o mesmo endpoint contado duas vezes, e
virava FP. A D8 já agrupava literais em templates **declarados**, mas não em templates **observados**.
**Correção.** O motor diferencial reúne os templates observados e não declarados (fase C, variações
de versão parametrizadas). Um literal do mesmo método que casa com um deles é registrado como
**ambíguo** e agrupado no template (política `declarado`). Com a política `shadow`, continua reportado
à parte. Testes: `test_literal_agrupado_no_coringa` e `test_metodo_diferente_nao_agrupa`.
**Impacto medido offline** nas 10 execuções sem auth anteriores, recalculando só o diff a partir das
observações gravadas: precisão de 0,50–0,62 → **1,00** nas 4 execuções afetadas; revocação inalterada.
