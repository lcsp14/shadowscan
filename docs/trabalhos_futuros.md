# Trabalhos futuros

Ideias fora do escopo congelado (CLAUDE.md, seção 2). Viram a seção de Trabalhos Futuros do artigo.

- Categorias de lógica de negócio do OWASP API Top 10 2023 (BOLA, BOPLA, mass assignment, SSRF), que exigem entender a semântica da aplicação.
- Wordlists adaptativas: gerar candidatos a partir do vocabulário da própria spec e das respostas (ex.: `createdb`, `_debug`), em vez de só wordlist estática.
- Desambiguar colisões literal × template (`/users/v1/admin`): comparar a estrutura da resposta com a de uma instância válida do template.
- Autenticação por sub-API e com múltiplos papéis (usuário comum × admin), para alcançar rotas que só respondem a perfis privilegiados.
- Suporte a outros formatos de especificação (Swagger 2.0, coleções Postman, GraphQL).
- Avaliação em APIs de produção, com autorização formal, para medir a prevalência real de shadow endpoints.
- Avaliar a sensibilidade ao limiar de similaridade (0,90) e ao número de baselines.
- Aplicar a wordlist também sob prefixos com parâmetro (`/users/v1/{username}/<palavra>`), instanciando o parâmetro. Hoje rotas como `PUT /users/v1/{username}/password`, quando ausentes da spec, não podem ser descobertas (diário E13). Custo: multiplica as requisições pelo número de prefixos parametrizados.
- Avaliar a acurácia da classificação heurística (versão obsoleta / depuração / administrativo) com um ground truth de shadow endpoints **naturais** e rotulados. O ground truth por degradação não exercita as categorias (A11). Caso já observado: `dashboard/flag` (vAPI) seria rotulado como administrativo, mas é o envio de flag do desafio.
- Descoberta de subárvores inteiras ocultadas: quando todos os caminhos sob um prefixo saem da especificação (ex.: `/books/v1/*` em n6_s4), não há prefixo declarado de onde partir e a wordlist não gera `/books/v1` (exige `v1` como palavra sob `/books`). Possível extensão: combinar palavras e segmentos de versão em profundidade 2, ao custo de crescimento quadrático de requisições.
- Sondar com corpos de requisição derivados dos esquemas da própria especificação, em vez de `{}`. Em alvos que colapsam todos os erros numa resposta única (vAPI: `500 {}`), rotas que lançam exceção com entrada vazia ficam indistinguíveis de inexistentes (diário E34).
