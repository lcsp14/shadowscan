# Auditoria de citações, referências e consistência interna — `artigo-rascunho-v1.md`

Auditoria independente feita em 18/11/2026 sobre o corpo do artigo (Resumo → Considerações finais) e a lista de Referências. Trechos entre ⟦…⟧ foram ignorados.

**Atenção:** o arquivo foi alterado durante a auditoria (gravação às 01:32, com §2.4/§2.5 reescritas e uma nota de rodapé acrescentada na Tabela 2). Os números de linha abaixo seguem a versão **posterior** a essa alteração. Da linha ~205 em diante, eles são uma unidade maiores que os da versão v1.8 original.

Fontes efetivamente lidas:
- **Texto integral:** NIST SP 800-228-upd1 (PDF da NIST); Yandrapally et al. (arXiv 2305.14692); D2Spec (arXiv 1801.08928, versão arXiv com título diferente do MSR); Ware, Klein e Nelson (arXiv 1102.0930); Bar-Yossef et al. (PDF no site do autor, Technion); Castagnaro, Conti e Pajola (arXiv 2404.14138); Arcuri (arXiv 1901.01538, versão anterior do EvoMaster).
- **Páginas oficiais:** OWASP API9:2023 e demais páginas da edição; OpenAPI 3.0.3; documentação do difflib (3.14), do Werkzeug (debug, 3.1.x), do ZAP OpenAPI e do Nuclei (input formats).
- **Repositórios:** READMEs e releases no GitHub (ffuf, gobuster, kiterunner, nuclei, zaproxy, VAmPI, vAPI, SecLists).
- **Metadados:** Crossref e OpenAlex, com os resumos.
- **Só pelo resumo:** Amoruso et al. (IEEE, sem acesso), Huang et al. (ACM, bloqueado por proteção anti-bot) e Kim et al. (idem).
- **Dados de execução:** o CSV `runs/exp_*_principal/metricas_recalculadas.csv`, para a Tarefa 3.

---

## 1. Resumo executivo

### Contagem por classificação (58 linhas na tabela da seção 2)

| Classificação | Qtde |
|---|---|
| CONFERE | 36 |
| CONFERE COM RESSALVA | 13 |
| NÃO CONFERE | 6 (inclui a linha da Tabela 2, por causa do EvoMaster) |
| NÃO VERIFICÁVEL | 2 (Wazlawick ×2) + 1 parcial (Tabela 1) |

### Problemas por gravidade

#### GRAVE (fato errado, atribuição indevida ou contradição com os próprios dados)

1. **L161 — Castagnaro, Conti e Pajola (2024) + "origem de todos os falsos negativos".** O texto diz: "O resultado confirma a limitação de cobertura das listas, que é a origem de todos os falsos negativos deste trabalho (Seção 6.5)". O erro é duplo:
   - O trabalho citado não mede cobertura. A premissa dele é a **ineficiência** ("enormous quantities of trials for a small amount of success"), e o resultado é um ganho médio de 969% do método com LM.
   - Pelos próprios dados do artigo, a wordlist **não** é a origem de todos os FN. No VAmPI, ela responde por 16 dos 26; os outros 10 vêm do prefixo parametrizado (4) e da subárvore `/books` (6). No vAPI, responde por 3 dos 14; os demais vêm da perda de âncora (8) e da resposta `500 {}` indistinguível (3).
   - A frase contradiz §6.5, §7.4 e §7.7.
2. **L35 (Resumo), L596 (QP3) e L650 (A13): "a queda de revocação com N maior decorre, em sua maior parte, da erosão de âncoras… nos dois alvos".** Vale para o VAmPI: 0,10 de uma queda de 0,13, ou 77%. **Não vale para o vAPI.** A queda observada é de 0,93 para 0,57 (0,37). Sem perda de âncora, pelos números do próprio texto (L624: 1,00 → 0,80), a queda ainda seria de 0,20. A âncora explica, portanto, cerca de 0,17 de 0,37, ou **45%**. A L650 confunde "8 dos 14 FN" (maioria dos FN) com "maior parte da queda". Pelo CSV: no N=3, 1 FN de âncora; no N=6, 7 de âncora, 3 de `/vapi/user` e 3 de wordlist. Basta reformular: "no VAmPI, a maior parte; no vAPI, cerca de metade".
3. **L167 — D2Spec: "encontrou inconsistências entre a documentação e as especificações de 64 APIs".** A fonte avaliou 64 APIs e achou divergências de template em **21** delas: "for the 64 APIs evaluated, we identified 385 path templates from 21 APIs where GuruSpecs and the documentation were different". Do jeito que está, a frase sugere que as 64 tinham inconsistências.
4. **L649 — A12: "produziu uma divergência de observação em 10 pares de execuções equivalentes".** O correto é **1 dos 10 pares** (L483 e §6.5: N=3, semente 1). Pode ser só erro de digitação, mas inverte o sentido.
5. **L195 — Tabela 2, EvoMaster, coluna "Parte da especificação declarada" = "—".** O EvoMaster usa a definição Swagger/OpenAPI: "the first step, when testing such RESTful service, is to retrieve such Swagger JSON definition" (Arcuri, versão arXiv). A própria L159 inclui o EvoMaster entre as ferramentas que "partem da superfície declarada". O correto é "Sim".

