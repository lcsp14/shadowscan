# Bloco 2.1 — Teste/fuzzing de APIs REST e descoberta de endpoints

Busca bibliográfica realizada em 18/11/2026. Todas as consultas foram feitas por requisição HTTP direta (curl) às APIs públicas listadas, com a resposta JSON/XML bruta salva e lida — não por resumo intermediário. Os resumos abaixo são **baseados no resumo (abstract)** de cada trabalho, obtido do registro indicado; nenhum texto completo foi lido.

---

## 1. Protocolo de busca

### 1.1 Bases tentadas e indisponíveis

| Base | Situação em 18/11/2026 |
|---|---|
| dblp (`dblp.org/search/publ/api` e espelho `dblp.uni-trier.de`) | **Indisponível**: a API devolveu página de verificação anti-robô ("Making sure you're not a bot!") em vez de JSON, inclusive com User-Agent próprio. Nenhuma contagem obtida. **Não declarar dblp como base consultada.** |
| Semantic Scholar (`/graph/v1/paper/search`) | Parcial: HTTP 429 (limite de taxa) persistente para 4 consultas mesmo após ~8 tentativas com espera de 12 s. 3 consultas retornaram. |
| OpenAlex (`api.openalex.org/works?search=`) | Parcial: limite de taxa anônimo ("Rate limit exceeded") em parte das consultas. Base adicionada pelo pesquisador (não estava na sugestão original) por expor contagem (`meta.count`) e resumos. |
| Google Scholar, IEEE Xplore, ACM DL | **Não consultados** como bases de busca. (IEEE Xplore e ACM DL aparecem apenas como destino de redirecionamento de DOI, sem busca.) |

### 1.2 Consultas registradas

Observação sobre Crossref: o parâmetro `query.bibliographic` ordena por relevância e casa termos com OU, por isso o "total reportado" é enorme e não tem significado como contagem de trabalhos pertinentes; foram triados os 20 primeiros por relevância. Em OpenAlex e arXiv as consultas foram feitas por frase exata (entre aspas).

