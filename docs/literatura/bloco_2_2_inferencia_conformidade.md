# Bloco 2.2 — Inferência de especificação e conformidade especificação–implementação

Levantamento feito em 18/11/2026 para a Seção 2.2 do artigo. Todas as referências da Seção 2 foram conferidas em registro buscado na hora (Crossref, OpenAlex, Semantic Scholar ou arXiv). A URL conferida aparece em cada entrada. Os resumos se baseiam no resumo (abstract) lido, salvo quando se indica "conferido no texto completo".

---

## 1. Protocolo de busca

Todas as consultas são de 18/11/2026. "Triados" conta os títulos lidos na primeira página de resultados. "Selecionados" conta os trabalhos que passaram para a Seção 2.

| # | Base (API) | Termos exatos | Data | Total reportado | Triados | Selecionados |
|---|---|---|---|---|---|---|
| 1 | Semantic Scholar (`/graph/v1/paper/search`) | `OpenAPI specification inference` | 18/11/2026 | 10.665 | 20 | 1 (Decrop et al.) |
| 2 | Semantic Scholar | `REST API specification inference` | 18/11/2026 | — (HTTP 429 persistente) | 0 | 0 |
| 3 | Semantic Scholar | `inferring REST API from traffic` | 18/11/2026 | — (HTTP 429 persistente) | 0 | 0 |
| 4 | OpenAlex (`/works?search=`) | `OpenAPI specification inference` | 18/11/2026 | 827 | 25 | 4 (Yandrapally et al.; Chen et al.; Levi e Dubin; Decrop et al. — repetido) |
| 5 | Crossref (`query.bibliographic`) | `OpenAPI specification inference` | 18/11/2026 | 213.967 (ranqueamento por relevância, sem filtro booleano) | 20 | 0 (relevante: "OpenAI for OpenAPI", SSRN, não incluído) |
| 6 | Crossref | `inferring REST API specification from traffic` | 18/11/2026 | 9.435.187 | 3 | 0 |
| 7 | Crossref | `REST API documentation inconsistency` | 18/11/2026 | 163.540 | 20 | 0 |
| 8 | Crossref | `OpenAPI conformance implementation` | 18/11/2026 | 579.798 | 20 | 0 |
| 9 | arXiv API (`export.arxiv.org/api/query`) | `all:"specification" AND all:"REST" AND all:"inference"` | 18/11/2026 | 222 | 30 | 3 (Chen et al.; Decrop et al.; Yandrapally et al.) |
| 10 | arXiv API | `abs:OpenAPI AND abs:undocumented` | 18/11/2026 | 4 | 4 | 2 (Decrop et al.; Levi e Dubin) |
| 11 | arXiv API | `abs:"shadow API" OR abs:"shadow endpoints" OR abs:"API9"` | 18/11/2026 | 3 | 3 | 0 (nenhum sobre APIs REST/inventário) |
| 12 | arXiv API | `abs:OpenAPI AND abs:inconsistencies` | 18/11/2026 | 2 | 2 | 2 (Mazhar et al.; Yandrapally et al. — repetido) |
| 13 | arXiv API | `abs:"REST API" AND abs:specification AND abs:"static analysis"` | 18/11/2026 | 4 | 4 | 1 (Chen et al. — repetido) |
| 14 | arXiv API | `all:Respector` | 18/11/2026 | 2 | 2 | 1 (Lercher et al.) |
| 15 | Crossref (busca dirigida por título, rows=5) | `Generating REST API Specifications through Static Analysis` | 18/11/2026 | 8.527.634 (ranqueado) | 5 | 2 (Huang et al.; Singh et al.) |
| 16 | Crossref (dirigida) | `Example-driven Web API specification discovery` | 18/11/2026 | 1.678.924 (ranqueado) | 5 | 1 (Ed-douibi et al.) |
| 17 | Crossref (dirigida) | `SpyREST automated RESTful API documentation HTTP proxy` | 18/11/2026 | 688.999 (ranqueado) | 5 | 1 (Sohan et al.) |
| 18 | Crossref (dirigida) | `Towards extracting web API specifications from documentation` | 18/11/2026 | 10.284.216 (ranqueado) | 5 | 1 (Yang et al.) |
| 19 | Crossref (dirigida) | `inconsistencies REST API documentation implementation detection` | 18/11/2026 | 2.301.191 (ranqueado) | 5 | 0 |
| 20 | Crossref (dirigida) | `RESTAssured formally verifying RESTful API specification conformance` (item visto no resultado da #16) | 18/11/2026 | 138.917 (ranqueado) | 5 | 0 (relatório técnico sem resumo acessível) |
| 21 | OpenAlex | `REST API specification mining` | 18/11/2026 | 21.018 | 25 | 1 (versão ICSME 2026 do RESTSpecIT — atualiza a 2.3) |
| 22 | OpenAlex | `shadow API endpoints undocumented` | 18/11/2026 | 176 | 15 (a listagem foi interrompida no 16º item por erro de codificação do script) | 1 (**Amoruso et al., 2026 — ver 2.11**) + 1 marginal (Gupta, 2024) |
| 23 | OpenAlex | `OpenAPI specification static analysis generation` | 18/11/2026 | 1.050 | 25 | 0 novos (Huang et al., Lercher et al., Chen et al., Mazhar et al. — repetidos) |

**Observações de protocolo (para a Metodologia ou para um apêndice):**

- **dblp** não pôde ser consultado. A API (`dblp.org/search/publ/api`) devolveu, em 18/11/2026, uma página anti-robô (Anubis) no lugar do JSON. Não foi contornada, e nenhuma contagem do dblp é reportada.
- **Semantic Scholar** limitou a taxa (HTTP 429) depois da primeira consulta. As consultas 2 e 3 não retornaram dados mesmo com novas tentativas e foram abandonadas. Consultas pontuais por DOI funcionaram e serviram para conferir dois resumos.
- **OpenAlex** também limitou a taxa ("Anonymous search is temporarily rate-limited"). As consultas 21–23 só voltaram depois de várias tentativas. Estas foram tentadas e **não** retornaram contagem: `REST API documentation inconsistency implementation`, `undocumented API endpoints detection`, `inferring OpenAPI specification from HTTP traffic` e `web API documentation drift`. Se houver tempo, repetir para fechar o protocolo. As consultas por DOI (`/works/doi:`) funcionaram.
- **Crossref** ordena por relevância e não aplica filtro booleano. O "total reportado" equivale, na prática, a quase todo o índice e não serve como medida de cobertura. Vale reportá-lo assim mesmo, com essa ressalva, ou usar no artigo apenas as contagens de arXiv, OpenAlex e Semantic Scholar.
- As buscas 14–20 foram **dirigidas** (bola de neve: título já conhecido ou citado por outro trabalho) e não exploratórias. O artigo deve dizer isso.
- Google Scholar, IEEE Xplore e ACM DL **não** foram consultados como bases de busca. A página do ACM DL para o PDF de Huang et al. retornou HTTP 403.
- Arquivos brutos das respostas das APIs: não preservados (ficaram em diretório temporário da sessão de busca). As contagens registradas neste relatório são o registro remanescente.

---

## 2. Referências confirmadas

### 2.1 Yandrapally et al. (2023) — APICARV — **mais próximo na linha de inferência de especificação** (na linha de segurança, ver 2.11)

**Referência (ABNT):**
YANDRAPALLY, Rahulkrishna; SINHA, Saurabh; TZOREF-BRILL, Rachel; MESBAH, Ali. Carving UI tests to generate API tests and API specification. *In*: IEEE/ACM INTERNATIONAL CONFERENCE ON SOFTWARE ENGINEERING (ICSE), 45., 2023, Melbourne. **Proceedings** [...]. [*S. l.*]: IEEE, 2023. p. 1971-1982. DOI: 10.1109/ICSE48619.2023.00167.

**URLs conferidas:** https://api.crossref.org/works/10.1109/icse48619.2023.00167 ; https://api.openalex.org/works/doi:10.1109/icse48619.2023.00167 ; https://export.arxiv.org/api/query?id_list=2305.14692 ; texto completo: https://arxiv.org/pdf/2305.14692v1

**Resumo (baseado no resumo e conferido no texto completo da versão arXiv v1):** A ferramenta APICARV navega a aplicação web pela interface, com testes de UI gerados pelo Crawljax ou escritos à mão. Ela captura as chamadas de API e gera uma suíte de testes de API e uma especificação OpenAPI do servidor. Endpoints com parâmetros de caminho são inferidos por um grafo de API (um nó por segmento de caminho), por comparação estrutural de respostas e por *sondagem dirigida* (*directed API probing*). Em sete aplicações de código aberto, a inferência de endpoints teve precisão de 98% e revocação de 56%, contra a especificação OpenAPI existente usada como ground truth.

**Como infere templates de caminho (texto completo, Seção III e Algoritmo 2):** as URLs observadas viram um grafo de segmentos. Dois nós-folha como `/users/user1` e `/users/user2` se fundem numa variável (`/users/{user}`) quando suas respostas são estruturalmente equivalentes (comparação em árvore). Há três tipos de sonda: (i) completar grafos bipartidos, por exemplo gerar `/users/user2/follow` a partir de `/users/user1/follow`; (ii) montar caminhos com chaves e valores extraídos das respostas, por exemplo `/tags/1` a partir de um JSON com `id: 1`; (iii) testar outros métodos HTTP em endpoints já conhecidos.

**Comparação com este trabalho:**
- *Sobreposição real.* (a) Combina tráfego observado com **sondagem ativa** para ampliar o conjunto observado. (b) Mede precisão e revocação contra a especificação declarada. (c) Relata explicitamente endpoints que existem mas não estão na especificação. No `realworld`, a precisão caiu de 1,00 para 0,98 por causa de um endpoint de *health check* encontrado por sondagem, "válido" e "ausente da especificação", que os autores chamam de "potential inconsistency". As operações OPTIONS/HEAD respondem 200 em todos os sujeitos e não estão documentadas. Esse é, na prática, o mesmo fenômeno do `/console` no VAmPI (um "falso positivo" contra o ground truth que na verdade é um endpoint real não declarado), e Yandrapally et al. o observaram em 2023.
- *Diferenças.* (1) O objetivo é **gerar testes e especificação** quando ela falta ou é inconsistente, e não auditar o inventário. Endpoints não declarados aparecem como efeito colateral, não como saída principal. (2) A descoberta é guiada pela **interface** (só encontra o que a UI chama, mais sondas derivadas disso), enquanto o shadowscan faz força bruta por wordlist ancorada nos prefixos declarados e acha caminhos que nenhum cliente chama, como o `/console`. (3) O ground truth é a especificação existente, **suposta correta**. Não há degradação controlada, e um endpoint real não declarado conta como falso positivo. A degradação com sementes fixas do shadowscan resolve justamente isso. (4) A generalização para template usa similaridade de respostas entre instâncias. O shadowscan não infere templates: casa segmento a segmento os caminhos concretos com templates *declarados*, e o template vem da especificação. (5) A detecção de soft 404 do shadowscan (similaridade com linhas de base de caminhos aleatórios) tem equivalente parcial na comparação de respostas do APICARV, mas com outra finalidade (fundir nós, não descartar respostas falsas).
- **Na banca:** citar como o trabalho mais próximo e reconhecer que ele já observou "endpoints válidos ausentes da especificação". A contribuição do shadowscan está em (i) tratar O\D como **saída primária** de auditoria de segurança (API9:2023), (ii) fazer descoberta independente de clientes ou UI e (iii) avaliar com ground truth construído por degradação, o que permite medir separadamente descoberta e diferencial.

### 2.2 Huang et al. (2024) — Respector

**Referência (ABNT):**
HUANG, Ruikai; MOTWANI, Manish; MARTINEZ, Idel; ORSO, Alessandro. Generating REST API specifications through static analysis. *In*: IEEE/ACM INTERNATIONAL CONFERENCE ON SOFTWARE ENGINEERING (ICSE '24), 46., 2024, Lisboa. **Proceedings** [...]. New York: ACM, 2024. p. 1-13. DOI: 10.1145/3597503.3639137.

**URLs conferidas:** https://api.crossref.org/works?query.bibliographic=Generating+REST+API+Specifications+through+Static+Analysis ; https://api.openalex.org/works/doi:10.1145/3597503.3639137 (PDF no ACM DL: HTTP 403; texto completo **não** lido)

**Resumo (baseado no resumo):** Especificações OpenAPI escritas à mão tendem a ficar incompletas ou inconsistentes conforme o software evolui. O Respector usa análise estática e simbólica do código-fonte para gerar a especificação REST. Foi avaliado em 15 APIs reais, com precisão e revocação na inferência de métodos de endpoint, parâmetros, respostas e restrições. Comparadas às especificações fornecidas pelos desenvolvedores, as especificações geradas revelaram muitos métodos de endpoint, parâmetros, restrições e respostas **ausentes**, além de inconsistências entre especificação e implementação.

**Comparação com este trabalho:**
- *Sobreposição real.* É o trabalho cujo resultado mais se parece com "descrição observada × especificação declarada → endpoints não declarados". O resumo afirma que a comparação com as especificações dos desenvolvedores encontrou métodos de endpoint ausentes delas.
- *Diferenças.* (1) É **caixa-branca**: exige o código-fonte (o resumo não diz quais linguagens/frameworks; Lercher et al., 2.5, o comparam em projetos Java/Spring Boot). O shadowscan é caixa-preta e roda contra a API em execução, sem código. Isso importa para inventário: um endpoint registrado por dependência ou modo de depuração, como o console do Werkzeug ativado com `debug=True`, pode não aparecer no código da aplicação. Isso é **hipótese a verificar**, não fato do Respector. (2) Os métodos ausentes são **subproduto** da comparação, e o resumo não diz que essa comparação foi medida com ground truth. (3) Não tem enquadramento de segurança/inventário.

### 2.3 Decrop et al. (2026) — RESTSpecIT

**Referência (ABNT):**
DECROP, Alix; DEVROEY, Xavier; PAPADAKIS, Mike; SCHOBBENS, Pierre-Yves; PERROUIN, Gilles. RESTSpecIT: REST API specification generation with LLM-assisted request mutations. *In*: IEEE INTERNATIONAL CONFERENCE ON SOFTWARE MAINTENANCE AND EVOLUTION (ICSME), 2026, Benevento. **Proceedings** [...]. [*S. l.*]: IEEE, 2026. p. 813-817. DOI: 10.1109/ICSME67971.2026.00090.

(Versão longa: DECROP, A. *et al.* **You can REST now**: automated REST API documentation and testing via LLM-assisted request mutations. arXiv:2402.05102v2, 2025. Pré-print.)

**URLs conferidas:** https://arxiv.org/abs/2402.05102 ; https://export.arxiv.org/api/query?id_list=2402.05102 (a v1, de 07/02/2024, tinha outro título: "You Can REST Now: Automated Specification Inference and Black-Box Testing of RESTful APIs with Large Language Models", segundo o registro do Semantic Scholar na busca #1). Versão publicada encontrada depois, na busca #21: ICSME 2026, p. 813-817 (artigo curto de 5 páginas), conferida em https://api.crossref.org/works/10.1109/icsme67971.2026.00090 e https://api.openalex.org/works/doi:10.1109/icsme67971.2026.00090. O resumo abaixo é o do pré-print; o da versão ICSME não foi lido.

**Resumo (baseado no resumo):** O RESTSpecIT infere a documentação de uma API REST e a testa em caixa-preta usando um LLM. Recebe só o nome da API e uma chave de acesso ao LLM, gera requisições-semente, muta essas requisições com dados vindos do LLM e analisa as respostas. Com DeepSeek V3, GPT-4.1 e GPT-3.5, encontrou em média 88,62% das rotas e 89,25% dos parâmetros de consulta, descobriu "dados de API não documentados" e produziu entradas OpenAPI válidas para outras ferramentas de teste.

**Comparação com este trabalho:**
- *Sobreposição.* É caixa-preta e ativo (envia requisições e interpreta respostas), gera uma descrição observada e mede cobertura de rotas contra uma referência. Também relata itens não documentados.
- *Diferenças.* (1) As rotas candidatas vêm do **conhecimento prévio do LLM** sobre APIs públicas conhecidas, e não de wordlist ancorada na especificação. Isso favorece APIs famosas e não se aplica a APIs internas, que são o alvo típico de shadow endpoints. (2) O resumo não descreve tratamento de soft 404 nem casamento por template. (3) O objetivo é documentar e testar a API, não diferenciar declarado de observado. Pelo resumo, não há saída "O\D".

### 2.4 Yang et al. (2018) — D2Spec

**Referência (ABNT):**
YANG, Jinqiu; WITTERN, Erik; YING, Annie T. T.; DOLBY, Julian; TAN, Lin. Towards extracting web API specifications from documentation. *In*: INTERNATIONAL CONFERENCE ON MINING SOFTWARE REPOSITORIES (MSR), 15., 2018, Gotemburgo. **Proceedings** [...]. New York: ACM, 2018. p. 454-464. DOI: 10.1145/3196398.3196411.

**URLs conferidas:** https://api.crossref.org/works?query.bibliographic=Towards+extracting+web+API+specifications+from+documentation ; https://api.openalex.org/works/doi:10.1145/3196398.3196411 ; https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3196398.3196411

**Resumo (baseado no resumo):** O D2Spec parte de uma página de documentação online, percorre as demais páginas da API e usa aprendizado de máquina para extrair URL base, **templates de caminho** e métodos HTTP. Em 116 APIs, alcançou precisão de 87,1% para URL base, 80,3% de precisão e 80,9% de revocação para templates de caminho e 83,8%/77,2% para métodos HTTP. Em 64 APIs com especificação existente, encontrou inconsistências entre a documentação e essas especificações.

**Comparação com este trabalho:**
- *Sobreposição.* Infere templates de caminho, com precisão e revocação medidas, e compara a descrição extraída com especificações existentes.
- *Diferenças.* A fonte é a **documentação textual**, não a API em execução. As inconsistências achadas ficam entre dois artefatos declarados (documentação × especificação). A deriva entre especificação e implementação, que gera shadow endpoints, não é observada. É útil no artigo como evidência de que especificações e documentação divergem na prática e como referência de métrica para inferência de templates.

### 2.5 Lercher et al. (2027) — AutoOAS

**Referência (ABNT):**
LERCHER, Alexander; JAMNIG, David; MACHO, Christian; BAUER, Clemens; PINZGER, Martin. Generating accurate OpenAPI descriptions from Java source code. **Journal of Systems and Software**, v. 244, art. 113122, fev. 2027. DOI: 10.1016/j.jss.2026.113122.

**URLs conferidas:** https://api.crossref.org/works/10.1016/j.jss.2026.113122 ; https://export.arxiv.org/api/query?id_list=2410.23873 (pré-print arXiv:2410.23873, 31/10/2024, sem o coautor D. Jamnig). Atenção: o Crossref registra a edição de **fev. 2027** e o artigo já está publicado online. Usar o ano que constar no registro do Crossref no momento da citação.

**Resumo (baseado no resumo do pré-print):** Os autores analisam fraquezas de três geradores de OpenAPI (Respector, Prophet e springdoc-openapi) e propõem o AutoOAS, que extrai caminhos de endpoint, métodos HTTP, códigos de resposta e modelos de dados direto do código-fonte Java. Em sete projetos Spring Boot reais, contra um **ground truth construído manualmente**, o AutoOAS teve a maior precisão e revocação. Contra o Respector, segundo melhor, ganhou 39% de precisão e 35% de revocação em parâmetros.

**Comparação com este trabalho:**
- *Sobreposição.* Usa ground truth explícito para avaliar a extração de endpoints, e a especificação gerada poderia ser comparada com a declarada.
- *Diferenças.* É estático, preso a Java/Spring e não faz o diferencial contra a especificação declarada (o resumo não menciona isso). Serve para mostrar que a linha de "geração a partir do código" já se avalia com ground truth, enquanto o diferencial caixa-preta para inventário não aparece nas buscas.

### 2.6 Sohan, Anslow e Maurer (2015) — SpyREST

**Referência (ABNT):**
SOHAN, S. M.; ANSLOW, Craig; MAURER, Frank. SpyREST: automated RESTful API documentation using an HTTP proxy server. *In*: IEEE/ACM INTERNATIONAL CONFERENCE ON AUTOMATED SOFTWARE ENGINEERING (ASE), 30., 2015, Lincoln, NE. **Proceedings** [...]. [*S. l.*]: IEEE, 2015. p. 271-276. DOI: 10.1109/ASE.2015.52.

**URLs conferidas:** https://api.crossref.org/works?query.bibliographic=SpyREST+automated+RESTful+API+documentation+HTTP+proxy ; https://api.openalex.org/works/doi:10.1109/ase.2015.52

**Resumo (baseado no resumo):** Um proxy HTTP intercepta chamadas de exemplo à API e gera documentação RESTful automaticamente a partir dos dados de requisição e resposta. O objetivo é baratear a produção e a manutenção de documentação, que hoje é manual e sujeita a erro.

**Comparação com este trabalho:** É o precursor da inferência **passiva** a partir de tráfego. Só documenta o que algum cliente chama, então um endpoint que ninguém usa, como o `/console`, nunca aparece. Não compara com especificação declarada e o resumo não relata avaliação com ground truth. Serve para contrastar observação passiva com a descoberta ativa do shadowscan.

### 2.7 Ed-douibi, Cánovas Izquierdo e Cabot (2017)

**Referência (ABNT):**
ED-DOUIBI, Hamza; CÁNOVAS IZQUIERDO, Javier Luis; CABOT, Jordi. Example-driven web API specification discovery. *In*: MODELLING FOUNDATIONS AND APPLICATIONS (ECMFA 2017). Cham: Springer, 2017. p. 267-284. (Lecture Notes in Computer Science). DOI: 10.1007/978-3-319-61482-3_16.

**URLs conferidas:** https://api.crossref.org/works/10.1007/978-3-319-61482-3_16 ; https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/978-3-319-61482-3_16 (o volume da LNCS não veio no registro; conferir na página da Springer antes de fechar a referência)

**Resumo (baseado no resumo):** Muitas APIs REST públicas não têm especificação legível por máquina. Os autores propõem um processo guiado por exemplos que gera especificações OpenAPI, por meio de modelos, a partir de exemplos de chamadas à API. Apresentam também uma ferramenta e um repositório comunitário das APIs descobertas.

**Comparação com este trabalho:** Também infere a especificação a partir de exemplos observados de chamadas, mas o resumo não informa como generaliza parâmetros de caminho nem traz avaliação quantitativa. Não compara com especificação declarada. Entra como referência histórica da linha "especificação a partir de exemplos".

### 2.8 Singh et al. (2026) — Speculate; Chen et al. (2026) — OOPS (geração por LLM a partir do código)

**Referências (ABNT):**
SINGH, Krishanu; KARAR, Kushagra; JINDAL, Abhilash; YANG, Guowei. Speculate: generating REST API specifications using LLMs. **Proceedings of the ACM on Software Engineering**, v. 3, n. FSE, p. 503-524, 2026. DOI: 10.1145/3797118.

CHEN, Hao; LI, Yunchun; CHEN, Chen; LIN, Fengxu; LI, Wei. OOPS: automated generation of REST API specification via LLMs. **Journal of Systems and Software**, v. 239, art. 112914, set. 2026. DOI: 10.1016/j.jss.2026.112914.

**URLs conferidas:** https://api.crossref.org/works/10.1145/3797118 ; https://api.openalex.org/works/doi:10.1145/3797118 ; https://api.crossref.org/works/10.1016/j.jss.2026.112914 ; https://export.arxiv.org/api/query?id_list=2601.12735

**Resumos (baseados nos resumos):** O *Speculate* junta análise estática leve com LLMs para gerar especificações REST a partir do código-fonte. Em 19 repositórios, com duas linguagens e três frameworks, superou as ferramentas existentes em precisão e revocação. O *OOPS* usa um fluxo de agentes LLM com grafo de dependências entre arquivos para extrair métodos de endpoint e gerar a OAS. Em 12 APIs reais, com 5 linguagens e 8 frameworks, teve F1 médio acima de 98% na inferência de métodos de endpoint.

**Comparação com este trabalho:** Mostram que gerar especificação a partir do código está ativo e já se avalia com precisão e revocação. Os dois exigem código-fonte, e nenhum resumo menciona diferencial contra a especificação declarada ou foco em endpoints não declarados. Basta citá-los em uma frase como estado da arte recente da linha estática.

### 2.9 Levi e Dubin (2026) — MRG (inferência a partir de tráfego, com viés de segurança)

**Referência (ABNT):**
LEVI, Yarin; DUBIN, Ran. **API security based on automatic OpenAPI mapping**. arXiv:2604.19471, 2026. Pré-print.

**URL conferida:** https://export.arxiv.org/api/query?id_list=2604.19471 (sem journal_ref nem DOI no registro)

**Resumo (baseado no resumo):** O Map Reduce Graph (MRG) aprende sem supervisão a estrutura de uma API HTTP/REST a partir de tráfego real e gera documentação compatível com OpenAPI, reconstruindo rotas, métodos e formatos de parâmetros. Faz atualização em tempo real e detecção de anomalias, inclusive de "comportamentos não documentados ou em evolução", combinando validação por grafo e um *autoencoder* para os payloads. Contra HRAL e FT-ANN, relata até 11,4% a mais de revocação na detecção de ataques.

**Comparação com este trabalho:** É o trabalho de **segurança** mais próximo na inferência de especificação. Também gera um OpenAPI "observado" e fala de comportamento não documentado. Pelo resumo, porém, (1) é **passivo** (depende de tráfego real), (2) não compara com uma especificação declarada e (3) a avaliação mede detecção de ataques, não acurácia de inventário. É pré-print recente: citar com essa ressalva.

### 2.10 (Vizinho metodológico — talvez pertença a outro bloco) Mazhar, Wang e Mäntylä (2026)

**Referência (ABNT):**
MAZHAR, Hamza Bin; WANG, Yuqing; MÄNTYLÄ, Mika V. **Fault injection in OpenAPI specifications for evaluating black-box testing effectiveness**. arXiv:2607.12101, 2026. Pré-print aceito no 37th IEEE International Symposium on Software Reliability Engineering (ISSRE 2026).

**URL conferida:** https://export.arxiv.org/api/query?id_list=2607.12101

**Resumo (baseado no resumo):** Os autores montam uma taxonomia de seis classes de falhas em especificações OpenAPI e as injetam em cinco níveis de severidade em dois benchmarks de microsserviços (TrainTicket e SocialNetwork). Medem o efeito sobre três ferramentas (EvoMaster, RESTler e Schemathesis) por cobertura de código, cobertura da especificação, qualidade de requisição/resposta e diversidade comportamental. Concluem que avaliar só por cobertura subestima o impacto das falhas.

**Comparação com este trabalho:** Não infere especificação, mas é o precedente mais próximo da **validação por degradação de spec**: mutar a especificação de propósito para criar condições conhecidas. O resumo não diz se alguma das seis classes é "remoção de operações", então não afirmar isso sem ler o artigo. Útil para justificar na Metodologia que injetar alterações controladas na especificação é prática já usada na avaliação de ferramentas REST. O propósito difere: lá a especificação degradada é *entrada* de ferramentas de teste; aqui as operações removidas são o *ground truth*.

---

### 2.11 Amoruso et al. (2026) — Zombie APIs — **AMEAÇA PRINCIPAL À ORIGINALIDADE (encontrado no fim da busca)**

**Referência (ABNT):**
AMORUSO, Edward L.; AMORUSO, Paul E.; BROQI, Aurela; ZOU, Cliff C. Zombie APIs: detecting runtime-reachable but deprecated endpoints. *In*: INTERNATIONAL SYMPOSIUM ON NETWORKS, COMPUTERS AND COMMUNICATIONS (ISNCC), 2026, Bristol. **Proceedings** [...]. [*S. l.*]: IEEE, 2026. p. 1-7. DOI: 10.1109/ISNCC70543.2026.11693891.

**URLs conferidas:** https://api.crossref.org/works/10.1109/isncc70543.2026.11693891 ; https://api.openalex.org/works/doi:10.1109/isncc70543.2026.11693891 (texto completo **não** lido)

**Resumo (baseado no resumo):** As ferramentas de teste de API costumam atacar só as interfaces documentadas e supõem que a especificação publicada é completa. Na prática, endpoints obsoletos, não documentados ou ocultos (*zombie APIs*) continuam acessíveis em tempo de execução e ampliam a superfície de ataque. Os autores formalizam *zombie APIs* como **discrepâncias entre o estado de ciclo de vida declarado e o comportamento observável em execução**. Propõem descobrir APIs zumbis e ocultas **a partir só da URL do alvo**, sem depender de especificação completa. O método combina extração de endpoints de artefatos do lado do cliente com **sondagem adaptativa** (mutação de método HTTP, enumeração de versões de API, sondagem "shadow" baseada em cabeçalhos e **análise diferencial de respostas**). Foi avaliado num *testbed* FastAPI controlado e num servidor exposto à Internet que emula um ecossistema real. Relata descoberta de endpoints quase completa (90–100%) e taxa de falsos positivos de 0% (ambientes controlado e real) a 15% (implantação semelhante à produção).

**Comparação com este trabalho:**
- *Sobreposição forte.* É **segurança de inventário de API**, o mesmo enquadramento do API9:2023. Faz **descoberta ativa caixa-preta**. Define o alvo como **diferença entre o declarado e o observado em execução**. Usa **análise diferencial de respostas**, que pode ser análoga ao filtro de soft 404 do shadowscan; não dá para saber sem o texto. Avalia com **ambiente controlado** e mede descoberta e falsos positivos. Das buscas feitas, é o trabalho mais parecido com o shadowscan, mais que o APICARV.
- *Diferenças (até onde o resumo permite afirmar).* (1) As candidatas vêm de artefatos do cliente (JavaScript, por exemplo), versões e métodos, e não de wordlist ancorada nos prefixos de uma especificação OpenAPI. Pelo resumo, o método roda "sem depender de especificação completa", e não está claro se usa a especificação como entrada do diferencial. (2) O foco declarado é o ciclo de vida (endpoints *obsoletos* que continuam alcançáveis), e não a especificação como conjunto declarado. (3) O resumo não fala de ground truth por degradação, de casamento por template nem de separar a métrica de descoberta da do diferencial. (4) Os alvos são outros (FastAPI e um servidor próprio, contra VAmPI e vAPI aqui).
- **Conflito de terminologia (importante para a banca):** neste trabalho, "zumbi" = **D\O** (declarado e não observado). Em Amoruso et al., "zombie API" = endpoint **obsoleto ou não documentado que continua alcançável**, o que está mais perto do "shadow" daqui (O\D). O próprio OWASP API9:2023 trata de versões antigas/obsoletas expostas. O artigo precisa definir os termos explicitamente e citar essa divergência.
- **Ação recomendada:** ler o texto completo antes de fechar a Seção 2 e a afirmação de originalidade, sobretudo a parte de "differential response analysis" e de como eles definem e medem falso positivo.

### 2.12 (Marginal) Gupta (2024) — API drift

**Referência (ABNT):**
GUPTA, Anoop. API drift detection enhancing data protection. **International Journal of Computer Applications**, v. 186, n. 49, p. 47-50, nov. 2024. DOI: 10.5120/IJCA2024924168.

**URLs conferidas:** https://api.crossref.org/works/10.5120/ijca2024924168 ; https://api.openalex.org/works/doi:10.5120/ijca2024924168

**Resumo (baseado no resumo):** Parte de um estudo da Gartner sobre vazamento de dados via APIs e afirma que as várias fases do ciclo de vida, com vários engenheiros envolvidos, aumentam o risco. Propõe detectar vazamento identificando "API drift" e localizar o ponto do vazamento.

**Comparação com este trabalho:** O tema (deriva entre o declarado e o implantado) é vizinho, mas o resumo é vago, o artigo tem 4 páginas e o periódico tem baixa seletividade. Usar no máximo como menção. Não serve de base para afirmações técnicas.

## 3. Tabela comparativa (linhas prontas para o artigo)

| Trabalho | Parte da especificação declarada? | Descoberta ativa? | Detecta não declarados? | Avaliação com ground truth? |
|---|---|---|---|---|
| Yandrapally et al. (2023) — APICARV | Não (gera a especificação; a declarada serve só de ground truth) | Sim (navegação de UI + sondagem dirigida) | Parcialmente (relata endpoint válido ausente da especificação e OPTIONS/HEAD não documentados, como efeito colateral) | Sim (especificação existente; P = 0,98, R = 0,56 em endpoints) |
| Huang et al. (2024) — Respector | Não (gera a partir do código), mas compara com a dos desenvolvedores | Não (análise estática/simbólica) | Sim (métodos de endpoint ausentes da especificação dos desenvolvedores) | Sim para a inferência; não informado para o diferencial |
| Decrop et al. (2026) — RESTSpecIT | Não | Sim (requisições guiadas por LLM, caixa-preta) | Parcialmente ("dados de API não documentados") | Sim (cobertura de rotas: 88,62%) |
| Yang et al. (2018) — D2Spec | Não (parte da documentação textual) | Não | Não (inconsistências documentação × especificação) | Sim (templates: P = 80,3%, R = 80,9%) |
| Lercher et al. (2027) — AutoOAS | Não | Não (estático, Java) | Não informado | Sim (ground truth manual, 7 projetos) |
| Sohan et al. (2015) — SpyREST | Não | Não (proxy passivo) | Não | Não informado no resumo |
| Ed-douibi et al. (2017) | Não | Não (exemplos de chamadas) | Não | Não informado no resumo |
| Singh et al. (2026) — Speculate | Não | Não (estático + LLM) | Não informado | Sim (P/R contra ferramentas existentes) |
| Chen et al. (2026) — OOPS | Não | Não (estático + LLM) | Não informado | Sim (F1 > 98% em métodos de endpoint) |
| Levi e Dubin (2026) — MRG | Não | Não (tráfego real) | Parcialmente ("comportamentos não documentados" como anomalia) | Sim, mas para detecção de ataques |
| Amoruso et al. (2026) — Zombie APIs | Não está claro no resumo ("sem depender de especificação completa"; diferença declarado × observado no ciclo de vida) | Sim (sondagem adaptativa caixa-preta + extração de artefatos do cliente) | Sim (objetivo principal: endpoints zumbis/ocultos) | Sim (testbed controlado; descoberta de 90–100%, FP de 0–15%) |
| **Este trabalho — shadowscan** | **Sim** | **Sim (wordlist ancorada + filtro de soft 404)** | **Sim (O\D é a saída principal)** | **Sim (degradação com sementes; P = 1,00 em 30 execuções)** |

---

## 4. NÃO CONFIRMADO

Trabalhos que apareceram nas buscas ou foram lembrados como candidatos, mas **não** entram como referência confirmada:

1. **"RESTAssured: Formally Verifying RESTful API Specification Conformance in Server-side Web Applications"** (Ye Shu, DOI 10.36934/tr2024_234). O Crossref e o OpenAlex confirmam a existência do registro (relatório técnico), mas sem resumo, local de publicação ou ano consistente. Pelo título, trata de conformidade especificação–servidor, o que interessa diretamente. Não usar sem ler o documento.
2. **"OpenAI for OpenAPI: Automated generation of REST API specification via LLMs"** (SSRN, DOI 10.2139/ssrn.6140637). Só o título foi visto no Crossref. Pode ser versão SSRN do OOPS (títulos parecidos), mas isso não foi verificado.
3. **"LRASGen: LLM-based RESTful API Specification Generation"** (Deng et al., arXiv:2504.16833). Visto só na lista de resultados do arXiv. O resumo não foi lido.
4. **"Generating a Formalized REST API Definition Language for a Dynamic Framework Without Annotations Using Static Analysis Tools"** (Usova, EDM 2023, DOI 10.1109/edm58354.2023.10225100). Só o título foi visto no Crossref.
5. **"DualMine: Static-Dynamic REST API Constraint Discovery with Dual Validation"** (Nguyen et al., arXiv:2609.27806). Só o resumo resumido pelo feed foi visto. Trata de restrições, não de endpoints. Fora de escopo provável.
6. **"Detecting HTTP Status Code Misuses in REST APIs via Static and Dynamic Analysis"** (Decrop et al., arXiv:2609.12770). Só o título e um resumo de uma linha. Fora do escopo do bloco.
7. **"Internal APIs Are All You Need: Shadow APIs, Shared Discovery…"** (Tham et al., arXiv:2604.00694). Usa "shadow APIs" em **outro sentido** (endpoints internos de sites para agentes). Não usar como referência de API9. Se citado, deixar clara a diferença de sentido.
8. **Prophet** e **springdoc-openapi**, citados por Lercher et al. Não foram buscados individualmente.
9. **Consultas ao dblp**: nenhuma. O acesso por API foi bloqueado por anti-robô (ver protocolo).

---

## 5. Risco de sobreposição

**Atualização (fim da busca):** a consulta #22 no OpenAlex trouxe **Amoruso et al. (2026)** (seção 2.11). Ele muda a avaliação abaixo: é um trabalho revisado (ISNCC 2026, IEEE) que faz descoberta ativa caixa-preta de endpoints ocultos/não documentados, com enquadramento de segurança, diferença declarado × observado e avaliação em ambiente controlado. A afirmação de originalidade **não** pode ser "primeira ferramenta a detectar endpoints não declarados por descoberta ativa". O que ainda parece diferenciar o shadowscan (sujeito a confirmar no texto completo de Amoruso et al.): (i) a especificação OpenAPI como conjunto declarado D, de forma explícita, com casamento por template; (ii) a descoberta ancorada nos prefixos declarados; (iii) a validação por degradação de especificação com sementes, que dá ground truth exato, e a separação entre métrica fim a fim e métrica do diferencial isolado; (iv) o caso documentado do `/console` num ambiente de referência de ensino.

**Avaliação (buscas 1–20; ler junto com a atualização acima):** nas buscas 1–20 acima, feitas em 18/11/2026 no Semantic Scholar (parcial), OpenAlex, arXiv e Crossref, **não foi encontrado** trabalho que faça o processo completo deste TCC: (a) partir de uma especificação OpenAPI declarada, (b) construir por **descoberta ativa caixa-preta e independente de clientes** um conjunto observado de endpoints, (c) usar a diferença O\D como **saída principal** de detecção de endpoints não declarados (API9:2023) e (d) medir essa detecção com **ground truth controlado**.

Ainda assim, há trabalhos que chegam perto, e a redação precisa reconhecê-los:

- **Yandrapally et al. (2023)** é a ameaça mais séria. A ferramenta deles também sonda ativamente, também mede precisão e revocação contra a especificação existente e **também relata endpoints reais ausentes da especificação**, incluindo um *health check* achado por sondagem e tratado como "potential inconsistency". A frase "nenhum trabalho detecta endpoints não declarados comparando com a especificação" seria **falsa**. A redação defensável é que, nesses trabalhos, endpoints não declarados aparecem como *subproduto* da inferência e são contados como falsos positivos contra a especificação tomada como verdade. Aqui eles são o objeto da detecção, e a avaliação por degradação permite distinguir "não declarado real" (o `/console`, tratado na D9) de erro da ferramenta.
- **Huang et al. (2024)** também encontra "métodos de endpoint ausentes" das especificações dos desenvolvedores, mas por análise estática do código. A diferenciação é caixa-branca × caixa-preta e o enquadramento de segurança/inventário.
- **Decrop et al.** e **Levi e Dubin** falam de comportamento ou dados "não documentados" a partir de observação, mas (pelos resumos) sem diferencial explícito contra a especificação declarada.
- A busca no arXiv por `shadow API`/`shadow endpoints`/`API9` (#11) não trouxe nada sobre inventário de APIs REST, mas a mesma ideia no OpenAlex (#22) trouxe Amoruso et al. **A literatura sobre o tema existe e é de 2026.** Também apareceram no #22 títulos de revisão, como *Security testing of RESTful APIs: approaches and research challenges* (Computer Science Review, 2026, DOI 10.1016/j.cosrev.2026.101043), que **não** foram conferidos e podem citar outros trabalhos próximos. dblp, IEEE Xplore, ACM DL e Google Scholar não foram consultados, e o Semantic Scholar foi consultado parcialmente.

**Sugestão de redação para a afirmação de originalidade:** "Nas buscas realizadas (Seção X), não foi encontrado trabalho que use a diferença entre a superfície observada por descoberta ativa e a especificação declarada como mecanismo principal de detecção de endpoints não declarados, avaliado com ground truth controlado. Yandrapally et al. (2023) e Huang et al. (2024) relatam endpoints ausentes das especificações como subproduto da inferência de especificações, o que corrobora a relevância do problema." **Essa sugestão precisa ser revista por causa de Amoruso et al. (2.11):** acrescentar algo como "Amoruso et al. (2026) também descobrem ativamente endpoints não documentados com foco no ciclo de vida, mas [diferença a confirmar no texto completo]; este trabalho se distingue pelo uso explícito da especificação OpenAPI como conjunto declarado e pela avaliação por degradação controlada da especificação."

**Ponto para a banca (D3/D8):** o casamento por template é uma *direção oposta* à inferência de templates. O APICARV e o D2Spec **inferem** templates a partir de instâncias (fundindo `/users/user1` e `/users/user2` por similaridade de resposta ou por aprendizado de máquina). O shadowscan **recebe** os templates da especificação declarada e só verifica se um caminho concreto é instância de algum deles. Por isso evita o erro de generalização que o APICARV mede como "duplicação" (fator médio de 0,85 em caminhos após a fase de carving e 0,83 após a sondagem; Tabela IV do pré-print). Em compensação, um endpoint não declarado com segmento variável aparece no O como vários caminhos concretos, e não como um template. Isso já está ligado à limitação de contagem por caminho único listada no CLAUDE.md, §5.