#### MÉDIA (exagero, extrapolação ou afirmação não verificável apresentada como fato)

6. **L675 — "A literatura indica que esse comportamento [colapso de erros numa resposta única] não é raro".** Nenhuma das duas fontes sustenta prevalência:
   - Bar-Yossef et al. (2004) apenas **adotam a convenção** de tratar 5xx como hard-404 no algoritmo deles.
   - Yandrapally et al. (2023) relatam que os servidores **respondiam 200 a OPTIONS** sem a operação estar na especificação, e tratam isso como "specification inconsistency". Não se trata de tratamento de erro. Ler isso como "o tratamento de erros fora do caminho principal costuma ser irregular" é extrapolação.
7. **L172 — OPTIONS/HEAD como "respaldo externo" à D11.** O número 85% → 48% confere. Mas os autores interpretam o fenômeno ao contrário: as aplicações respondem 200 a OPTIONS, o cliente da interface **usa** OPTIONS em 11 endpoints, e eles recomendam **documentar** OPTIONS na especificação. Isso não respalda a ideia de que OPTIONS é ruído a excluir. Convém matizar: "respaldo parcial — os autores atribuem a queda a inconsistência da especificação".
8. **L184 — Amoruso et al.: "seu texto completo não estava em acesso aberto na data da busca".** O OpenAlex registra `is_oa: true`, `oa_status: hybrid` e licença **cc-by** para o DOI 10.1109/ISNCC70543.2026.11693891. O Crossref aponta a licença padrão IEEE. **O autor precisa conferir manualmente no IEEE Xplore.** Se o PDF estiver aberto, o trabalho mais próximo precisa ser lido na íntegra antes da banca, porque a Tabela 2, a L59 e a L212 dependem dele.
9. **L184 — "o único [trabalho acadêmico] que trata diretamente da detecção desses endpoints em APIs REST".** A Tabela 1 (L144) marca **2 pré-prints relevantes** sobre "undocumented endpoint" (inferência a partir de tráfego), que não são discutidos nem citados em lugar nenhum. Ou se discutem esses dois, ou se explica por que não contam. Sem isso, o "único" fica vulnerável.
10. **L59 e L171 — APICARV "contra especificações existentes, tomadas como completas" / "suposta completa".** Os autores escrevem: "we use them with the expectation that they may have some inconsistencies" (Threats to Validity). Melhor dizer "tomadas como *ground truth*", sem "completas".
11. **L626 — "Castagnaro, Conti e Pajola (2024) mostram que a força bruta baseada em wordlists fixas gera muitas tentativas para poucos acertos".** Isso é a **premissa** declarada no resumo deles, não um resultado demonstrado. Trocar por "argumentam" ou "partem da constatação de que". A frase seguinte ("Nos dois casos… o gargalo é a cobertura… e não o critério de decisão") atribui a Castagnaro uma conclusão que o trabalho não formula.
12. **L35, L598 e L643 — "dois endpoints reais" que a especificação omite.** Pela definição operacional do próprio artigo (D1: endpoint = método + caminho), são **6 endpoints em 2 caminhos**, e §6.3 (L505) fala em "seis shadows intrínsecos". O Resumo deve dizer "dois caminhos (seis endpoints)". Um avaliador atento à D1 vai notar a incoerência.
13. **L76 e L220 — Wazlawick (2021).** Não é verificável: não há página citada e o livro não foi acessado. A 3ª ed. (LTC, 2021) só foi confirmada por bibliografia de terceiros (UFPR); não achei ISBN. Antes da entrega, conferir no livro a classificação "pesquisa experimental" e o argumento de que "ferramenta não é resultado", e incluir as páginas.
14. **L141–151 — Tabela 1 (contagens de busca).** Reproduzi "shadow API" = 11 no OpenAlex usando o filtro `title_and_abstract.search`. Com `search=` (texto completo), deu 74. O limite de requisições impediu reproduzir as demais linhas. Como §2.1 afirma que as consultas são repetíveis "com a mesma contagem", o protocolo precisa informar o **campo/filtro exato** de cada base, senão a afirmação não se sustenta.
15. **L492 (vAPI) — falta o F1 bruto ao lado do ajustado.** No vAPI só a precisão bruta é dada. O `resumo.md` tem F1 bruto de 0,44 (N=3) e 0,41 (N=6). O briefing do projeto exige as duas versões em tabelas adjacentes, e o VAmPI tem a Tabela 4, mas o vAPI não tem equivalente.

