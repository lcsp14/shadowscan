# Bloco de literatura — (a) soft 404; (b) inventário de API, shadow e zombie APIs

Busca realizada em 18/11/2026. Destino no artigo: §1.3, §1.4, §2.3, §4.4 e Introdução (fonte do termo *shadow endpoint*).

Regra seguida: só entra em "Referências confirmadas" o que foi conferido em registro bibliográfico obtido nesta sessão (Crossref, OpenAlex, arXiv, PDF do autor/órgão). Onde li o texto completo, digo isso; onde li só o resumo, digo "baseado no resumo".

---

## 1. Protocolo de busca

Observações sobre as bases:

- **dblp** (`dblp.org/search/publ/api`, e os espelhos `dblp.uni-trier.de` e `dblp.dagstuhl.de`): **bloqueado** por proteção anti-robô (Anubis, "Making sure you're not a bot!"). Nenhuma contagem obtida. Não declarar no artigo que o dblp foi consultado.
- **Semantic Scholar** (`api.semanticscholar.org/graph/v1/paper/search`): **HTTP 429 (Too Many Requests)** em todas as tentativas de busca, mesmo com novas tentativas espaçadas por vários minutos. Nenhuma contagem obtida. A API foi usada só para buscar registros pontuais por DOI (funcionou uma vez). Não declarar no artigo que o Semantic Scholar foi consultado como base de busca.
- **Crossref** (`api.crossref.org/works?query=`): respondeu, mas a busca é por relevância com termos combinados por OU. O "total" reportado conta qualquer registro com qualquer termo (p. ex., "soft" em patologia). Os totais estão registrados por honestidade, mas **não têm valor como medida de cobertura**; triagem feita só nos 20 primeiros.
- **OpenAlex** (`api.openalex.org/works?filter=title_and_abstract.search:"<frase>"`): busca por **frase exata** em título e resumo. Foi a base mais útil e com contagens interpretáveis. Teve limite de taxa intermitente (contornado com novas tentativas).
- **arXiv** (`export.arxiv.org/api/query?search_query=all:"<frase>"`): busca por frase exata em todos os campos, com `opensearch:totalResults`.
- Não foram consultados Google Scholar, IEEE Xplore nem ACM DL como bases de busca. Páginas da IEEE e da ACM foram acessadas só para conferir um DOI.

| # | Base | Termos (exatos) | Data | Total reportado | Triados | Selecionados |
|---|---|---|---|---|---|---|
| 1 | dblp | soft 404; shadow API; zombie API; API inventory; undocumented API; shadow endpoint; Sic transit gloria telae | 18/11/2026 | — (bloqueado) | 0 | 0 |
| 2 | Semantic Scholar | soft 404; soft 404 detection; shadow API; zombie API; API inventory; undocumented API; shadow endpoint; undocumented REST API endpoints discovery | 18/11/2026 | — (HTTP 429) | 0 | 0 |
| 3 | Crossref | soft 404 | 18/11/2026 | 547.819 (OU, irrelevante) | 20 | 0 |
| 4 | Crossref | shadow API | 18/11/2026 | 77.260 (OU) | 20 | 0 |
| 5 | Crossref | shadow endpoint | 18/11/2026 | 60.274 (OU) | 20 | 0 |
| 6 | Crossref | Sic transit gloria telae | 18/11/2026 | 245.833 (OU) | 1 (1º resultado) | 1 (Bar-Yossef et al., 2004) |
| 7 | Crossref | soft 404 detection; zombie API; API inventory management; undocumented API endpoints | 18/11/2026 | falha de resposta/irrelevante (OU) | 20 em "API inventory management" | 0 |
| 8 | arXiv | all:"soft 404" | 18/11/2026 | 1 | 1 | 1 (Garg et al., 2025 — apoio, ver §2.6) |
| 9 | arXiv | all:"shadow API" | 18/11/2026 | 3 | 3 | 0 (sentidos diferentes, ver §5) |
| 10 | arXiv | all:"shadow APIs" | 18/11/2026 | 3 (os mesmos) | 3 | 0 |
| 11 | arXiv | all:"zombie API" / all:"zombie APIs" | 18/11/2026 | 0 / 0 | 0 | 0 |
| 12 | arXiv | all:"API inventory" | 18/11/2026 | 0 | 0 | 0 |
| 13 | arXiv | all:"undocumented API" | 18/11/2026 | 3 | 3 | 1 (Decrop et al. — RESTSpecIT; complementar) |
| 14 | arXiv | all:"undocumented endpoints" / all:"shadow endpoints" / all:"hidden endpoints" | 18/11/2026 | 0 / 0 / 1 (QKD, irrelevante) | 1 | 0 |
| 15 | OpenAlex | "soft 404" | 18/11/2026 | 10 | 10 | 2 (Prieto et al., 2013; Meneses et al., 2012) |
| 16 | OpenAlex | "soft-404" | 18/11/2026 | 10 (os mesmos) | 10 | 0 adicionais |
| 17 | OpenAlex | "shadow API" | 18/11/2026 | 11 | 11 (por título; 2 resumos lidos) | 1 complementar (Marcon; Oliveira, 2026). Ver §3 e §5 |
| 17b | OpenAlex | "shadow APIs" | 18/11/2026 | 11 (os mesmos 11) | 11 | 0 adicionais |
| 18 | OpenAlex | "zombie API" | 18/11/2026 | 1 | 1 | 1 (Amoruso et al., 2026) |
| 19 | OpenAlex | "shadow endpoint" | 18/11/2026 | 1 (capítulo de livro de fotografia, irrelevante) | 1 | 0 |
| 20 | OpenAlex | "zombie APIs" | 18/11/2026 | 1 (o mesmo Amoruso et al.) | 1 | 0 adicionais |
| 20b | OpenAlex | "API inventory" | 18/11/2026 | 6 | 6 (por título) | 0. Um preprint SSRN relevante, mas não revisado: "Orphan API Discovery from Encrypted Network Traffic Through Behavioural Inference" (2026, DOI 10.2139/ssrn.7389041), não conferido além do título |
| 20c | OpenAlex | "undocumented API" | 18/11/2026 | — (limite de taxa persistente após 5 tentativas) | 0 | 0 |
| 21 | Busca web (motor genérico, sem contagem) | "Sic transit gloria telae" Bar-Yossef soft 404 pdf; soft 404 detection paper...; Meneses Furuta Shipman ...; "shadow APIs" "zombie APIs" ...; NIST SP 800-228 ... | 18/11/2026 | n/a | — | serviu para **localizar** PDFs (Bar-Yossef, Ware et al., NIST); todos conferidos depois na fonte |

