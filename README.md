# shadowscan — detecção de shadow endpoints em APIs REST

Código, dados e documentação do Trabalho de Conclusão de Curso "Detecção de endpoints não
documentados em APIs REST por análise diferencial: avaliação por degradação de especificação"
(Engenharia de Software, Instituto de Ensino Superior iCEV, 2026).

A ferramenta compara a especificação OpenAPI declarada (conjunto D) com a superfície observada
por descoberta ativa (conjunto O). Reporta O \ D (shadow endpoints) e D \ O (operações declaradas
não observadas; rótulo interno `zombie`). A avaliação usa degradação de especificação: N operações
sorteadas com semente fixa são removidas da spec e formam o conjunto de referência.

> **Uso exclusivo contra instâncias locais de aplicações deliberadamente vulneráveis.** Não aponte
> a ferramenta para sistemas de terceiros sem autorização formal.

## Conteúdo

```
shadowscan/        ferramenta
  spec_parser.py   [1] OpenAPI -> conjunto D (método, caminho-template)
  responses.py         comparação de respostas (soft 404)
  discovery.py     [2] descoberta ativa -> conjunto O (baselines, fases A/B/C)
  diff.py          [3] O\D = shadow, D\O = declarada não observada (casamento por template)
  classify.py      [4] classificação heurística (não avaliada experimentalmente)
  metrics.py           precisão, revocação, F1
  ground_truth.py      degradação de spec + registro do que foi removido
  __main__.py          CLI
experiments/
  run_experiments.py           bateria (N × sementes × autenticação)
  analyze.py                   tabelas do artigo a partir de runs/ (não toca nos alvos)
  laravel_routes_to_openapi.py spec do vAPI a partir de routes/api.php
tests/             testes unitários
specs/             specs originais e shadows intrínsecos verificados
wordlists/         SecLists (api/objects.txt, api/actions.txt)
runs/              saídas de todas as execuções, inclusive as substituídas e invalidadas
envs/vapi_config/  configuração local do vAPI usada nos experimentos (docker-compose.override.yml)
docs/
  decisoes.md                 D1–D21: decisões que afetam o resultado (Apêndice A)
  protocolo_experimental.md   procedimento, métricas e ameaças à validade (Apêndice B)
  ambiente_experimental.md    hardware, versões, digests e hashes SHA-256 (Apêndice D)
  protocolo_busca.md          busca bibliográfica (Apêndice E)
  diario_de_pesquisa.md       registro cronológico (entradas E##) citado nos apêndices
  literatura/                 relatórios da busca e auditoria de citações
  trabalhos_futuros.md
```

Cada execução em `runs/<bateria>/<n>_<semente>_<auth>/` contém `spec_degradada.yml`,
`ground_truth.json` (G e o tipo de cada remoção) e `resultado.json` (configuração, contadores,
todas as observações de O, shadows, operações declaradas não observadas, casos ambíguos e métricas).
As tabelas do artigo vêm de `runs/exp_*_principal/metricas_recalculadas.csv`.

## Reprodução

Requisitos: Python 3.14, Docker. Versões exatas, digests e hashes em `docs/ambiente_experimental.md`.

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
python -m unittest discover tests

# Alvo 1: VAmPI (imagem fixada por digest)
docker run -d --name vampi -p 5000:5000 erev0s/vampi@sha256:0a5a224b6e14ae7da6a6ea265178ff71286ff903aec74adee98f660bb0e4ca12

# Alvo 2: vAPI, no commit usado nos experimentos, com a configuração local deste repositório
git clone https://github.com/roottusk/vapi envs\vapi
git -C envs\vapi checkout 67152695b0acf13dd424905729080fbc80d5a593
Copy-Item envs\vapi_config\docker-compose.override.yml envs\vapi\
cd envs\vapi; docker compose up -d --build; cd ..\..

# N = 0 (levantamento de intrínsecos) e bateria principal
python -m experiments.run_experiments --alvo vampi --n 0 --seeds 1 --out runs\exp_vampi_n0
python -m experiments.run_experiments --alvo vampi --n 3 6 --seeds 1 2 3 4 5 --out runs\exp_vampi_principal
python -m experiments.run_experiments --alvo vapi  --n 0 --seeds 1 --out runs\exp_vapi_n0
python -m experiments.run_experiments --alvo vapi  --n 3 6 --seeds 1 2 3 4 5 --out runs\exp_vapi_principal

# Tabelas (só lê runs/)
python -m experiments.analyze runs\exp_vampi_principal --intrinsecos specs\vampi_intrinsecos.json
python -m experiments.analyze runs\exp_vapi_principal  --intrinsecos specs\vapi_intrinsecos.json
```

Para recalcular as métricas a partir dos dados publicados, sem executar nada contra os alvos,
basta o último bloco. O mesmo G de qualquer execução pode ser regenerado com
`python -m shadowscan.ground_truth <spec> -n N --seed S -o <dir>`.

## Uso avulso

```powershell
python -m shadowscan --url http://127.0.0.1:5000 --spec specs\vampi_openapi3.yml -o runs\x.json
```

## Licenças de terceiros

As wordlists em `wordlists/` são do projeto SecLists (licença MIT), commit
`6b19c2f5088c45b5dadb4d8918d2ab4f7efb03a9`. VAmPI e vAPI não são redistribuídos aqui.