#### LEVE (formatação, referência cruzada, precisão de redação)

16. **L470** — "colapso das respostas de erro (A2), discutido na §6.5": a discussão está na **§7.7**. A §6.5 só tem uma linha de tabela, que por sua vez remete à §7.7.
17. **L655** — "mas ocorreu no vAPI (ver abaixo)": o item do vAPI está **acima** (L652). Além disso, A2 aparece ao mesmo tempo em "se manifestaram" e em "não se manifestaram". Fundir os dois itens.
18. **L582** — "contra cerca de 35 min nas demais": as duas execuções normais do vAPI com N=3 duraram 2 285 s e 2 329 s, ou **≈ 38 min**. Os 35 min (2 040 s) são a média do grupo N=6. Os extremos 52 e 69 min conferem (3 124 s; 4 156 s).
19. **L620** — "ocorreu duas vezes no desenho (N=6, sementes 3 e 4)": na semente 1 (N=6), `GET /users/v1/_debug` também foi ocultado. Nela, `GET /users/v1/{username}` foi ocultado como tipo `metodo`, de modo que o caminho-template continuou declarado com outro método. Conferir se o casamento da D8 é por caminho ou por (método, caminho). Se for por caminho, foram **três** ocorrências.
20. **L212 × L199** — o texto diz que Respector detecta não declarados "como subproduto", mas a Tabela 2 marca "Sim, por análise de código" na coluna "Endpoints não declarados como objeto". Uniformizar.
21. **L198** — APICARV: "Descoberta ativa: Sim (sondagem dirigida)". A descoberta principal é guiada pela navegação da interface (cliente); a sondagem é complementar. Sugestão: "Parcial (UI + sondagem dirigida)".
22. **Numeração de tabelas.** Tabelas "3b" e "5b" não seguem o padrão ABNT/IBGE de numeração sequencial em algarismos arábicos. Cerca de 10 tabelas não têm número nem título: fatores (§3.4), alternativas (§4.4), "não encontrado" (§5.1), parâmetros (§5.3), N=0 (§6.1), FN do VAmPI e do vAPI (§6.5), §6.6, custo (§6.7, duas). Também falta a linha "Fonte:" nas Tabelas 3 a 5b.
23. **L333** — difflib, "variante, com refinamentos, do *gestalt pattern matching*". A documentação diz "predates, and is a little fancier than" o algoritmo de Ratcliff e Obershelp. Melhor: "anterior a ele e um pouco mais elaborado". Observação metodológica, sem relação com a citação: a doc avisa que, com `autojunk=True` (padrão) e sequências de 200 ou mais itens, elementos com mais de 1% de frequência são tratados como *junk*. Como a comparação usa até 4 000 caracteres, essa heurística atua sobre os corpos. Vale ao menos mencionar como limitação, ou confirmar em D5 se `autojunk=False` foi usado. É só texto: não altera código nem dados.
24. **L456 / ref. PALLETS** — a citação aponta a documentação **3.1.x**, mas o ambiente roda Werkzeug **2.2.3**. O conteúdo citado (PIN, aviso de produção) existe nas duas versões, mas o certo é citar a doc da versão usada ou declarar a diferença.
25. **Ref. OWASP** — a URL aponta a página-lista (`0x11-t10`), enquanto as afirmações de L106 e L117 vêm da página da categoria (`0xa9-improper-inventory-management`). Citar a página específica ou incluir as duas.
26. **Ref. PROJECTDISCOVERY** — a URL redireciona para `https://docs.projectdiscovery.io/opensource/nuclei/input-formats`. Atualizar.
27. **Ref. CHANDRAMOULI; BUTCHER** — a própria NIST recomenda citar como **2025** ("June 2025 — includes updates as of 03-13-2026"; "How to cite: Chandramouli R, Butcher Z (2025)"). Usar 2026 é defensável para o upd1, mas convém explicitar: "2025, atualizado em mar. 2026".
28. **Ref. WARE; KLEIN; NELSON** — o arXiv 1102.0930 é um **relatório técnico** de 24 páginas, e a entrada deveria dizer isso ("Relatório técnico / preprint"). Existe uma versão revisada por pares curta no JCDL 2011 (DOI 10.1145/1998076.1998101), com título diferente. Se essa for usada, conferir os autores.
29. **Ref. AMORUSO** — a entrada ainda tem ⟦CONFERIR⟧. Os metadados conferem com o Crossref.
30. **Ref. MIESSLER et al. (SecLists)** — o repositório recebeu push em 17/11/2026. Para que as "3291 palavras únicas" sejam reproduzíveis, citar o **commit** usado. O hash já está no Apêndice D? Se não estiver, incluir.
31. **Ref. YANG et al.** — os números citados (64 APIs) foram conferidos na versão arXiv, de título diferente ("Automatically Extracting Web API Specifications from HTML Documentation"). Convém confirmar no texto do MSR.