Fontes obtidas por **acesso direto** (não por busca): página OWASP API9:2023; PDF da NIST SP 800-228 e 800-228-upd1.

---

## 2. Referências confirmadas

### 2.1 Bar-Yossef et al. (2004) — origem do termo e do método de detecção de soft 404

**ABNT:**
BAR-YOSSEF, Ziv; BRODER, Andrei Z.; KUMAR, Ravi; TOMKINS, Andrew. Sic transit gloria telae: towards an understanding of the web's decay. In: INTERNATIONAL CONFERENCE ON WORLD WIDE WEB, 13., 2004, New York. **Proceedings** [...]. New York: ACM, 2004. p. 328–337. DOI: 10.1145/988672.988716.

**URLs conferidas:**
- Registro Crossref: https://api.crossref.org/works/10.1145/988672.988716 (título, 4 autores, anais, p. 328–337, ACM, evento WWW04, New York, 17/05/2004).
- `https://doi.org/10.1145/988672.988716` redireciona para `dl.acm.org` (a ACM DL devolveu 403 ao acesso automatizado).
- **Texto completo lido:** https://www.ee.technion.ac.il/people/zivby/papers/decay/decay.pdf (página do primeiro autor). O título completo no PDF é "Sic Transit Gloria Telae: Towards an Understanding of the Web's Decay". No Crossref, o título registrado é só "Sic transit gloria telae".

**Resumo** (texto completo lido): o artigo propõe uma medida de "decaimento" (*decay*) de páginas web, calculada por passeio aleatório com absorção nas páginas mortas, e mostra que ela indica obsolescência melhor que a simples fração de links mortos. Para identificar páginas mortas, os autores precisaram tratar servidores que não devolvem erro para páginas inexistentes. Por isso definiram o *soft-404* e propuseram um algoritmo de detecção (função `isDeadPage`, Tabela 1 do artigo). Na amostra de 1.000 páginas aleatórias, cerca de 16% dos links mortos apontavam para soft-404. Nos passeios aleatórios, foram cerca de 11%.

**O que diz sobre soft 404 (citações literais do PDF):**