| Base | Termos (exatos) | Data | Total reportado | Triados | Selecionados |
|---|---|---|---|---|---|
| Semantic Scholar | `REST API fuzzing` | 18/11/2026 | — (HTTP 429) | 0 | 0 |
| Semantic Scholar | `REST API testing` | 18/11/2026 | — (HTTP 429) | 0 | 0 |
| Semantic Scholar | `RESTful API black-box testing` | 18/11/2026 | — (HTTP 429) | 0 | 0 |
| Semantic Scholar | `undocumented endpoint` | 18/11/2026 | — (HTTP 429) | 0 | 0 |
| Semantic Scholar | `hidden API endpoint discovery` | 18/11/2026 | 159 | 20 | 1 (Amoruso et al., 2026) |
| Semantic Scholar | `undocumented REST API endpoints` | 18/11/2026 | 302 | 20 | 1 novo (Huang et al., 2024); Amoruso et al. repetido |
| Semantic Scholar | `shadow API endpoint` | 18/11/2026 | 2136 | 20 | 0 novos (Huang et al. repetido) |
| OpenAlex | `"undocumented endpoint"` | 18/11/2026 | 32 | 25 | 2 (Levi; Dubin, 2026; Yang et al., 2026 — ambos preprints) |
| OpenAlex | `"zombie API"` | 18/11/2026 | 15 | 15 | 0 novos (Amoruso et al. repetido) |
| OpenAlex | `"RESTful API black-box testing"` | 18/11/2026 | 5 | 5 | 0 |
| OpenAlex | `"hidden API endpoint discovery"` | 18/11/2026 | 0 | 0 | 0 |
| OpenAlex | `"REST API fuzzing"`, `"REST API testing"`, `"shadow API"`, `"forced browsing"`, `"kiterunner"`, `"soft 404"` | 18/11/2026 | — (limite de taxa) | 0 | 0 |
| Crossref | `REST API fuzzing` | 18/11/2026 | 65.895 (OU, relevância) | 20 | 1 (Atlidakis et al., 2019) |
| Crossref | `shadow API endpoints` | 18/11/2026 | 84.088 (OU, relevância) | 20 | 0 |
| Crossref | `undocumented API endpoints detection` | 18/11/2026 | 1.612.243 (OU, relevância) | 20 | 0 |
| Crossref | `zombie API deprecated endpoints` | 18/11/2026 | 36.365 (OU, relevância) | 20 | 0 novos (Amoruso et al. repetido) |
| arXiv API | `all:"REST API fuzzing"` | 18/11/2026 | 12 | 12 | 0 novos (preprint do RESTler, 1806.09739) |
| arXiv API | `all:"REST API" AND all:undocumented` | 18/11/2026 | 4 | 4 | 0 novos (Levi; Dubin repetido) |
| arXiv API | `all:"shadow API"` | 18/11/2026 | 3 | 3 | 0 (ver nota sobre Unbrowse em §4) |
| arXiv API | `all:"zombie API"` | 18/11/2026 | 0 | 0 | 0 |
| arXiv API | `all:"undocumented endpoints"` | 18/11/2026 | 0 | 0 | 0 |
| arXiv API | `all:"hidden endpoints"` | 18/11/2026 | 1 | 1 | 0 (tema não relacionado) |
| arXiv API | `all:"directory brute forcing"` | 18/11/2026 | 1 | 1 | 1 (Castagnaro et al., 2024) |
| arXiv API | `all:"forced browsing"` | 18/11/2026 | 0 | 0 | 0 |
| arXiv API | `all:gobuster` | 18/11/2026 | 0 | 0 | 0 |
| arXiv API | `all:ffuf` | 18/11/2026 | 0 | 0 | 0 |
| arXiv API | `all:kiterunner` | 18/11/2026 | 1 | 1 | 0 (homônimo, robótica) |
| arXiv API | `all:"soft 404"` | 18/11/2026 | 1 | 1 | 0 (fora deste bloco) |
| Crossref (busca por item conhecido) | DOIs dos 3 candidatos indicados pelo autor + Kim et al. (2022) | 18/11/2026 | — | 4 | 4 |

Endpoints usados: `https://api.semanticscholar.org/graph/v1/paper/search?query=...&limit=20`; `https://api.openalex.org/works?search="..."&per-page=25`; `https://api.crossref.org/works?query.bibliographic=...&rows=20`; `https://export.arxiv.org/api/query?search_query=...&max_results=25`.

---

## 2. Referências confirmadas

Prioridade sugerida para o artigo: **[1] RESTler, [3] Golmohammadi et al., [4] Kim et al., [5] Amoruso et al.** (núcleo, 4 referências); [2] EvoMaster, [6] Respector e [7] Castagnaro et al. como complementares. [8] e [9] são preprints arXiv sem revisão por pares confirmada — usar só se necessário e identificá-los como preprint.

### [1] RESTler

ATLIDAKIS, Vaggelis; GODEFROID, Patrice; POLISHCHUK, Marina. **RESTler: Stateful REST API Fuzzing**. In: IEEE/ACM INTERNATIONAL CONFERENCE ON SOFTWARE ENGINEERING (ICSE), 41., 2019, Montreal. *Proceedings* [...]. IEEE, 2019. p. 748–758. DOI: 10.1109/ICSE.2019.00083.

