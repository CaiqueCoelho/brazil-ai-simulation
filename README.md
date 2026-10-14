# brazil-sim: Brasil 2027–2030 simulado por IA

Experimento que simula quatro anos de governo no Brasil (2027–2030) sob duas plataformas registradas no TSE em 2026, a de **Lula** e a de **Flávio Bolsonaro**, e compara os resultados com um **cenário base** sem novas políticas.

> **Não é previsão.** É um experimento estilizado: modelos de linguagem tomam decisões e um modelo de equações simples transforma essas decisões em números. Os resultados refletem as hipóteses do modelo e os vieses dos modelos de IA.

Todo o experimento, incluindo o código, a calibração, a execução, a análise e o artigo, foi conduzido por IA (Claude, da Anthropic, no Claude Code). O papel humano foi aprovar o orçamento, validar a lista de propostas, decidir algumas premissas registradas nos arquivos de regras e publicar.

## Resultado final (motor v8)

Agentes sem saber quem governa, com propostas em linguagem neutra e um histórico anônimo de cada grupo (números oficiais por ano, sem anos nem eventos citados). Mercado e Banco Central seguem regras fixas iguais para os dois (regra de Taylor; confiança do mercado pelas contas públicas, dívida, inflação, crescimento e estabilidade), cortes de gasto seguem o efeito líquido medido por Guajardo, Leigh e Pescatori (2014), e mudanças de imposto sobre consumo e de custo do trabalho mexem nos preços uma vez só, sem se arrastar pela inflação dos trimestres seguintes. Custos e efeitos de cada proposta conferidos em fontes públicas e estudos, com a mesma régua para os dois (`data/engine_v7_rules.json`, `data/engine_v8_rules.json`). Vence um indicador quem é melhor na média e na maioria das simulações, comparadas uma a uma; diferenças dentro da tolerância oficial (resultado primário ±0,25 ponto do PIB, inflação ±1,5) são empate (`data/scoring_v3_rules.json`, regra adotada depois de ver o resultado; com a anterior, que exigia todas as simulações, o placar seria 8 × 1). Indicadores que medem a mesma coisa contam uma vez (11 itens).

| Versão | Lula × Flávio | Sensibilidade (18) |
|---|---|---|
| Versão principal (100 cidadãos, 5 simulações, mercado e BC por regras fixas) | **9 × 1** | Lula 18 |
| Rodada anterior (200 cidadãos), refeita com as premissas atuais e mercado e BC por regras fixas | **8 × 2** | — |
| Histórico real (Bolsonaro 2019/2022 × Lula 2023–2025, sem rebote da pandemia) | **3 × 2** | — |

Lula vence desemprego, pobreza, desigualdade, fome, mortalidade infantil, homicídios, Amazônia e democracia nas 5 simulações; Flávio vence contas públicas nas 5. Lula vence também aprovação (45% contra 43% na média, à frente em 4 de 5 simulações). Economia empata (Lula cresce mais, Flávio tem Selic um pouco menor).

O corte de gastos de Flávio usa o tamanho apresentado pela equipe econômica dele (cerca de 1,5% do PIB, R$ 190 bilhões), com aposentadorias, BPC e pisos de saúde e educação corrigidos só pela inflação, itens citados pela própria equipe.

Resultados em `out/blind-v10/`: simulações 1 a 3 de `config/blind-v10.yaml` e 4 e 5 de `config/blind-v10b.yaml`. O cenário base vem de `out/blind-v7` (mesmas sementes), refeito com as regras fixas. Depois da correção do efeito único nos preços, a rodada foi refeita sem custo com as decisões gravadas dos agentes; o placar não mudou. Rodadas exploratórias anteriores foram removidas do repositório.

## Como funciona

```text
Propostas do TSE ──► lista estruturada (data/policies_*.json)
                        │
Trimestre a trimestre (16 trimestres = 4 anos):
  1. Choques externos sorteados (iguais para os três cenários)
  2. Agentes institucionais (DeepSeek): Presidente, Ministro da Fazenda, Centrão,
     3 blocos do Congresso (votação ponderada por cadeiras), STF e imprensa;
     Banco Central e mercado seguem regras fixas (sim/rule_agents.py)
  3. Cidadãos virtuais (amostra pelo perfil IBGE/PNAD) reagem e avaliam o governo
  4. Motor de equações (sim/engine.py) calcula os indicadores
```