- Definição: *"many web servers today [...] do not return an error code even when they receive HTTP requests for non-existent pages. Instead, they return an OK code (200) and some substitute page; typically, this substitute is an error message page or the home-page of that host or even some completely unrelated page. We call such non-existent pages that behave as above 'soft-404 pages'."* (Seção 3)
- *"Loosely speaking, a soft-404 page is a non-existent page that does not return an error code. In contrast a hard-404 page is a non-existent page that returns an error code of 403, 404, or 410, or any code of the form 5xx."*
- Introdução: *"these type of substitutions, called 'soft-404s' account for more than 15% of the dead links."*
- Método: *"The algorithm detects whether u is a soft-404 page or not by 'learning' whether the web server of u.host produces soft-404 at all. This is done by asking for a page r, known with high probability not to exist on u.host. It then compares the server behavior when asked for r, with its behavior when asked for u."*
- URL aleatória **no mesmo diretório**: *"we choose a URL, which has the same directory as u, and whose file name is a sequence of R random letters (in our experiments we choose R = 25)"*. A justificativa: *"in large hosts different directories are controlled by different web servers, and therefore may exhibit different responses to requests for non-existent pages"* (exemplo: `www.ibm.com/blablabla` dá 404, mas `www.ibm.com/us/blablabla` devolve a home de `/us`).
- Comparação: o algoritmo compara a URL final após redirecionamentos, o número de redirecionamentos e o conteúdo. A similaridade aproximada é medida por *shingling* (ref. [8] do artigo: Broder et al., WWW 1997). A justificativa: *"testing near-identity (as opposed to complete identity) may be important, because sometime the web server embeds the non-existing URL u in the text of the page it returns or does other minor changes."*
- Limitação admitida: a heurística falha para a página raiz de domínio "estacionado" (*parked*). A raiz de um site nunca é classificada como soft-404.

Nota técnica: na extração de texto do PDF, os símbolos "≠" das condições do pseudocódigo se perderam e aparecem como "=". Ao citar as condições exatas de `isDeadPage`, conferir visualmente no PDF.

**Comparação com este trabalho:**
- **É o antecessor direto do D5/D6.** O shadowscan também (i) aprende o comportamento de "não encontrado" do servidor requisitando caminhos aleatórios inexistentes; (ii) compara o candidato com essas respostas por similaridade aproximada, não por igualdade exata; (iii) usa um baseline no **diretório pai** (D6), que corresponde à escolha de Bar-Yossef et al. de gerar `r` em `u.parent`; (iv) neutraliza o eco do caminho no corpo, motivação que o artigo de 2004 já explicita.
- **Diferenças:** (a) Bar-Yossef et al. usam *shingling* e também comparam a cadeia de redirecionamentos. O shadowscan usa `difflib.SequenceMatcher` com limiar de 0,90 após normalização explícita do eco, e não usa a cadeia de redirecionamentos como sinal. (b) O contexto deles é a classificação de links da web (páginas HTML). O deste trabalho é a descoberta de endpoints de API REST com respostas JSON. (c) O D6 trata um caso que não existe no cenário de 2004: um caminho que casa com um **template parametrizado** (`/users/v1/{username}`), em que "não encontrado" vindo do template é prova de existência da rota, não de ausência.
- **Ponto sensível para o §1.4 do rascunho.** Na definição de Bar-Yossef et al., soft-404 é a página inexistente que **não** devolve código de erro. Respostas 5xx (e 403/404/410) são **hard-404**. O rascunho atual diz que o soft 404 inclui "200 com corpo de erro, 500, 401". O caso do vAPI (500 `{}` para qualquer caminho) **seria um hard-404** na taxonomia original, e o problema prático é outro: o 500 não distingue rota inexistente de rota existente com erro. Recomendação: no §1.4, citar a definição original (200 + página substituta) e dizer explicitamente que este trabalho **generaliza** o conceito para "qualquer resposta a recurso inexistente que não seja distinguível pelo código de status". Isso evita uma arguição fácil.

### 2.2 Ware, Klein e Nelson (2011) — mesmo esquema, com limiar 0,9 de similaridade

**ABNT:**
WARE, Jeb; KLEIN, Martin; NELSON, Michael L. **An evaluation of link neighborhood lexical signatures to rediscover missing web pages**. [S. l.]: arXiv, 2011. Relatório técnico. arXiv:1102.0930 [cs.IR]. Disponível em: https://arxiv.org/abs/1102.0930. Acesso em: 18 nov. 2026.

**URLs conferidas:** https://arxiv.org/abs/1102.0930 (metadados: autores, submissão em 04/02/2011, comentário "technical report", sem *journal-ref*). PDF lido em https://arxiv.org/pdf/1102.0930.

**Resumo** (texto lido nas partes relevantes): o trabalho constrói "assinaturas lexicais" de páginas desaparecidas a partir das páginas que apontam para elas (*backlinks*), para reencontrá-las por busca. Na limpeza dos dados, aplica um filtro de soft 404.

