# brazil-sim: Brasil 2027–2030 simulado por IA

Experimento que simula quatro anos de governo no Brasil (2027–2030) sob duas plataformas registradas no TSE em 2026, a de **Lula** e a de **Flávio Bolsonaro**, e compara os resultados com um **cenário base** sem novas políticas.

> **Não é previsão.** É um experimento estilizado: modelos de linguagem tomam decisões e um modelo de equações simples transforma essas decisões em números. Os resultados refletem as hipóteses do modelo e os vieses dos modelos de IA.

Todo o experimento, incluindo o código, a calibração, a execução, a análise e o artigo, foi conduzido por IA (Claude, da Anthropic, no Claude Code). O papel humano foi aprovar o orçamento, validar a lista de propostas e publicar.

## Resultado final (motor v5)

| Lente | Por indicador (Lula × Flávio) | Por área |
|---|---|---|
| Simulação principal (agentes sem saber quem governa) | 5 × 5 | 4 × 2 |
| Principal, mercado e Banco Central iguais para os dois | 9 × 2 | 6 × 1 |
| Simulação informada (agentes veem o histórico real) | 5 × 7 | 4 × 3 |
| Informada, mercado e Banco Central iguais | 7 × 2 | 5 × 2 |
| Histórico real (Bolsonaro 2019/2022 × Lula 2023–2025, sem rebote da pandemia) | 4 × 4 | 2 × 2 |

Em todas as simulações, Lula vence desigualdade, Amazônia, saúde e democracia (risco democrático e estabilidade institucional), e Flávio vence contas públicas. As vitórias econômicas de Flávio vêm da reação dos agentes "mercado" e "Banco Central". Teste de sensibilidade (18 combinações): Lula 12, empate 6, Flávio 0.

**Motor v4** (`data/engine_v4_rules.json`): retirado o termo de inflação do Gini, que não tinha base em dados e acumulava efeito sem limite; correção identificada depois dos resultados e declarada no artigo.

**Motor v5** (`data/engine_v5_rules.json`): canal das aposentadorias do piso/BPC (Ipea) e do salário mínimo (Firpo e Reis; Engbom e Moser) na desigualdade; reforma do IR documentada sem efeito no Gini (medido antes do imposto). Teste à parte: Flávio sem ganho real do mínimo (`sim/min_wage_test.py`).

**Motor v3** (`data/engine_v3_rules.json`): efeito das transferências sobre a desigualdade segundo o IBGE e memória de conflito com o STF na estabilidade institucional. Resultados em `out/scale-e5/` e `out/informed-e5/`.

**Motor v2** (`data/engine_v2_rules.json`, registrado antes do ajuste): canal de consumo das transferências de renda e queda estrutural do desemprego, estimados com dados de 2018–2026; o erro do desemprego caiu de 2,0 para 1,1 ponto. As decisões gravadas dos agentes foram reprocessadas (`sim/replay_v2.py`) em `out/scale-e5/` e `out/informed-e5/`; resultados do motor v1 preservados em `out/scale/` e `out/informed/`, e a primeira versão em `out/scale-v1/`.

**Auditoria:** custo de programas de Lula contado em dobro (corrigido); infraestrutura de Flávio tratada como pública (corrigido); propostas faltantes dos dois lados adicionadas; índice de risco democrático com memória do conflito com o STF; contador de custo subestimava tokens em cache (corrigido); placar por área adicionado ao lado do placar por indicador.

## Como funciona

```text
Propostas do TSE ──► lista estruturada (data/policies_*.json)
                        │
Trimestre a trimestre (16 trimestres = 4 anos):
  1. Choques externos sorteados (iguais para os três cenários)
  2. Agentes institucionais (DeepSeek): Presidente, Ministro da Fazenda, Centrão,
     3 blocos do Congresso (votação ponderada por cadeiras), STF, Banco Central,
     mercado e imprensa
  3. 200 cidadãos virtuais (amostra pelo perfil IBGE/PNAD) reagem e avaliam o governo
  4. Motor de equações (sim/engine.py) calcula os indicadores
```

