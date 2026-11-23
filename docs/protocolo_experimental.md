# Protocolo experimental

Descrição formal do experimento: questões de pesquisa, variáveis, procedimento, métricas
(com fórmulas) e ameaças à validade. É a base das seções de Metodologia e Discussão do
artigo. As decisões de implementação estão em `decisoes.md` (D1–D21); o ambiente exato,
em `ambiente_experimental.md`; o histórico do que foi feito, em `diario_de_pesquisa.md`.

---

## 1. Questões de pesquisa

- **QP1.** Com que precisão e revocação a abordagem diferencial (descoberta ativa
  confrontada com a especificação OpenAPI) identifica shadow endpoints?
- **QP2.** Qual parcela dos erros vem da **descoberta** (o endpoint nunca foi observado) e
  qual vem do **motor diferencial** (foi observado mas classificado errado)?
- **QP3.** O desempenho se mantém estável quando variam o número de endpoints ocultos (N),
  quais endpoints são ocultados (semente) e o uso de autenticação?
- **QP4.** As especificações de APIs de referência são completas? A ferramenta encontra
  shadow endpoints reais, que não foram plantados pelo experimento?

---

## 2. Método de validação: ground truth por degradação de especificação

Medir acerto exige conhecer de antemão a resposta correta. Em uma API arbitrária, o
conjunto real de shadow endpoints é desconhecido. O método usado **planta** shadow
endpoints conhecidos:

1. Parte-se da especificação original S do alvo, com o conjunto de operações D(S).
2. Sorteiam-se N operações de D(S) com um gerador pseudoaleatório de semente fixa
   (`random.Random(seed).sample`), e elas são removidas, gerando a spec degradada S'.