**O que diz sobre soft 404 (citações literais):**
- *"To determine if a page was a soft 404, we used a subset of the method laid out by Bar-Yossef, Broder, Kumar, and Tomkins [2]."*
- Os autores requisitam a URI original e duas variantes com uma cadeia aleatória de 20 caracteres, uma inserida após a primeira barra e outra após a última. Medem a similaridade com o **coeficiente de Jaccard** sobre palavras únicas: *"If both similarity coefficients were above 0.9, then the original URI was deemed to be a soft 404 and discarded."*
- Também: *"If the first modified URI returned a HTTP error code, then the page could not be a soft 404"*. É o mesmo princípio do "o servidor dá hard-404 nesse diretório".

**Comparação com este trabalho:** é o precedente mais próximo do **limiar de 0,90**. Os autores usam o mesmo princípio (baseline aleatório), o mesmo limiar numérico e dois baselines de profundidades diferentes (raiz e diretório do recurso), análogos aos baselines aleatórios na raiz e ao baseline do pai (D6) do shadowscan. Diferem na medida: Jaccard sobre conjuntos de palavras, contra a razão do SequenceMatcher sobre sequências de caracteres. Serve para justificar no artigo que 0,90 não é um limiar arbitrário. Pode-se dizer que é um valor já empregado na literatura com o mesmo propósito, desde que se registre que a métrica de similaridade é outra. Cuidado: é um **relatório técnico no arXiv**, não um artigo revisado por pares. Cite-o como tal.

### 2.3 Prieto, Álvarez e Cacheda (2013) — detecção de soft 404 por conteúdo e aprendizado de máquina

**ABNT:**
PRIETO, Víctor M.; ÁLVAREZ, Manuel; CACHEDA, Fidel. Analysis and detection of Soft-404 pages. In: INTERNATIONAL CONFERENCE ON INNOVATIVE COMPUTING TECHNOLOGY (INTECH 2013), 3., 2013. **Proceedings** [...]. [S. l.]: IEEE, 2013. p. 217–226. DOI: 10.1109/INTECH.2013.6653695.

**URLs conferidas:** https://api.crossref.org/works/10.1109/intech.2013.6653695 (autores, título, evento, p. 217–226, ago. 2013, IEEE); https://api.openalex.org/works/doi:10.1109/intech.2013.6653695 (resumo).

**Resumo** (baseado no resumo): os autores mediram que 7,35% dos servidores web respondem 200 a requisições de documentos desconhecidos. Propõem o **Soft404Detector**, que combina heurísticas baseadas no **conteúdo** da página com um classificador **C4.5** (árvore de decisão), treinado num conjunto de dados de soft-404 construído pelos autores. Relatam precisão 0,992 e revocação 0,980.

**O que diz sobre soft 404:** *"Some web servers do not always use the appropriate HTTP response code for dead links [...] These web pages are known as Soft-404 pages."* (resumo)

**Comparação com este trabalho:** representa a linha **supervisionada e baseada no conteúdo da própria página**. O shadowscan segue a linha **comparativa** de Bar-Yossef et al., que não exige rótulos nem treino e se adapta a cada servidor, porque o baseline é gerado no próprio alvo. Para APIs REST, com corpos JSON curtos e sem os indícios textuais típicos de páginas HTML de erro, um classificador treinado em páginas web não se transfere diretamente. Isso justifica descartar a abordagem por aprendizado. Pode entrar como linha na tabela de "alternativas descartadas" do §4.4.

### 2.4 Amoruso et al. (2026) — trabalho relacionado direto (zombie/hidden APIs em REST)

**ABNT:**
AMORUSO, Edward L.; AMORUSO, Paul E.; BROQI, Aurela; ZOU, Cliff C. Zombie APIs: detecting runtime-reachable but deprecated endpoints. In: INTERNATIONAL SYMPOSIUM ON NETWORKS, COMPUTERS AND COMMUNICATIONS (ISNCC), 2026. **Proceedings** [...]. [S. l.]: IEEE, 2026. p. 1–7. DOI: 10.1109/ISNCC70543.2026.11693891.

**URLs conferidas:** https://api.crossref.org/works/10.1109/isncc70543.2026.11693891 (autores, título, evento, p. 1–7, set. 2026, IEEE); https://api.openalex.org/works/doi:10.1109/isncc70543.2026.11693891 (resumo); `https://doi.org/10.1109/isncc70543.2026.11693891` redireciona para https://ieeexplore.ieee.org/document/11693891/. Texto completo **não** lido (acesso pago).