---

## 2. Tabela por citação

Legenda: C = CONFERE; CR = CONFERE COM RESSALVA; NC = NÃO CONFERE; NV = NÃO VERIFICÁVEL.

| Linha | Citação | Afirmação | Fonte consultada | Class. | Observação |
|---|---|---|---|---|---|
| 53 | OPENAPI INITIATIVE, 2020 | Formato legível por máquina que declara caminhos, métodos, parâmetros e respostas | https://spec.openapis.org/oas/v3.0.3 | C | — |
| 55 | CHANDRAMOULI; BUTCHER, 2026 | *Rogue or shadow APIs* para uso interno (depuração, testes, ad hoc), possivelmente não documentadas, que escapam da revisão | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-228-upd1.pdf (§2.1) | C | Literal: "may not be appropriately documented and often bypass standard security review practices". Ano: ver item 27 |
| 55 | OWASP FOUNDATION, 2023 | API9:2023 Improper Inventory Management como categoria própria | https://api-security.owasp.org/editions/2023/en/0x11-t10/ | C | — |
| 57 | ZAP, 2025 | O complemento importa e percorre a definição; não descreve comparação | https://www.zaproxy.org/docs/desktop/addons/openapi-support/ | CR | "spider and import OpenAPI (Swagger) definitions". A ausência foi verificada só nessa página |
| 57 | PROJECTDISCOVERY, 2026 | O Nuclei usa a especificação para gerar requisições e testá-las | https://docs.projectdiscovery.io/opensource/nuclei/input-formats | C | Quase literal: "uses these specifications to generate HTTP requests and test them against the target". A URL redireciona |
| 57 | FFUF, 2026; REEVES, 2025 | Os READMEs não mencionam OpenAPI | README.md dos dois repositórios no GitHub | C | 0 ocorrências de "openapi" e "swagger" |
| 59 | YANDRAPALLY et al., 2023 | Medem contra especificações existentes "tomadas como completas" | arXiv 2305.14692, §IV.D e §IV.F | CR | As especificações são "considered the ground truth", mas os autores esperam "some inconsistencies" |
| 59 | AMORUSO et al., 2026 | Medem em ambientes de teste construídos para esse fim | OpenAlex (resumo) | CR | "FastAPI-based testbed and an Internet-facing server that emulates a real-world API ecosystem"; o resumo também cita FP "in controlled and real-world APIs" |
| 76 | WAZLAWICK, 2021 | A ferramenta não é, em si, o resultado da pesquisa | — (livro não acessado) | NV | Incluir página |
| 94 | FIELDING, 2000 | REST; recursos por URI; operações uniformes | https://ics.uci.edu/~fielding/pubs/dissertation/top.htm (§5.1.5) | CR | "Uniform interface" é uma restrição de interface, não exatamente "conjunto uniforme de operações". Simplificação aceitável |
| 96–100 | OPENAPI INITIATIVE, 2020 | `paths`; templates `{}`; caminhos relativos a `servers` | spec 3.0.3, §4.7.8 | C | "The path is appended (no relative URL resolution) to the expanded URL from the Server Object's url". O VAmPI usa 3.0.1 (irrelevante) |
| 106 | OWASP, 2023 | Acesso por versões antigas / endpoints sem correção; documentação desatualizada; *documentation blindspot* | https://api-security.owasp.org/editions/2023/en/0xa9-improper-inventory-management/ | C | Literal |
| 106 | OWASP, 2023 | A descrição não menciona depuração | idem | C | 0 ocorrências de "debug" |
| 117 | CHANDRAMOULI; BUTCHER, 2026 | *Zombie or deprecated APIs* = obsoletas que continuam acessíveis | NIST, §2.1 | CR | "replaced or superseded… but have not yet been entirely removed". Paráfrase aceitável |
| 117 | AMORUSO et al., 2026 | *Zombie APIs* = obsoletos, não documentados ou ocultos ainda alcançáveis | resumo (OpenAlex) | C | — |
| 117 | OWASP, 2023 | O Top 10 2023 não emprega "shadow" nem "zombie" | 11 páginas da edição 2023 | C | 0 ocorrências em todas |
| 121 | Bar-Yossef et al. (2004) | Soft-404 = inexistente com 200 e substituto; hard-404 = 403/404/410/5xx; URL aleatória no mesmo diretório | https://www.ee.technion.ac.il/people/zivby/papers/decay/decay.pdf §3 | C | Literal. R = 25 letras aleatórias |
| 121 | Ware, Klein e Nelson (2011) | Subconjunto do método, Jaccard > 0,9 | arXiv 1102.0930, §4.1 | C | "subset of the method laid out by Bar-Yossef"; "both similarity coefficients were above 0.9"; string de 20 caracteres |
| 125 | MANNING; RAGHAVAN; SCHÜTZE, 2008, seção 8.3 | P, R e F1 (média harmônica) | Índice da edição online (nlp.stanford.edu/IR-book, §8.3 "Evaluation of unranked retrieval sets"), via busca | C | O site estava fora do ar; confirmado pelo título da seção e por resumos |
| 141–151 | Tabela 1 | Contagens de busca | api.openalex.org; export.arxiv.org | NV (parcial) | Só "shadow API" = 11 foi reproduzido (filtro title_and_abstract). Ver item 14 |
| 159 | Golmohammadi, Zhang e Arcuri (2024) | 92 artigos; interesse crescente a partir de 2017 | Crossref (resumo) | C | Literal |
| 159 | ATLIDAKIS; GODEFROID; POLISHCHUK, 2019 | Analisa a especificação e gera sequências inferindo dependências | OpenAlex (resumo) | C | — |
| 159 | ARCURI, 2019 | Algoritmo evolutivo guiado por cobertura de código | Crossref (resumo); arXiv 1901.01538 | CR | Também "fault-finding metrics". Usa Swagger (ver item 5) |
| 159 | Kim et al. (2022) | 10 ferramentas, 20 serviços reais, cobertura e falhas | OpenAlex (resumo) | C | — |
| 161 | ASSETNOTE, 2021 | Rotas a partir de especificações Swagger de várias fontes, incluindo varredura da internet | README do kiterunner | C | "internet wide scan for the 40+ most common swagger paths… GitHub via BigQuery, APIs.guru" |
| 161 | Castagnaro, Conti e Pajola (2024) | Propõe gerar candidatos com LMs | arXiv 2404.14138 | C | — |
| 161 | idem | "Único trabalho localizado sobre essa classe" | — | CR | Afirmação de ausência; a Tabela 1 não registra busca sobre o tema |
| 161 | idem | "O resultado confirma a limitação de cobertura das listas, origem de todos os FN" | arXiv 2404.14138 + CSV dos resultados | **NC** | Item 1 |
| 167 | YANG et al., 2018 | D2Spec infere a partir da documentação | arXiv 1801.08928 | C | — |
| 167 | idem | "Inconsistências … de 64 APIs" | idem, RQ2 | **NC** | 64 avaliadas, 21 com divergência (item 3) |
| 167 | SOHAN; ANSLOW; MAURER, 2015 | Tráfego interceptado por proxy | OpenAlex (resumo) | C | — |
| 167 | HUANG et al., 2024 | 15 APIs; métodos, parâmetros e respostas ausentes | OpenAlex (resumo) | C | "identify many missing end-point methods, parameters, constraints, and responses" |
| 169 | YANDRAPALLY et al., 2023 | Interface + sondagem dirigida; 7 aplicações; P 98%, R 56%; *ground truth* = especificações existentes | arXiv 2305.14692 (resumo; §IV.A; Tab. III) | C | Médias por aplicação |
| 171 | idem | Um endpoint achado por sondagem: 1,0 → 0,98; *health check*; "potential inconsistency" | idem, §IV.D | C | É a precisão de caminho; a de operação cai para 0,95 (Pr*). Aplicação: realworld |
| 172 | idem | OPTIONS/HEAD: 85% → 48%; nenhuma aplicação os tratava corretamente; respaldo à D11 | idem, §IV.D | CR | Números e frase conferem; a interpretação não (item 7) |
| 178 | APICARV / D2Spec | Inferem templates a partir de instâncias (respostas / ML) | arXiv das duas | C | "infers path parameters… from concrete endpoint instances"; "agglomerative hierarchical clustering" |
| 182 | CHANDRAMOULI; BUTCHER, 2026 | Definição de shadow; reconciliação entre especificações declaradas e tráfego; citação "including shadow, orphan, and zombie API endpoints" | NIST, §3.1.x | C | Citação literal correta |
| 182 | idem | "O NIST fala em observar o tráfego" | idem | CR | O mesmo item diz "API discovery tools must be deployed during runtime"; o contraste com "descoberta ativa" é menos nítido do que parece |
| 184 | AMORUSO et al., 2026 | Publicado em set./2026; texto completo não estava em acesso aberto | OpenAlex; Crossref | **NC/verificar** | O OpenAlex diz OA hybrid, cc-by (item 8) |
| 184 | idem | O "único" trabalho acadêmico que trata diretamente do tema | Tabela 1 do próprio artigo | CR | 2 pré-prints marcados como relevantes e não discutidos (item 9) |
| 184 | idem | Definição; parte só da URL; métodos de sondagem; 90–100%; FP 0–15% | OpenAlex (resumo) | C | Tudo literal no resumo |
| 186 | idem | Mesma premissa: especificações supostas completas; o resumo não menciona comparação com OpenAPI nem decomposição | idem | C | A redação atual se limita corretamente ao resumo |
| 194–200 | Tabela 2 | Classificação dos trabalhos | fontes acima | CR/NC | EvoMaster "—" é **NC** (item 5); APICARV "Sim" na descoberta ativa: CR (item 21); Respector: inconsistente com L212 (item 20); demais C |
| 212 | YANDRAPALLY; HUANG; AMORUSO | Detectam não declarados por outras vias | idem | C | — |
| 220 | WAZLAWICK, 2021 | Classificação como pesquisa experimental | — | NV | Já marcado ⟦VERIFICAR⟧ |
| 333 | PYTHON SOFTWARE FOUNDATION, 2026 | ratio = 2M/T; variante do *gestalt pattern matching*; recursão à esquerda e à direita | https://docs.python.org/3.14/library/difflib.html | CR | "Variante" ≠ "predates… fancier than" (item 23) |
| 389 | EREV0S, 2026 | Especificação OpenAPI 3.0.1 escrita à mão; 14 operações em 12 caminhos | GitHub erev0s/VAmPI `openapi_specs/openapi3.yml` | C | Contado: 3.0.1, 12 caminhos, 14 operações |
| 391 | ROOTTUSK, 2025 | Commit 67152695 | API do GitHub | C | 67152695b0ac…, 10/01/2025 (último commit do repositório) |
| 414 | MIESSLER; HADDIX; G0TMI1K, 2026 | `api/objects.txt` e `actions.txt` | raw.githubusercontent (HTTP 200) | CR | Arquivos existem; contagem de 3291 não verificada; fixar o commit (item 30) |
| 456 | PALLETS, 2024 | Console executa código; PIN; "nunca deve ser usado em produção" | https://werkzeug.palletsprojects.com/en/stable/debug/ | C | "The debugger must never be used on production machines". Versão da doc: item 24 |
| 456 | (código-fonte) | `app.py`, linhas 15 e 17, debug deliberado | GitHub erev0s/VAmPI `app.py`; Dockerfile | C | L15: comentário; L17: `debug=True`; o Dockerfile executa `python app.py` |
| 608 | CHANDRAMOULI; BUTCHER, 2026 | A depuração é o primeiro exemplo de *shadow APIs* | NIST §2.1 | C | "(e.g., debugging, testing, ad hoc…)" |
| 608 | Yandrapally et al. (2023) | *Health check* numa das 7 aplicações; perda de precisão de 1,0 para 0,98 | arXiv §IV.D | C | — |
| 608 | ATLIDAKIS et al., 2019 | Explora operações declaradas | resumo | C | — |
| 626 | YANDRAPALLY et al., 2023 | P 98%, R 56%, revocação limitada pela navegação da interface | arXiv §IV.D | C | Os autores atribuem a revocação baixa à cobertura do *crawling* / testes de UI |
| 626 | Castagnaro, Conti e Pajola (2024) | "Mostram" que wordlists geram muitas tentativas para poucos acertos | arXiv 2404.14138 | CR | É premissa, não resultado (item 11) |
| 675 | Bar-Yossef et al. (2004) | Tratavam 5xx como hard-404 | PDF do autor, §3 | C | Literal |
| 675 | idem + Yandrapally | "A literatura indica que esse comportamento não é raro" | idem | **NC** | Item 6 |
| 675 | Yandrapally et al. (2023) | Nenhuma das 7 tratava OPTIONS/HEAD; logo, tratamento de erro irregular | arXiv §IV.D | **NC** (inferência) | A fonte fala de 200 em OPTIONS, não de erro (item 6) |