3. As operações removidas, G = D(S) \ D(S'), continuam implementadas na API, mas não estão
   mais declaradas. São, por definição, shadow endpoints conhecidos, e formam o ground truth.
4. A ferramenta roda contra a API usando S'.
5. O conjunto reportado R é comparado com G.

Cada operação removida recebe um **tipo** (D4):
- `caminho`: nenhum método do caminho sobrou em S'. Para achar, é preciso descobrir o
  caminho (wordlist, prefixo, versão ou rota-coringa).
- `metodo`: o caminho continua em S' com outro método. Para achar, é preciso variar o
  método HTTP.

### 2.1 Levantamento de shadows intrínsecos (N = 0)

Antes da bateria, a ferramenta roda com a spec **original** (N=0, G=∅). Todo shadow reportado
nessa condição é candidato a **shadow intrínseco**: endpoint real do alvo, ausente da spec
original. O escopo é a superfície HTTP na origem da API (esquema, host e porta da URL base),
seja o endpoint servido por rota de API, rota web, componente do framework ou arquivo
estático (D9; artigo, Seção 4.3). Cada candidato é **verificado manualmente** com requisições diretas, e os
confirmados entram em `specs/<alvo>_intrinsecos.json`. Na bateria, eles são removidos de R
antes de contar falsos positivos (D9). As métricas **brutas**, sem essa exclusão, são
sempre reportadas ao lado das ajustadas.

---

## 3. Variáveis

### 3.1 Independentes (fatores)

| Fator | Níveis | Justificativa |
|---|---|---|
| Alvo | VAmPI, vAPI | Frameworks diferentes (Flask/connexion × Laravel), comportamentos de "não encontrado" diferentes (404 × 500 `{}`) e specs de naturezas diferentes (escrita à mão × derivada do roteador) |
| N (operações removidas) | 3, 6 | VAmPI tem 14 operações, então N=3 ≈ 21% e N=6 ≈ 43% da spec. Testa a estabilidade com degradação leve e forte. |
| Semente | 1, 2, 3, 4, 5 | Cada semente sorteia um conjunto diferente de operações. Varia **quais** endpoints ficam ocultos e, com isso, o tipo de remoção. |
| Autenticação | sem, com (usuário comum) | Endpoints protegidos podem responder igual antes e depois da autenticação (ver A2). Só no VAmPI (D16). |

Desenho fatorial completo no VAmPI: 2 (N) × 5 (sementes) × 2 (auth) = **20 execuções**,
mais 2 execuções N=0 (com e sem auth). No vAPI: 2 × 5 × 1 = **10 execuções**, mais 1 N=0.

### 3.2 Fixas (controladas)

Todos os parâmetros da seção 2.2 de `ambiente_experimental.md`: limiar 0,90, wordlist,
métodos, concorrência etc. Antes de cada execução no VAmPI, o banco é reiniciado com
`GET /createdb` (D15), para que o estado da aplicação seja o mesmo em todas as execuções.

### 3.3 Dependentes (medidas)

Ver seção 4.

---

## 4. Métricas

Notação: R = shadows reportados (pares método × caminho canônico, D3), I = shadows
intrínsecos verificados, G = ground truth, O = conjunto observado pela descoberta.

### 4.1 Fim-a-fim (QP1)

R* = R \ I  (versão ajustada; na versão bruta, R* = R)

- VP = |R* ∩ G|
- FP = |R* \ G|
- FN = |G \ R*|
- **Precisão** P = VP / (VP + FP)
- **Revocação** Rev = VP / (VP + FN) = VP / |G|
- **F1** = 2·P·Rev / (P + Rev)

Por convenção, P = 0 quando R* = ∅ (nada reportado).

### 4.2 Decomposição (QP2, D17)

- G_O = {g ∈ G : g foi observado em O}. Uma observação conta para g se tem o mesmo método
  e a mesma chave canônica, ou se é um caminho concreto que casa com o template de g.
- **Revocação da descoberta** = |G_O| / |G|
- **Revocação do diferencial isolado** = |G_O ∩ R| / |G_O|
- Identidade: Rev (fim-a-fim) = Rev_descoberta × Rev_diferencial, quando calculadas sobre
  o mesmo conjunto.

Os falsos negativos são separados por causa:
- **FN de descoberta**: g ∉ O. Limite da wordlist ou da estratégia de sondagem.
- **FN de diferencial**: g ∈ O, mas g ∉ R. Limite do casamento por template ou da política
  para casos ambíguos.

### 4.3 Por caminho único

Mesmas fórmulas da 4.1, mas com o caminho como unidade, ignorando o método. Neutraliza
a inflação causada por caminhos que respondem a vários métodos (ex.: `/console` × 5).

### 4.4 Custo

Número de requisições HTTP, número de erros de rede e tempo total em segundos. O tempo é
indicativo (ver A4).

### 4.5 Agregação

Para cada combinação (alvo, N, auth): média ± desvio padrão amostral entre as 5 sementes.
Para as razões de contagem (tabelas 2 e 4 do `resumo.md`): soma dos numeradores ÷ soma dos
denominadores (micro-média).

---

## 5. Procedimento (reprodutível)

```powershell
# 1. Ambientes (versões exatas no Apêndice D)
docker run -d --name vampi -p 5000:5000 erev0s/vampi@sha256:0a5a224b6e14ae7da6a6ea265178ff71286ff903aec74adee98f660bb0e4ca12
cd envs\vapi; docker compose up -d --build; cd ..\..

# 2. Levantamento de intrínsecos (N=0), seguido de verificação manual de cada candidato
python -m experiments.run_experiments --alvo vampi --n 0 --seeds 1 --out runs\exp_vampi_n0
python -m experiments.run_experiments --alvo vapi  --n 0 --seeds 1 --out runs\exp_vapi_n0

# 3. Bateria principal
python -m experiments.run_experiments --alvo vampi --n 3 6 --seeds 1 2 3 4 5 --out runs\exp_vampi_principal
python -m experiments.run_experiments --alvo vapi  --n 3 6 --seeds 1 2 3 4 5 --out runs\exp_vapi_principal

# 4. Análise (não toca nos alvos)
python -m experiments.analyze runs\exp_vampi_principal --intrinsecos specs\vampi_intrinsecos.json
python -m experiments.analyze runs\exp_vapi_principal  --intrinsecos specs\vapi_intrinsecos.json
```

Cada execução grava em `runs/<bateria>/<n>_<seed>_<auth>/`:
- `spec_degradada.yml`: a spec S' usada;
- `ground_truth.json`: N, semente e a lista G com o tipo de cada remoção;
- `resultado.json`: configuração completa, contadores de execução, todos os shadows
  (com origem, status e colisão com template), operações declaradas não observadas
  (campo `zombie`), casos ambíguos, **todas as
  observações de O** e as métricas bruta e ajustada.

Como o sorteio usa semente fixa, o mesmo G pode ser regenerado a qualquer momento com
`python -m shadowscan.ground_truth <spec> -n N --seed S -o <dir>`.

---

## 6. Escopo ético e de execução

Todas as requisições foram feitas **exclusivamente contra instâncias locais** (127.0.0.1),
em containers criados e controlados pelo autor, de aplicações **deliberadamente vulneráveis**
publicadas para ensino (VAmPI e vAPI). Nenhum sistema de terceiros, API pública ou alvo não
controlado foi sondado. Os métodos que alteram estado (POST, PUT, PATCH, DELETE) foram
enviados com corpo vazio (`{}`), e o estado do VAmPI foi reiniciado antes de cada execução.

---

## 7. Ameaças à validade

A1–A9 foram previstas antes da coleta dos dados usados no artigo e registradas neste protocolo em 17/11/2026, às 10:21 (diário E17). A bateria válida do VAmPI começou às 10:24 (E19). A10–A13 foram identificadas durante o desenvolvimento: A10 por um defeito durante a coleta (E22), A11 na revisão do texto (E24), A12 e A13 nos resultados (E29 e E32).

| Id | Ameaça | Tipo | Mitigação / tratamento |
|---|---|---|---|
| A1 | **Spec original incompleta.** Se S não declara tudo, endpoints reais aparecem como FP. | Interna | Levantamento de intrínsecos (N=0) com verificação manual. Métricas bruta e ajustada lado a lado (D9). |
| A2 | **Rotas protegidas indistinguíveis.** Um middleware de autenticação que responde 401 para qualquer caminho sob um prefixo torna rotas reais iguais ao baseline. | Interna | Fator autenticação no desenho. Limitação documentada (D6). **Manifestada no vAPI (diário E34):** o tratador global de exceções (`app/Exceptions/Handler.php:37–39`) responde `500 {}` a toda exceção. Rota inexistente, falta de credencial e erro de código ficam indistinguíveis. Duas rotas declaradas (`GET /vapi/user`, protegida por `auth:sanctum`; `POST /vapi/api7/user`, que lança exceção com o corpo `{}`) foram reportadas como operações declaradas não observadas, embora existam. |
| A3 | **Wordlist.** A revocação depende da cobertura da wordlist. | Construto | Wordlist pública e **não ajustada ao alvo** (D14). Decomposição descoberta × diferencial (D17) separa esse efeito da contribuição central. |
| A4 | **Tempo de execução.** Máquina não dedicada, com outros containers ativos. | Construto | Tempo reportado só como indicativo. Baterias de alvos diferentes **não** rodam em paralelo. |
| A5 | **Poucos alvos (2), ambos didáticos.** | Externa | Alvos com frameworks e comportamentos diferentes. Generalização para APIs de produção fica como trabalho futuro. |
| A6 | **Shadows plantados ≠ shadows naturais.** Endpoints removidos da spec são rotas "normais", enquanto shadows reais tendem a ser debug, admin ou versões antigas. | Externa | Complementado pelo achado de shadows naturais (QP4: `/console` no VAmPI). |
| A7 | **Tamanho da amostra.** 5 sementes por condição. | Conclusão | Média ± desvio reportados. Sem testes de significância estatística, por causa do n pequeno. |
| A8 | **Contagem por método.** Um caminho multi-método infla as contagens. | Construto | Métricas por caminho único (Seção 4.5). |
| A9 | **Política para casos ambíguos.** O resultado depende de `template_policy`. | Interna | Política conservadora fixada a priori (D8). Casos ambíguos listados em cada resultado. |
| A10 | **Credencial de vida curta.** Um token que expira durante a execução transforma "autenticado" em "credencial expirada" sem aviso, e os baselines obtidos antes e depois da expiração deixam de ser comparáveis (diário E22). | Interna | Renovação periódica da credencial (D19), com o número de renovações registrado em cada execução. |
| A11 | **Classificação não avaliada.** O ground truth sintético raramente exercita as categorias heurísticas (VAmPI: 1 de 14 operações; vAPI: 3 de 33) e não fornece rótulo de categoria. | Construto | Declarar a classificação como recurso de apresentação, não como componente avaliado. Avaliação com shadows naturais rotulados → trabalho futuro. |
| A12 | **Estado do alvo alterado pela própria varredura.** A descoberta sonda endpoints declarados que mudam estado. No VAmPI, `GET /createdb` executa `db.drop_all()` + `db.create_all()`. Com requisições concorrentes, algumas pegam o banco no meio da recriação (logs: 64 chamadas a `/createdb` na bateria, 3 respostas 500, 2 erros `no such table`). | Interna | Banco resetado antes de cada execução (D15). Efeito medido: 1 observação divergente em 10 pares de execuções equivalentes, nenhuma métrica alterada. Mecanismo verificado em log (diário E32): na execução divergente, a chamada da própria varredura a `/createdb` falhou (500), o banco ficou sem os usuários padrão e `GET /users/v1/admin` respondeu 404. Excluir o endpoint da sondagem foi descartado por ser ajuste ao alvo. |
| A13 | **Erosão de âncoras pela degradação.** No desenho por degradação, N controla ao mesmo tempo o número de shadows e a completude da especificação restante. Como a descoberta se ancora nos prefixos declarados, ocultar mais operações remove também a informação que ajudaria a encontrá-las. Em uma API real, as duas grandezas são independentes. | Construto | Efeito estimado por contrafactual (diário E32), não medido diretamente. Supondo que os 3 FN da subárvore `/books`, ocultada inteira, teriam sido encontrados com a âncora presente, N = 6 teria revocação de 0,77. Da queda entre N = 3 e N = 6 (0,80 → 0,67), 0,10 seria atribuível à perda de âncora e 0,03 ao sorteio de endpoints difíceis. O diferencial isolado não é afetado (1,00 nas duas condições). |