**Resumo** (baseado no resumo): os autores observam que as ferramentas de teste de API visam vulnerabilidades em interfaces documentadas e *"assume that published specifications are complete"*. Chamam de *zombie APIs* os *"deprecated, undocumented, or hidden endpoints [...] accessible at runtime"* e os formalizam *"as discrepancies between declared lifecycle states and observable runtime behavior"*. O método descobre endpoints a partir de uma URL alvo, sem depender de especificação completa. Combina extração de endpoints de recursos do cliente (*client-side*) com sondagem adaptativa: mutação de método HTTP, enumeração de versões, *"header-based shadow probing"* e *"differential response analysis"*. Os autores avaliam num *testbed* FastAPI e num servidor exposto à Internet. Relatam descoberta de 90–100% e falsos positivos de 0% a 15%.

**Comparação com este trabalho:**
- É o trabalho acadêmico **mais próximo** encontrado: mesma motivação (especificação incompleta e endpoints acessíveis fora dela) e mesmo alvo (REST). **Precisa ser citado no §2.3**, senão a banca pode apontar a omissão.
- **Diferenças defensáveis** (com base só no resumo; confirmar no texto completo, se houver acesso pela instituição): (i) a fonte de candidatos deles são artefatos do cliente e enumeração de versões; a do shadowscan é uma wordlist mais a especificação; (ii) eles se concentram no ciclo de vida (obsoleto ainda ativo); o shadowscan, na diferença de conjuntos O\D em relação à spec; (iii) a avaliação do shadowscan usa **degradação controlada da especificação** com ground truth exato e métricas fim a fim e do diferencial isolado. Pelo resumo, não é possível afirmar que eles fazem algo equivalente.
- **Conflito terminológico:** neste artigo, "zombie" engloba também endpoints *não documentados* e *ocultos*, o que se sobrepõe ao que este TCC chama de **shadow**. Ver §3.

### 2.5 NIST SP 800-228-upd1 (2025, atualizada em 2026) — fonte institucional para os termos e para a reconciliação spec × runtime

**ABNT:**
CHANDRAMOULI, Ramaswamy; BUTCHER, Zack. **Guidelines for API protection for cloud-native systems**. Gaithersburg, MD: National Institute of Standards and Technology, 2025. (NIST Special Publication, 800-228-upd1). Inclui atualizações de 13 mar. 2026. DOI: 10.6028/NIST.SP.800-228-upd1.

**URLs conferidas:** PDF lido em https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-228-upd1.pdf (destino de `https://doi.org/10.6028/NIST.SP.800-228-upd1`, conferido). A versão original de jun. 2025 (https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-228.pdf) consta como **retirada (*withdrawn*) em 13/03/2026** e substituída pela upd1. **Cite a upd1.** A forma de citação recomendada pelo próprio documento é *"Chandramouli R, Butcher Z (2025) Guidelines for API Protection for Cloud-Native Systems. [...] NIST SP 800-228-upd1. Includes updates as of March 13, 2026."*

**Resumo** (texto lido nas seções relevantes): guia do NIST para proteção de APIs em sistemas nativos de nuvem. Trata riscos (Seção 2), controles e recomendações numeradas (REC-API-*), entre elas a manutenção de inventário de APIs.

**O que diz sobre shadow/zombie (citações literais, upd1):**
- §2.1 "Lack of Visibility of APIs in the Enterprise Inventory" (p. 7): *"Rogue or shadow APIs: APIs that are defined for internal use (e.g., debugging, testing, ad hoc solutions to business problems) may not be appropriately documented and often bypass standard security review practices."*
- Mesma seção: *"Zombie or deprecated APIs: APIs may have been replaced or superseded by newer systems but have not yet been entirely removed [...]. They risk falling behind the latest security policies and protections."*
- REC-API-4.2 (p. 19): *"Organizational API inventory of all internal (including shadow and Zombie APIs) and external APIs should be maintained."*
- Sob REC-API-8 (p. 20): *"API discovery tools must be deployed during runtime and reconciliation between declared specifications, and live traffic must be performed as part of maintaining an accurate API inventory. The objective of this type of discovery and reconciliation is to identify differences between what is deployed and what should be deployed in production, including shadow, orphan, and zombie API endpoints."*
- A Seção 2 atribui o risco de "lack of visibility of APIs in the enterprise inventory" à ref. [7], que é o OWASP API Security Top 10 2023.