---

## 3. Tabela de referências (Tarefa 2)

| Entrada | Metadados vs Crossref/fonte | URL / versão | Citada no corpo? | Problemas |
|---|---|---|---|---|
| AMORUSO et al. 2026 | Autores, título, ISNCC 2026 Bristol, p. 1-7 e DOI conferem | — | Sim | ⟦CONFERIR⟧ pendente; situação de OA (item 8) |
| ARCURI 2019 | TOSEM v. 28, n. 1, p. 1-37, jan. 2019 conferem | — | Sim | — |
| ASSETNOTE 2021 | — | 200; v1.0.2 existe (11/04/2021) | Sim | — |
| ATLIDAKIS et al. 2019 | ICSE 41, Montreal, p. 748-758 e DOI conferem | — | Sim | — |
| BAR-YOSSEF et al. 2004 | WWW 13, New York, p. 328-337 e DOI conferem | — | Sim | — |
| CASTAGNARO et al. 2024 | AISec 2024 (no CCS), Salt Lake City, p. 184-195 e DOI conferem | — | Sim | — |
| CHANDRAMOULI; BUTCHER 2026 | Título e DOI conferem; Crossref: 13/03/2026 | — | Sim | A NIST sugere citar como 2025 (item 27) |
| EREV0S 2026 | Último commit em 07/04/2026 | 200 | Sim | O subtítulo vem do README ("a vulnerable API made with Flask"); a descrição do repositório é outra. Aceitável |
| FFUF 2026 | — | 200; v2.3.0 existe (09/09/2026) | Sim | — |
| FIELDING 2000 | Tese de doutorado, UC Irvine, 2000 | — | Sim | Sem URL (opcional) |
| GOLMOHAMMADI et al. 2024 | TOSEM v. 33, n. 1, p. 1-41, jan. 2024 conferem (online em nov. 2023) | — | Sim | — |
| HUANG et al. 2024 | ICSE 46, Lisboa, ACM, p. 1-13 e DOI conferem | — | Sim | — |
| KIM et al. 2022 | ISSTA 31, virtual, p. 289-301 e DOI conferem | — | Sim | — |
| MANNING et al. 2008 | CUP 2008 | — | Sim | — |
| MIESSLER et al. 2026 | — | 200; arquivos existem | Sim | Sem commit (item 30) |
| OPENAPI INITIATIVE 2020 | 3.0.3 (2020) | 200 | Sim | — |
| OWASP FOUNDATION 2023 | — | 200 | Sim | URL da página-lista em vez da API9 (item 25) |
| PALLETS 2024 | Doc 3.1.x | 200 | Sim | Versão diferente da do ambiente (item 24) |
| PROJECTDISCOVERY 2026 | v3.11.1 existe (08/08/2026) | 200 após redirecionamento | Sim | Atualizar a URL (item 26) |
| PYTHON SF 2026 | Doc 3.14 | 200 | Sim | — |
| REEVES 2025 | v3.8.2 existe (04/09/2025) | 200 | Sim | — |
| ROOTTUSK 2025 | Último commit em 10/01/2025 | 200 | Sim | — |
| SOHAN et al. 2015 | ASE 30, Lincoln, p. 271-276 e DOI conferem | — | Sim | O título oficial no IEEE tem o sufixo "(N)" (dispensável) |
| WARE et al. 2011 | arXiv 1102.0930 existe (04/02/2011) | 200 | Sim | É relatório técnico (item 28) |
| WAZLAWICK 2021 | 3ª ed., LTC, 2021: confirmado só por fonte secundária | — | Sim | Página ausente (item 13) |
| YANDRAPALLY et al. 2023 | ICSE 45, Melbourne, p. 1971-1982 e DOI conferem | — | Sim | — |
| YANG et al. 2018 | MSR 15, Gotemburgo, p. 454-464 e DOI conferem | — | Sim | Números conferidos na versão arXiv (item 31) |
| ZAP 2025 | 2.17.0 existe (15/12/2025; versão do ZAP, não do add-on) | 200 | Sim | — |