- **Os agentes decidem, as equações calculam.** A IA nunca inventa o PIB: ela escolhe ações (votos, juros, prioridades) e o motor determinístico calcula o resultado.
- **Cego para nomes.** Os agentes veem apenas "o Presidente" e a plataforma, nunca o nome do candidato.
- **Mesmo mundo para todos.** Os mesmos choques, cidadãos e ruído aleatório (por semente) valem para os três cenários.
- **Cinco repetições (sementes).** Cada cenário roda 5 vezes; o relatório mostra a média e a faixa entre a menor e a maior.
- **Calibração com dados oficiais.** `sim/calibrate.py` ajusta o motor a 34 trimestres (2018–2026) de séries do Banco Central/IBGE (`data/bcb/`, geradas por `sim/history.py`).

## Indicadores

PIB, inflação, Selic, desemprego, dívida pública, resultado primário, câmbio, pobreza, Gini, mortalidade infantil (saúde), homicídios, desmatamento, aprovação, estabilidade institucional e risco democrático. As definições estão em `sim/metrics_pt.py`.

## Estrutura

| Caminho | O que é |
|---|---|
| `sim/engine.py` | Motor de equações e regras institucionais (votação, STF, tentativas) |
| `sim/agents.py` | Prompts e esquemas JSON dos agentes |
| `sim/run.py` | Orquestração, sementes, guarda de orçamento |
| `sim/llm.py` | Cliente DeepSeek, cache SQLite, limite de gasto |
| `sim/history.py`, `sim/calibrate.py` | Download de dados oficiais e calibração |
| `sim/analysis.py` | Vencedor por indicador (com regra de empate) |
| `sim/track_record.py` | Histórico real: governo Bolsonaro (2019, 2022) x governo Lula (2023-2025) com dados oficiais e regras pré-registradas em `data/track_record_rules.json` |
| `sim/sensitivity.py` | Teste de sensibilidade: reexecuta as decisões gravadas com hipóteses alternativas (US$ 0) |
| `sim/report.py` | Relatório HTML interativo com replay (1 ano = 1 minuto) |
| `sim/article.py`, `article/` | Artigo em PDF |
| `data/` | Propostas, ponto de partida, choques, séries oficiais, parâmetros calibrados |
| `out/scale/` | Resultados completos, análise e relatório da execução publicada |

## Rodando

```bash
uv sync
cp .env.example .env              # coloque sua DEEPSEEK_API_KEY
uv run pytest -q
uv run python -m sim.run --config config/scale.yaml --dry-run   # projeção de custo, US$ 0
uv run python -m sim.run --config config/scale.yaml             # execução real
uv run python -m sim.analysis out/scale/results.json
uv run python -m sim.sensitivity out/scale/results.json
uv run python -m sim.report out/scale/results.json
uv run python -m sim.article out/scale --repo https://github.com/<você>/brazil-sim   # depois imprima article/artigo.html em PDF
```

O custo é protegido em camadas: verificação prévia (recusa se o custo esperado passar do limite), reserva do pior caso antes de cada chamada (para em `budget_usd`), cache de respostas e saldo pré-pago da conta.

## Limitações

- O motor é simples: 34 trimestres de calibração não capturam toda a economia brasileira (erro médio trimestral: inflação ~1,7 p.p., dívida ~2,4 p.p.).
- O tamanho do efeito de cada proposta (`levers` em `data/policies_*.json`) é um julgamento feito pela IA com uma escala única para os dois candidatos (pequeno = 0,25, médio = 0,5, grande = 1,0).
- Modelos de linguagem têm vieses próprios; o anonimato dos candidatos reduz, mas não elimina, esse efeito.
- A composição do Congresso usa as bancadas aproximadas de 2023–2026; o resultado da eleição de 2026 não foi modelado.

## English summary

LLM agents (DeepSeek) play Brazil's institutions and 200 citizens; a deterministic engine calibrated on 2018–2026 central-bank data turns their decisions into metrics. Three scenarios (Lula's and Flávio Bolsonaro's 2026 platforms, plus a no-new-policy baseline) × 5 seeds. Built and run end-to-end by an AI (Claude Code). Not a forecast.