**Comparação com este trabalho:** é a melhor fonte institucional encontrada para o termo, e a última citação descreve quase literalmente o método do shadowscan: reconciliar a **especificação declarada** com o **comportamento em execução** para achar *shadow* e *zombie endpoints*. A diferença é que o NIST fala em "live traffic" (observação passiva de tráfego), e o shadowscan faz **descoberta ativa**. Isso permite posicionar a ferramenta como uma instância ativa, sem acesso ao tráfego, da reconciliação que o NIST recomenda. O exemplo "debugging" da definição de *shadow API* casa diretamente com o achado do `/console` do Werkzeug.

### 2.6 Referências complementares (confirmadas, uso opcional)

- **MENESES, Luis; FURUTA, Richard; SHIPMAN, Frank.** Identifying "soft 404" error pages: analyzing the lexical signatures of documents in distributed collections. In: THEORY AND PRACTICE OF DIGITAL LIBRARIES (TPDL 2012). Berlin, Heidelberg: Springer, 2012. p. 197–208. (Lecture Notes in Computer Science). DOI: 10.1007/978-3-642-33290-6_22.
  Conferido em https://api.crossref.org/works/10.1007/978-3-642-33290-6_22 e no registro do Semantic Scholar por DOI, que confirma autores, título, evento e ano. **Conteúdo não lido**: o resumo foi suprimido pela editora nos registros e o capítulo é fechado. O número do volume da LNCS (7489) e a descrição "classificador Naïve Bayes, precisão 99%, revocação 92%" vieram **apenas de trechos de busca web** e não foram conferidos. Não use esses detalhes sem ler o capítulo.