- **Cruzamento citação ↔ lista:** todas as 28 entradas são citadas no corpo, e toda citação do corpo tem entrada. Ano e autor coincidem entre citação e entrada.
- **Ordem alfabética:** correta.
- **Formatação ABNT:** consistente no conjunto. Os únicos problemas claros são os itens 27 e 28.

---

## 4. Consistência interna (Tarefa 3)

**Resumo × tabelas: tudo confere, exceto a afirmação da "maior parte" (item 2) e a contagem "dois endpoints" (item 12).**

| Afirmação | Onde | Verificação |
|---|---|---|
| VAmPI: 20 execuções, P = 1,00, R = 0,80 / 0,67 | Resumo; Tab. 3 | Confere |
| vAPI: P = 1,00, R = 0,93 / 0,57 | Resumo; Tab. 3b; `resumo.md` | Confere |
| Diferencial 32 (VAmPI) e 31 (vAPI) | L594; Tab. 5/5b | 12 + 20 = 32; 14 + 17 = 31. Confere |
| Mecanismos 12 + 7 + 7 + 3 + 3 = 32 | L518 | Confere |
| Precisão bruta 0,28–0,38; F1 0,72–0,96 | L592 | Confere (VAmPI 0,28 / 0,38; vAPI 0,28 / 0,33) |
| FN do VAmPI: 26; wordlist 16 | L644; tabela da §6.5 | 10 + 6 + 4 + 6 = 26. Confere |
| FN do vAPI: 14; âncora 8; wordlist 3; `500 {}` 3 | L624, L650, L651 | Confere com o CSV |
| Contrafactuais 0,77 (VAmPI) e 0,80 / 1,00 (vAPI) | L596, L622, L624 | Confere |
| 0,10 + 0,03 da queda no VAmPI | L622 | Confere |
| "Maior parte da queda" nos dois alvos | L35, L596, L650 | **Não confere no vAPI** (item 2) |
| 9 de 10 pares × "10 pares" | L483 × L649 | **Contradição** (item 4) |
| Requisições do VAmPI ≈ 41 017 | §6.7; CSV | Confere |
| vAPI: 8 h; 158–191 mil requisições; 39 erros (13 + 9 + 17) | L444, L582 | Confere; "35 min" deveria ser ≈ 38 min (item 18) |
| 13 ameaças, 6 manifestadas | L274, L694 | Confere (A1, A2, A3, A10, A12, A13) |
| Numeração de tabelas | 1, 2, 3, 3b, 4, 5, 5b | Sequencial, mas com sufixo "b" e cerca de 10 tabelas sem número (item 22) |
| Figura 1 | L285 | Existe; não há outras figuras citadas |
| Referências cruzadas | — | Seções 4.2, 4.5, 3.2, 3.5, 6.1, 6.5, 7.4, 7.5, 7.7, 6.7 e Apêndices A–D existem e tratam do que é dito. Exceções: L470 → §6.5 (deveria ser §7.7, item 16); L655 "ver abaixo" (item 17); L161 → §6.5 cita a seção correta, mas a afirmação não confere (item 1) |
| Referências às decisões | L251 (D16) etc. | D16 de fato registra que o vAPI roda só sem autenticação. D1–D21 existem no Apêndice A |