- **Os agentes decidem, as equações calculam.** A IA nunca inventa o PIB: ela escolhe ações (votos, juros, prioridades) e o motor determinístico calcula o resultado.
- **Cego para nomes.** Os agentes veem apenas "o Presidente", a plataforma em linguagem neutra e um histórico anônimo do grupo, nunca o nome do candidato.
- **Mesmo mundo para todos.** Os mesmos choques, cidadãos e ruído aleatório (por semente) valem para os três cenários.
- **Cinco repetições (sementes).** Cada cenário roda 5 vezes; o relatório mostra a média e a faixa entre a menor e a maior.
- **Calibração com dados oficiais.** `sim/calibrate.py` ajusta o motor a 34 trimestres (2018–2026) de séries do Banco Central/IBGE (`data/bcb/`, geradas por `sim/history.py`).

## Indicadores

PIB, inflação, Selic, desemprego, dívida pública, resultado primário, pobreza, Gini, fome, mortalidade infantil (saúde), homicídios, desmatamento, aprovação, estabilidade institucional e risco democrático. O câmbio é calculado, mas não entra no placar. As definições estão em `sim/metrics_pt.py`.

## Estrutura

| Caminho | O que é |
|---|---|
| `sim/engine.py` | Motor de equações e regras institucionais (votação, STF, tentativas) |
| `sim/agents.py` | Prompts e esquemas JSON dos agentes |
| `sim/run.py` | Orquestração, sementes, guarda de orçamento |
| `sim/llm.py` | Cliente DeepSeek, cache SQLite, limite de gasto |
| `sim/history.py`, `sim/calibrate.py` | Download de dados oficiais e calibração |
| `sim/analysis.py` | Vencedor por indicador e por item (com regra de empate) |
| `sim/track_record.py` | Histórico real: governo Bolsonaro (2019, 2022) x governo Lula (2023-2025) com dados oficiais e regras pré-registradas em `data/track_record_rules.json` |
| `sim/rule_agents.py` | Regras fixas de mercado e Banco Central (`data/engine_v8_rules.json`) |
| `sim/sensitivity.py` | Teste de sensibilidade: reexecuta as decisões gravadas com hipóteses alternativas (US$ 0) |
| `sim/report.py` | Relatório HTML interativo com replay (1 ano = 1 minuto) |
| `sim/article.py`, `article/` | Artigo em PDF |
| `data/` | Propostas, ponto de partida, choques, séries oficiais, parâmetros calibrados |
| `out/blind-v10/` | Resultados, análises e relatório publicados |

## Rodando

```bash
uv sync
cp .env.example .env              # coloque sua DEEPSEEK_API_KEY
uv run pytest -q
uv run python -m sim.run --config config/blind-v10.yaml --dry-run   # projeção de custo, US$ 0
uv run python -m sim.run --config config/blind-v10.yaml             # execução real
uv run python -m sim.analysis out/blind-v10/results.json
uv run python -m sim.sensitivity out/blind-v10/results.json
uv run python -m sim.report out/blind-v10/results.json
uv run python -m sim.article out/blind-v10 --repo https://github.com/CaiqueCoelho/brazil-ai-simulation   # depois imprima article/artigo.html em PDF
```

O custo é protegido em camadas: verificação prévia (recusa se o custo esperado passar do limite), reserva do pior caso antes de cada chamada (para em `budget_usd`), cache de respostas e saldo pré-pago da conta.

## Limitações

- O motor é simples: 34 trimestres de calibração não capturam toda a economia brasileira (erro médio trimestral: inflação ~1,7 p.p., dívida ~2,4 p.p.).
- O tamanho do efeito de cada proposta (`levers` em `data/policies_*.json`) vem de fontes públicas e estudos, com a mesma régua para os dois; algumas são inferências documentadas nos arquivos de regras. Os pesos da regra do mercado são escolha do modelo, testados pela metade e em dobro.
- Modelos de linguagem têm vieses próprios; o anonimato dos candidatos reduz, mas não elimina, esse efeito.
- O Congresso usa as cadeiras da Câmara eleita em 4 de outubro de 2026 (esquerda 24%, Centrão 50%, direita 26%).

## English summary

LLM agents (DeepSeek) play Brazil's institutions and 100 citizens; the market and central bank follow fixed rules; a deterministic engine calibrated on 2018–2026 central-bank data turns their decisions into metrics. Three scenarios (Lula's and Flávio Bolsonaro's 2026 platforms, plus a no-new-policy baseline) × 5 seeds. Final score: Lula 9 × 1. Built and run end-to-end by an AI (Claude Code). Not a forecast.