- **GARG, Kritika; ALAM, Sawood; AYALA, Dietrich; WEIGLE, Michele C.; NELSON, Michael L.** Not here, go there: analyzing redirection patterns on the web. In: ACM WEB SCIENCE CONFERENCE (WebSci '25), 17., 2025. **Proceedings** [...]. New York: ACM, 2025. p. 249–260. DOI: 10.1145/3717867.3717925.
  Conferido no Crossref e no arXiv (2507.22019, versão estendida, lida). Entre 62 mil URIs de páginas 404 personalizadas, *"only 46% returned a 404 Not Found status, while 47% were incorrectly terminated with a 200 OK status despite being 404 error pages."* Útil só como **evidência recente de prevalência** do soft 404. Não propõe método de detecção.
- **WANG, Chao; ZHANG, Yue; LIN, Zhiqiang.** Uncovering and exploiting hidden APIs in mobile super apps. In: ACM SIGSAC CONFERENCE ON COMPUTER AND COMMUNICATIONS SECURITY (CCS '23), 2023. **Proceedings** [...]. New York: ACM, 2023. p. 2471–2485. DOI: 10.1145/3576915.3616676.
  Conferido no Crossref e no arXiv 2306.08134 (resumo). Baseado no resumo: APIs **não documentadas** (*"hidden undocumented APIs"*) em super apps (WeChat, TikTok etc.) são achadas por análise estática e confirmadas por análise dinâmica (ferramenta APIScope). Domínio diferente (APIs de plataforma móvel, não REST), mas é evidência acadêmica de alto nível (CCS) de que **APIs não documentadas são um vetor de ataque real**. Pode reforçar a motivação na Introdução.
- **DECROP, Alix; DEVROEY, Xavier; PAPADAKIS, Mike; SCHOBBENS, Pierre-Yves; PERROUIN, Gilles.** RESTSpecIT: REST API specification generation with LLM-assisted request mutations. In: IEEE INTERNATIONAL CONFERENCE ON SOFTWARE MAINTENANCE AND EVOLUTION (ICSME), 2026. **Proceedings** [...]. [S. l.]: IEEE, 2026. p. 813–817. DOI: 10.1109/ICSME67971.2026.00090.
  Registro Crossref conferido. O resumo lido é o da versão arXiv 2402.05102v2, que tem **título diferente** ("You Can REST Now: Automated REST API Documentation and Testing via LLM-Assisted Request Mutations"). Pelo resumo, a ferramenta infere a documentação de APIs por mutação de requisições com LLM e *"discover undocumented API data"*. Relevante para o bloco 2.2 (inferência de especificação), se ainda não estiver lá.
- **MARCON, Marcelo de Melo; OLIVEIRA, Carlos Eduardo Costa.** Superfície de ataque não inventariada e negação de serviço na camada de aplicação: um modelo de avaliação da exposição de APIs. **Revista Científica SOL21 – Standard Open Literature**, v. 2, n. 1, e2136, 2026. DOI: 10.67553/sol21.v2i1.36.
  Conferido no Crossref (publicado em 14/10/2026) e no OpenAlex (resumo). Baseado no resumo: artigo brasileiro, de *Design Science Research*, que caracteriza *"Shadow APIs e [...] endpoints zumbis como dívida de superfície de ataque"* e conclui que *"a completude do inventário constitui condição de eficácia dos demais controles"*. É periódico novo e de pouca tradição: use, no máximo, como exemplo do uso dos termos em português, não como fonte de definição.

---

## 3. Fonte para o termo "shadow endpoint/API" (e "zombie")

**Resultado honesto:**

1. **O OWASP API9:2023 não usa os termos "shadow" nem "zombie".** Baixei a página https://api-security.owasp.org/editions/2023/en/0xa9-improper-inventory-management/ (destino de `owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/`) e procurei por "shadow" e "zombie": **zero ocorrências**. O mesmo vale para as páginas 0x11-t10, *release notes*, *foreword*, *introduction* e *what's next* da edição 2023. O API9 fala em *"deprecated endpoints"*, *"old API versions or endpoints left running unpatched"*, *"documentation blindspot"* e *"The host's inventory is missing or outdated"*. Também recomenda *"Inventory all API hosts"* e *"Document all aspects of your API such as [...] endpoints"*. A única referência externa da página é *"CWE-1059: Incomplete Documentation"*. **Não atribuir o termo "shadow" ao OWASP.**

2. **Melhor fonte citável: NIST SP 800-228-upd1** (institucional/governamental, não acadêmica revisada por pares; ver §2.5). Redação exata:
   - *"Rogue or shadow APIs: APIs that are defined for internal use (e.g., debugging, testing, ad hoc solutions to business problems) may not be appropriately documented and often bypass standard security review practices."* (§2.1, p. 7)
   - *"Zombie or deprecated APIs: APIs may have been replaced or superseded by newer systems but have not yet been entirely removed [...]."* (§2.1, p. 7)
   - *"[...] identify differences between what is deployed and what should be deployed in production, including shadow, orphan, and zombie API endpoints."* (p. 20)

3. **Fonte acadêmica:** a única encontrada que usa os termos no sentido de segurança e inventário é **Amoruso et al. (2026)** (§2.4). Ela usa **"zombie"**, não "shadow", e numa acepção ampla: *"deprecated, undocumented, or hidden endpoints [...] accessible at runtime"*. Não encontrei artigo acadêmico revisado por pares que defina "shadow API/endpoint" no sentido de API9 (ver §5).

4. Dos 11 resultados do OpenAlex para "shadow API", vários usam o termo em **outros sentidos** e **não servem** como fonte. Os demais são periódicos de pouca tradição que usam o termo de passagem (WAF, *gateways*, revisão sobre bancos, o artigo brasileiro de Marcon e Oliveira na §2.6). Esses foram triados só pelo título, e dois pelo resumo. Os de outro sentido: revendedores não oficiais de acesso a LLMs (Zhang et al., arXiv 2603.01919, aceito no CCS 2026), APIs internas *first-party* por trás de interfaces web (Tham et al., arXiv 2604.00694) e fluxos de suporte ao cliente usados metaforicamente como "shadow APIs" (IEEE Security & Privacy, 2026, DOI 10.1109/MSEC.2026.3685070, só o título visto no OpenAlex). Vale uma frase no artigo reconhecendo que o termo é **polissêmico**.

5. Material de fornecedores (F5, Akamai, Checkmarx, Treblle, Equixly etc.) usa os dois termos com frequência. **Não citar**, salvo como ilustração do uso na indústria. Nenhuma dessas páginas foi conferida em detalhe.

**Consequência para o §1.3 do rascunho (zombie):** a divergência que o autor suspeitava **se confirma**. Na literatura encontrada (NIST; Amoruso et al.), *zombie* = obsoleto/substituído **mas ainda acessível**. Isto é, está ativo, o que no esquema D/O cairia em O, não em D\O. A definição do TCC (D\O, declarado mas **não** respondendo) é **outra coisa**. Na terminologia de outras fontes, isso seria mais próximo de "endpoint documentado inexistente" ou de documentação desatualizada. O NIST também usa "orphan", sem defini-lo nos trechos lidos. Sugestões, a critério do autor: (a) manter "zombie" para D\O e declarar explicitamente que é uma **definição operacional deste trabalho, diferente** do uso no NIST SP 800-228-upd1 e em Amoruso et al.; ou (b) renomear D\O para algo neutro ("declarado não observado"). A opção (a) é a mais barata a 10 dias da entrega e não mexe em código nem em dados, só em texto.

---

## 4. NÃO CONFIRMADO

| Item | Motivo |
|---|---|
| Que Bar-Yossef et al. (2004) sejam a **primeira** ocorrência do termo "soft 404" | O artigo diz "We call such non-existent pages [...] 'soft-404 pages'", o que indica cunhagem ou ao menos formalização, e a Wikipédia (vista só em trecho de busca, não acessada) atribui a origem a eles. Não verifiquei uso anterior em listas ou fóruns. Redação segura: "o termo foi formalizado por Bar-Yossef et al. (2004)" ou "conforme definido por", em vez de "cunhado por". |
| Método e números de Meneses, Furuta e Shipman (2012) (Naïve Bayes, P = 99%, R = 92%; LNCS vol. 7489; TPDL em Paphos, Chipre) | Só em trechos de busca web. Capítulo fechado e resumo suprimido nos registros. Metadados básicos (autores, título, p. 197–208, DOI) **estão** confirmados. |
| Conteúdo integral de Amoruso et al. (2026) | Só o resumo foi lido (IEEE Xplore, acesso pago). As comparações da §2.4 são baseadas no resumo. |
| Prieto, Álvarez e Cacheda (2014), "Soft-404 Pages, a Crawling Problem" | Apareceu no OpenAlex (DOI 10.5281/zenodo.10644204, repositório da Univ. da Coruña), com resumo quase idêntico ao do artigo de 2013. Não consegui confirmar o periódico de publicação (repositório DSpace sem resposta útil; API do Zenodo falhou). Use a versão de 2013 (IEEE). |
| "Orphan API Discovery from Encrypted Network Traffic Through Behavioural Inference" (SSRN, 2026) | Só o título foi visto no OpenAlex. Preprint não revisado. Não conferido. |
| Pacote PyPI `soft404` / `soft-404` (classificador treinado em ~120k páginas) | Visto só em trecho de busca. Não é publicação acadêmica. Não citar. |
| Artigo de 2023 sobre *content drift* em arquivos web canadenses (CEUR-WS vol. 3246) | Visto só em trecho de busca. Não conferido. |
| Definições de shadow/zombie em blogs de fornecedores (F5, Akamai, Checkmarx, Invicti, Equixly) | Não conferidas. Não são fontes acadêmicas. |
| Totais de busca do dblp e do Semantic Scholar | Bases inacessíveis (bloqueio anti-robô e HTTP 429). Não declarar no artigo que foram consultadas. |

---

## 5. Achado sobre a lacuna

Redação conservadora sugerida para o artigo:

> Nas bases consultadas (OpenAlex e arXiv, com busca por frase exata em 18/11/2026), a literatura acadêmica revisada por pares que trata *shadow* ou *zombie APIs* no sentido de gestão de inventário (OWASP API9:2023) mostrou-se escassa e recente. A busca por "zombie API" retornou um único trabalho (AMORUSO et al., 2026). Entre as ocorrências de "shadow API", as publicadas em veículos de maior tradição referiam-se a outros fenômenos, como revendedores não oficiais de acesso a modelos de linguagem. As demais saíram em periódicos de menor tradição e não foram analisadas em profundidade (triagem por título). A principal definição institucional dos termos encontrada é a do NIST SP 800-228-upd1, que recomenda a reconciliação entre especificações declaradas e comportamento em execução para identificar *shadow* e *zombie endpoints*. Não foi localizado, nas bases consultadas, trabalho que avalie essa reconciliação com *ground truth* controlado por degradação de especificação.

Ressalvas que devem acompanhar a afirmação:
- A busca não cobriu IEEE Xplore, ACM DL, Scopus nem Google Scholar diretamente. dblp e Semantic Scholar estavam inacessíveis. **Não** escrever "não há trabalhos" nem "este é o primeiro trabalho". Escrever "não foi localizado, nas bases consultadas".
- Amoruso et al. (2026) é concorrente direto e recente (set. 2026). A lacuna precisa ser formulada **contra** ele, e não ignorando-o: pelo resumo, o diferencial do TCC está na avaliação com ground truth exato por degradação de spec e na separação entre métrica fim a fim e do diferencial isolado, não na ideia de detectar endpoints fora da especificação.
- Sobre soft 404, a lacuna é diferente: a técnica de baseline aleatório existe desde 2004 (Bar-Yossef et al.) e foi reutilizada com limiar 0,9 (Ware; Klein; Nelson, 2011). A contribuição do TCC aqui **não é** a técnica. É a **adaptação** dela a APIs REST: normalização simétrica do eco (D20), baseline do pai combinado com o casamento por template (D6) e generalização para códigos não-200, como o 500 do vAPI. Formular assim no §4.4 é mais seguro e mais honesto.