- URL conferida: https://api.crossref.org/works/10.1109/icse.2019.00083 (metadados); https://api.openalex.org/works/doi:10.1109/icse.2019.00083 (resumo).
- Resumo (baseado no resumo): apresentado como o primeiro fuzzer *stateful* de APIs REST. Analisa a especificação da API e gera sequências de requisições inferindo dependências produtor-consumidor entre os tipos de requisição declarados na especificação e aprendendo com o retorno dinâmico das respostas para podar sequências inválidas. Avaliado no GitLab (28 bugs) e em serviços Azure e Office365, com bugs confirmados pelos mantenedores.
- **Comparação com este trabalho**: parte da especificação e explora apenas as requisições nela declaradas; não faz descoberta de caminhos fora da especificação nem trata endpoints não declarados. Avaliação por bugs encontrados, não por ground truth de precisão/revocação. É o exemplo canônico de "explorar o que está declarado".

### [2] EvoMaster

ARCURI, Andrea. **RESTful API Automated Test Case Generation with EvoMaster**. *ACM Transactions on Software Engineering and Methodology*, v. 28, n. 1, p. 1–37, jan. 2019. DOI: 10.1145/3293455.

- URL conferida: https://api.crossref.org/works/10.1145/3293455 (metadados e resumo).
- Resumo (baseado no resumo): propõe abordagem caixa-branca, do ponto de vista do desenvolvedor com acesso ao código, em que casos de teste para APIs RESTful são gerados por algoritmo evolutivo, recompensados por cobertura de código e métricas de detecção de falhas, com técnicas de amostragem que exploram boas práticas de projeto REST. Em cinco serviços de código aberto, encontrou 80 bugs reais, com cobertura inferior às suítes manuais existentes.
- **Comparação com este trabalho**: o resumo **não menciona explicitamente** o uso da especificação OpenAPI (fala em "endpoints REST" e informação caixa-branca do código); não afirmar no artigo que o EvoMaster é dirigido por especificação com base apenas nesta referência. Não trata endpoints não declarados; avaliação por bugs e cobertura, sem ground truth de inventário. Contraste útil: caixa-branca × caixa-preta (o shadowscan é caixa-preta).

### [3] Golmohammadi, Zhang e Arcuri — survey

GOLMOHAMMADI, Amid; ZHANG, Man; ARCURI, Andrea. **Testing RESTful APIs: A Survey**. *ACM Transactions on Software Engineering and Methodology*, v. 33, n. 1, p. 1–41, 2023. DOI: 10.1145/3617175.

- URL conferida: https://api.crossref.org/works/10.1145/3617175 (metadados e resumo).
- Observação: o Crossref registra publicação em 24/11/2023 no v. 33, n. 1 (fascículo datado de 2024 pela ACM). Citar como 2023 conforme o registro, ou conferir na página da ACM qual ano o orientador prefere.
- Resumo (baseado no resumo): revisão abrangente do estado da arte em teste de APIs RESTful a partir de 92 artigos científicos, coletados em sete bases com critérios predefinidos e *snowballing*. Categoriza os trabalhos e discute desafios em aberto; mostra interesse crescente a partir de 2017.
- **Comparação com este trabalho**: referência de enquadramento da área. O resumo não menciona detecção de endpoints não declarados nem gestão de inventário; não se pode afirmar, sem ler o texto completo, que o survey não cobre o tema. Recomenda-se ao autor verificar no texto completo se há alguma categoria sobre endpoints fora da especificação antes de usar o survey como evidência de lacuna.

### [4] Kim et al. — comparação empírica de ferramentas

KIM, Myeongsoo; XIN, Qi; SINHA, Saurabh; ORSO, Alessandro. **Automated test generation for REST APIs: no time to rest yet**. In: ACM SIGSOFT INTERNATIONAL SYMPOSIUM ON SOFTWARE TESTING AND ANALYSIS (ISSTA), 31., 2022, evento virtual. *Proceedings* [...]. ACM, 2022. p. 289–301. DOI: 10.1145/3533767.3534401.

