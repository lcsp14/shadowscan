# Protocolo da busca bibliográfica

Consolidado em 18/11/2026 a partir dos relatórios de busca (pasta `docs/literatura/`), sem alteração das contagens.

**Atenção às contagens do OpenAlex.** As consultas desta tabela usaram, conforme o bloco, a busca geral do OpenAlex (`search`, que inclui o texto completo) ou o filtro de título e resumo. Por isso a mesma frase pode ter totais diferentes aqui: "undocumented endpoint" dá 32 na busca geral e 8 no filtro de título e resumo, e "zombie API" dá 15 e 1. A Tabela 1 deste trabalho usa apenas o filtro de título e resumo, refeito às 01h46 de 18/11/2026 para que todas as linhas tenham o mesmo critério.

## Procedimento

- **Data:** 18/11/2026.
- **Bases e acesso:** OpenAlex (`api.openalex.org`), arXiv (`export.arxiv.org/api`), Semantic Scholar (`api.semanticscholar.org`) e Crossref (`api.crossref.org`), por interface programática. O procedimento pode ser repetido pelas mesmas interfaces. As bases, porém, são atualizadas continuamente: os totais registrados correspondem à data da consulta e podem diferir em uma repetição.
- **Limitações declaradas:**
  - o **dblp** bloqueou as consultas automáticas (verificação antirrobô) e não forneceu nenhuma contagem;
  - o **Semantic Scholar** e o **OpenAlex** limitaram a taxa de requisições em parte das consultas, marcadas com "—";
  - o **Crossref** combina os termos por disjunção e ordena por relevância, então seus totais não medem cobertura. Foi usado para triar os primeiros resultados e para localizar e conferir itens conhecidos;
  - **IEEE Xplore, ACM Digital Library e Google Scholar não foram consultados** como bases de busca.
- **Triagem:** pelo título e, quando pertinente, pelo resumo. Uma referência só foi aceita depois de conferida em registro bibliográfico (DOI no Crossref, OpenAlex ou arXiv). Afirmações sobre o conteúdo se limitam ao que foi lido (resumo ou texto completo, conforme indicado na Seção 3).
- **Complemento:** candidatos levantados na fase de projeto, buscas dirigidas por título e busca web genérica, usada apenas para localizar PDFs de itens já identificados.

## Consultas

| Bloco | Base | Termos (total reportado) |
|---|---|---|
| Teste e descoberta em APIs REST | Semantic Scholar | REST API fuzzing (—); REST API testing (—); RESTful API black-box testing (—); undocumented endpoint (—); hidden API endpoint discovery (159); undocumented REST API endpoints (302); shadow API endpoint (2 136) |
| Teste e descoberta em APIs REST | OpenAlex | "undocumented endpoint" (32); "zombie API" (15); "RESTful API black-box testing" (5); "hidden API endpoint discovery" (0); "REST API fuzzing", "REST API testing", "shadow API", "forced browsing", "kiterunner", "soft 404" (—) |
| Teste e descoberta em APIs REST | Crossref | REST API fuzzing (65 895); shadow API endpoints (84 088); undocumented API endpoints detection (1 612 243); zombie API deprecated endpoints (36 365) |
| Teste e descoberta em APIs REST | arXiv | all:"REST API fuzzing" (12); all:"REST API" AND all:undocumented (4); all:"shadow API" (3); all:"zombie API" (0); all:"undocumented endpoints" (0); all:"hidden endpoints" (1); all:"directory brute forcing" (1); all:"forced browsing" (0); all:gobuster (0); all:ffuf (0); all:kiterunner (1); all:"soft 404" (1) |
| Teste e descoberta em APIs REST | Buscas dirigidas | DOIs dos 3 candidatos indicados pelo autor + Kim et al. (2022) (—) |
| Inferência de especificação e conformidade | Semantic Scholar | OpenAPI specification inference (10 665); REST API specification inference (—); inferring REST API from traffic (—) |
| Inferência de especificação e conformidade | OpenAlex | OpenAPI specification inference (827); REST API specification mining (21 018); shadow API endpoints undocumented (176); OpenAPI specification static analysis generation (1 050) |
| Inferência de especificação e conformidade | Crossref | OpenAPI specification inference (213 967); inferring REST API specification from traffic (9 435 187); REST API documentation inconsistency (163 540); OpenAPI conformance implementation (579 798) |
| Inferência de especificação e conformidade | arXiv | all:"specification" AND all:"REST" AND all:"inference" (222); abs:OpenAPI AND abs:undocumented (4); abs:"shadow API" OR abs:"shadow endpoints" OR abs:"API9" (3); abs:OpenAPI AND abs:inconsistencies (2); abs:"REST API" AND abs:specification AND abs:"static analysis" (4); all:Respector (2) |
| Inferência de especificação e conformidade | Buscas dirigidas | Generating REST API Specifications through Static Analysis (8 527 634); Example-driven Web API specification discovery (1 678 924); SpyREST automated RESTful API documentation HTTP proxy (688 999); Towards extracting web API specifications from documentation (10 284 216); inconsistencies REST API documentation implementation detection (2 301 191); RESTAssured formally verifying RESTful API specification conformance (138 917) |
| Soft 404 e inventário de APIs | dblp | soft 404; shadow API; zombie API; API inventory; undocumented API; shadow endpoint; Sic transit gloria telae (—) |
| Soft 404 e inventário de APIs | Semantic Scholar | soft 404; soft 404 detection; shadow API; zombie API; API inventory; undocumented API; shadow endpoint; undocumented REST API endpoints discovery (—) |
| Soft 404 e inventário de APIs | Crossref | soft 404 (547 819); shadow API (77 260); shadow endpoint (60 274); Sic transit gloria telae (245 833); soft 404 detection; zombie API; API inventory management; undocumented API endpoints (falha de resposta/irrelevante) |
| Soft 404 e inventário de APIs | arXiv | all:"soft 404" (1); all:"shadow API" (3); all:"shadow APIs" (3); all:"zombie API" / all:"zombie APIs" (0 / 0); all:"API inventory" (0); all:"undocumented API" (3); all:"undocumented endpoints" / all:"shadow endpoints" / all:"hidden endpoints" (0 / 0 / 1) |
| Soft 404 e inventário de APIs | OpenAlex | "soft 404" (10); "soft-404" (10); "shadow API" (11); "shadow APIs" (11); "zombie API" (1); "shadow endpoint" (1); "zombie APIs" (1); "API inventory" (6); "undocumented API" (—) |
| Soft 404 e inventário de APIs | Buscas dirigidas | consultas por título e autor de itens já identificados (Bar-Yossef et al., 2004; Meneses, Furuta e Shipman, 2012; Chandramouli e Butcher, 2025, a NIST SP 800-228) e por "shadow APIs" e "zombie APIs" (não se aplica: sem contagem) |

Totais entre parênteses; "—" indica consulta sem resposta por limite de requisições ou bloqueio. Os totais do Crossref ordenam por relevância e combinam os termos por disjunção, e por isso não medem cobertura. As buscas dirigidas localizaram itens já identificados (candidatos da fase de projeto e textos completos). O registro de cada consulta, com o número de itens triados e selecionados, está em `docs/literatura/`, junto com o código e os dados (Seção 6.5).