- URL conferida: https://api.crossref.org/works/10.1145/3533767.3534401 (metadados); https://api.openalex.org/works/doi:10.1145/3533767.3534401 (resumo).
- Resumo (baseado no resumo): estudo empírico que seleciona sistematicamente 10 ferramentas de teste de APIs REST (acadêmicas e de praticantes) e as aplica a 20 serviços RESTful reais de código aberto, comparando cobertura de código e falhas únicas disparadas, para identificar forças, fraquezas e limitações das estratégias.
- **Comparação com este trabalho**: as métricas de comparação são cobertura e falhas, não completude de inventário. Útil para sustentar que a avaliação dominante na área mede o que acontece *dentro* da superfície declarada. Não trata endpoints não declarados (pelo resumo).

### [5] Amoruso et al. — Zombie APIs (TRABALHO MAIS PRÓXIMO; ler na íntegra)

AMORUSO, Edward L.; AMORUSO, Paul E.; BROQI, Aurela; ZOU, Cliff C. **Zombie APIs: Detecting Runtime-Reachable but Deprecated Endpoints**. In: INTERNATIONAL SYMPOSIUM ON NETWORKS, COMPUTERS AND COMMUNICATIONS (ISNCC), 2026, Bristol. *Proceedings* [...]. IEEE, 2026. p. 1–7. DOI: 10.1109/ISNCC70543.2026.11693891.

- URL conferida: https://api.crossref.org/works/10.1109/isncc70543.2026.11693891 (metadados); https://api.openalex.org/works/doi:10.1109/isncc70543.2026.11693891 (resumo); https://doi.org/10.1109/ISNCC70543.2026.11693891 → redireciona para https://ieeexplore.ieee.org/document/11693891/ (verificado só o redirecionamento). Também apareceu no Semantic Scholar (duas consultas).
- Resumo (baseado no resumo): afirma que as ferramentas de teste de API existentes visam vulnerabilidades dentro de interfaces documentadas e assumem especificações completas. Formaliza *zombie APIs* como discrepâncias entre o estado de ciclo de vida declarado e o comportamento observável em execução, abrangendo endpoints obsoletos, não documentados ou ocultos. Propõe descoberta a partir de uma URL alvo sem depender de especificação completa, combinando extração de endpoints de artefatos do lado do cliente com sondagem adaptativa (mutação de método HTTP, enumeração de versões, sondagem *shadow* por cabeçalhos e **análise diferencial de respostas**). Avaliado em testbed FastAPI controlado e em servidor exposto à Internet; relata descoberta de 90–100% dos endpoints e taxa de falsos positivos de 0% a 15%.
- **Comparação com este trabalho**: é o trabalho encontrado mais próximo. Também detecta endpoints não declarados por sondagem ativa caixa-preta, usa análise diferencial de respostas e mede descoberta e falsos positivos em ambiente controlado. Diferenças que **parecem** existir pelo resumo (confirmar no texto completo): (a) ponto de partida é a URL e artefatos do cliente, não o diferencial contra uma especificação OpenAPI; (b) o foco é ciclo de vida/obsolescência; (c) não há menção a ground truth construído por degradação controlada da especificação com sementes fixas, nem a precisão/revocação separadas para descoberta e diferencial. **Atenção terminológica**: nesse trabalho "zombie" engloba endpoints obsoletos, não documentados e ocultos, enquanto o shadowscan usa *zombie* = D\O (declarado e não observado). O artigo precisa explicitar essa divergência.

### [6] Respector

HUANG, Ruikai; MOTWANI, Manish; MARTINEZ, Idel; ORSO, Alessandro. **Generating REST API Specifications through Static Analysis**. In: IEEE/ACM INTERNATIONAL CONFERENCE ON SOFTWARE ENGINEERING (ICSE), 46., 2024, Lisboa. *Proceedings* [...]. ACM, 2024. p. 1–13. DOI: 10.1145/3597503.3639137.

- URL conferida: https://api.crossref.org/works/10.1145/3597503.3639137 (metadados); https://api.openalex.org/works/doi:10.1145/3597503.3639137 (resumo). Também retornado pelo Semantic Scholar.
- Resumo (baseado no resumo): observa que especificações OpenAPI escritas manualmente tendem a ficar incompletas ou inconsistentes à medida que o software evolui. Propõe o Respector, que usa análise estática e simbólica do código-fonte para gerar especificações. Em 15 APIs reais, ao comparar a especificação gerada com a fornecida pelos desenvolvedores, identificou muitos métodos de endpoint, parâmetros, restrições e respostas ausentes, além de inconsistências entre especificação e implementação.
- **Comparação com este trabalho**: confirma empiricamente, por via caixa-branca, que especificações reais omitem endpoints, o que sustenta a premissa do shadowscan. Diferença: exige o código-fonte; o shadowscan é caixa-preta. Avalia precisão e revocação da inferência de endpoints contra referência, mas não detecção de *shadow endpoints* em execução.

### [7] Castagnaro, Conti e Pajola — força bruta de diretórios

CASTAGNARO, Alberto; CONTI, Mauro; PAJOLA, Luca. **Offensive AI: Enhancing Directory Brute-forcing Attack with the Use of Language Models**. In: WORKSHOP ON ARTIFICIAL INTELLIGENCE AND SECURITY (AISec), 2024, Salt Lake City (realizado com o ACM CCS '24). *Proceedings* [...]. ACM, 2024. p. 184–195. DOI: 10.1145/3689932.3694770.

- URL conferida: https://export.arxiv.org/api/query?id_list=2404.14138 (resumo, arXiv 2404.14138); https://api.crossref.org/works/10.1145/3689932.3694770 (metadados da versão publicada). O resumo lido é o da versão arXiv ("Under submission"); presume-se, mas não foi verificado, que coincide com o publicado.
- Resumo (baseado no resumo): no contexto de testes de penetração web, trata do ataque de força bruta de diretórios, apontando que as soluções comerciais baseadas em wordlists geram enorme número de tentativas para poucos acertos. Propõe um framework baseado em modelos de linguagem para enumeração de diretórios; em testbed de 1 milhão de URLs de domínios variados, relata ganho médio de 969%.
- **Comparação com este trabalho**: único trabalho acadêmico encontrado sobre a classe de ferramentas wordlist (gobuster/ffuf etc.). Confirma a limitação de cobertura da wordlist, a mesma origem dos falsos negativos do shadowscan (ex.: `GET /createdb`). Não parte de especificação nem faz diferencial. Bom suporte para a discussão de limitações e para Trabalhos Futuros (wordlist guiada por modelo de linguagem).

### [8] Levi e Dubin — MRG (preprint)

LEVI, Yarin; DUBIN, Ran. **API Security Based on Automatic OpenAPI Mapping**. arXiv:2604.19471, 2026. Preprint. DOI: 10.48550/arXiv.2604.19471.

- URL conferida: https://export.arxiv.org/api/query?id_list=2604.19471; https://api.openalex.org/works/doi:10.48550/arxiv.2604.19471.
- Resumo (baseado no resumo): método não supervisionado (Map Reduce Graph) que aprende a estrutura de uma API REST a partir de tráfego real, gera documentação compatível com OpenAPI e detecta anomalias e ataques, ajudando a identificar comportamentos não documentados ou em evolução.
- **Comparação com este trabalho**: descoberta **passiva** (tráfego), não ativa; não parte de uma especificação existente. A detecção de "não documentado" é subproduto, e a avaliação relatada é sobre detecção de ataques, não de endpoints não declarados.

### [9] Yang et al. — APISENSOR (preprint)

YANG, Yanjing; ZHONG, Chenxing; HAN, Ke; CHENG, Zeru; XU, Jinwei; ZHOU, Xin; ZHANG, He; LIU, Bohan. **APISENSOR: Robust Discovery of Web API from Runtime Traffic Logs**. arXiv:2603.23852, 2026. Preprint. DOI: 10.48550/arXiv.2603.23852.

- URL conferida: https://export.arxiv.org/api/query?id_list=2603.23852; https://api.openalex.org/works/doi:10.48550/arxiv.2603.23852.
- Resumo (baseado no resumo): reconstrói as APIs de aplicações web, sem supervisão, a partir de logs de tráfego em execução com ruído misto. Classifica as abordagens existentes em estáticas (código ou especificação) e dinâmicas (tráfego). Em seis aplicações, relata F1 de 94,91% e aponta inconsistências de documentação confirmadas pelos desenvolvedores.
- **Comparação com este trabalho**: descoberta passiva por tráfego, avaliada com ground truth (precisão/F1), mas o alvo é reconstruir a API, não medir o conjunto não declarado em relação a uma especificação. Útil para posicionar a dicotomia descoberta passiva × ativa.

---

## 3. Tabela comparativa (linhas para o artigo)

Legenda: "Sim/Não" segundo o resumo; "n.e." = não explícito no resumo.

| Trabalho | Parte da especificação? | Descoberta ativa? | Detecta não declarados? | Avaliação com ground truth? |
|---|---|---|---|---|
| Atlidakis, Godefroid e Polishchuk (2019) — RESTler | Sim | Não (só operações declaradas) | Não | Não (bugs encontrados) |
| Arcuri (2019) — EvoMaster | n.e. (caixa-branca, código) | Não | Não | Não (bugs e cobertura) |
| Golmohammadi, Zhang e Arcuri (2023) — survey | — (revisão) | — | n.e. no resumo | — |
| Kim et al. (2022) — comparação empírica | n.e. | Não | Não | Não (cobertura e falhas) |
| Amoruso et al. (2026) — Zombie APIs | Não (parte da URL e artefatos do cliente) | Sim | Sim | Parcial: testbed controlado, taxas de descoberta e de FP; método de construção do ground truth n.e. |
| Huang et al. (2024) — Respector | Não (código-fonte); compara com a especificação | Não (estática) | Sim, por análise do código | Sim (precisão/revocação da inferência) |
| Castagnaro, Conti e Pajola (2024) | Não | Sim (força bruta de diretórios) | Sim (diretórios web, sem noção de spec) | Sim (testbed de 1 milhão de URLs) |
| Levi e Dubin (2026) — preprint | Não (gera a especificação) | Não (passiva, tráfego) | Parcial ("comportamentos não documentados") | Sim, para ataques, não para endpoints |
| Yang et al. (2026) — preprint | Não | Não (passiva, tráfego) | Indireto | Sim (precisão/F1 de reconstrução) |
| **Este trabalho (shadowscan)** | **Sim** | **Sim** | **Sim (O\D)** | **Sim (degradação controlada da spec, sementes fixas)** |

---

## 4. NÃO CONFIRMADO / localizado mas não incluído

- **Abinaya, J.; Thilagam, P. Santhi; Sivakumar, K.; Pais, Alwyn Roshan. "Security testing of RESTful APIs: Approaches and research challenges". *Computer Science Review*, v. 63, art. 101043. DOI 10.1016/j.cosrev.2026.101043.** Existência confirmada no Crossref (https://api.crossref.org/works/10.1016/j.cosrev.2026.101043), mas **nenhum resumo disponível** no Crossref nem no OpenAlex, e o Crossref registra fascículo de fev./2027 (publicação antecipada online). Não incluído porque não li o conteúdo. Pode ser relevante (survey de testes de segurança em APIs REST); se o autor quiser usar, abrir a página da Elsevier e ler o resumo primeiro.
- **Chaplia, O.; Klym, H. "Extracting REST API Endpoints from Microservices Using LLM Agents". DESSERT 2024. DOI 10.1109/DESSERT65323.2024.11122242.** Confirmado (Crossref + OpenAlex) e resumo lido: extração de endpoints a partir do código-fonte de microsserviços Node.js com agentes LLM para gerar OpenAPI. Não incluído: caixa-branca, foco em documentação, sem relação com detecção de endpoints não declarados em execução.
- **Tham, L.; Mac Gregor Garcia, N.; Hahn, J. "Internal APIs Are All You Need: Shadow APIs, ..." arXiv:2604.00694 (2026).** Resumo lido. Usa "shadow APIs" no sentido de APIs internas de primeira parte por trás de interfaces web, para agentes de IA, e não no sentido de API9. Não incluído; registrado só para evitar confusão terminológica se a banca o mencionar.
- **Semantic Scholar para "REST API fuzzing", "REST API testing", "RESTful API black-box testing", "undocumented endpoint"**: não executadas (HTTP 429). Não declarar essas consultas como feitas.
- **dblp**: nenhuma consulta executada (bloqueio anti-robô). Não declarar.
- **Trabalhos acadêmicos sobre kiterunner, ffuf, gobuster**: nada encontrado no arXiv (0 resultados para `ffuf` e `gobuster`; `kiterunner` só homônimo de robótica). As consultas no OpenAlex esbarraram no limite de taxa. Essas ferramentas devem ser citadas como software (repositório/URL), não como literatura acadêmica.
- Candidatos vistos nas listas mas **não verificados** (nenhum registro individual consultado, então não usar): WuppieFuzz (ICISSP 2026), APIRL (AAAI 2025), Human-Centered Evaluation of REST API Fuzzing Tools (ASE 2025), "Intelligent REST API data fuzzing" (ESEC/FSE 2020), MINER, foREST, Pythia, RESTCov (arXiv 2608.28114), OASQuali (LNCS 2026). Se algum for necessário, buscar o registro DOI antes de citar.

---

## 5. Achado sobre a lacuna

**A afirmação "nenhum trabalho mede a acurácia da detecção de endpoints não declarados" NÃO se sustenta.** Nas consultas Semantic Scholar `hidden API endpoint discovery` e `undocumented REST API endpoints`, OpenAlex `"zombie API"` e Crossref `zombie API deprecated endpoints`, foi encontrado **Amoruso et al. (ISNCC 2026, publicado em set./2026)**. Segundo o resumo, esse trabalho descobre endpoints ocultos ou não documentados por sondagem ativa com análise diferencial de respostas e relata taxa de descoberta (90–100%) e de falsos positivos (0–15%) em testbed controlado.

O que **não foi encontrado** nas buscas registradas acima (Semantic Scholar parcial, OpenAlex parcial, Crossref, arXiv; dblp indisponível):
1. trabalho que defina o conjunto shadow como diferencial **O\D contra uma especificação OpenAPI** e meça precisão e revocação desse diferencial;
2. trabalho que construa o ground truth por **degradação controlada da especificação** (remoção de N operações com sementes fixas);
3. trabalho que reporte separadamente a métrica **fim-a-fim** e a do **diferencial isolado**.

Formulação sugerida para o artigo, de forma conservadora: "Ferramentas de teste dirigidas por especificação, como RESTler (ATLIDAKIS; GODEFROID; POLISHCHUK, 2019), exploram a superfície declarada, e as comparações empíricas da área (KIM et al., 2022) medem cobertura e falhas. Amoruso et al. (2026) abordam a descoberta de endpoints não documentados em execução, partindo da URL alvo e de artefatos do cliente. Nas buscas realizadas não se encontrou trabalho que avalie o diferencial entre a especificação OpenAPI e a superfície observada com ground truth obtido por degradação controlada da especificação." A novidade fica no **método de avaliação** e no **diferencial ancorado na spec**, não na ideia de detectar endpoints não documentados.

**Ação recomendada antes de redigir a seção 2.1:** obter e ler o texto completo de Amoruso et al. (IEEE Xplore, documento 11693891; pode exigir acesso institucional) para confirmar (a) se usam a especificação OpenAPI, (b) como constroem o ground truth, (c) a definição exata de *zombie* e *shadow*. As diferenças listadas em [5] são inferências a partir do resumo.
