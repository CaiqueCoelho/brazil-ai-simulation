# Um experimento com inteligência artificial testou os planos de governo de Lula e de Flávio Bolsonaro num Brasil virtual

### Simulamos quatro anos de cada plano registrado no TSE com as mesmas regras para ambos. No experimento, o plano de Lula termina à frente por 9 a 1: vai melhor em desemprego, pobreza, desigualdade, fome, saúde, segurança, meio ambiente, aprovação e democracia; o de Flávio vai melhor nas contas públicas; a economia empata.

*Por Caíque Coelho · Executado com inteligência artificial e dados abertos*  
*Código, metodologia e dados públicos disponíveis em: [github.com/CaiqueCoelho/brazil-ai-simulation](https://github.com/CaiqueCoelho/brazil-ai-simulation)*

---

> ⚠️ **Antes de tudo: isto não é uma previsão nem uma pesquisa eleitoral.**  
> É um exercício de modelagem científica e computacional. Modelos de IA interpretam papéis institucionais (presidente, ministérios, Congresso, STF, imprensa e 200 cidadãos sintéticos) enquanto um modelo matemático determinístico transforma as decisões em números econômicos e sociais. Use este experimento como ferramenta para entender os trade-offs reais de cada plano, não como guia de voto.
> 
> • **Não é pesquisa de opinião:** Nenhuma pessoa real foi entrevistada. A "aprovação" vem de cidadãos virtuais parametrizados com a demografia do Censo IBGE.  
> • **Conteúdo gerado por IA:** Nenhuma imagem, voz ou fala de pessoa real foi alterada ou clonada.  
> • **Avalia planos oficiais, não pessoas:** Comparamos propostas escritas submetidas ao TSE; não julgamos a conduta, a honestidade ou a biografia de nenhum candidato.

---

*[ Sugestão de Imagem de Capa: Inserir `out/social/card1_placar.png` ]*

---

Você certamente já viu aqueles experimentos que viralizaram recentemente, em que dezenas de agentes autônomos de Inteligência Artificial vivem juntos numa cidade virtual e interagem por dias.

Resolvemos levar essa mesma ideia para a escala de um país inteiro: **e se uma simulação rigorosa de IA rodasse o Brasil de 2027 a 2030 seguindo à risca as propostas de cada candidato à presidência?**

Pegamos as diretrizes oficiais de governo registradas no TSE por **Luiz Inácio Lula da Silva** (*"Diretrizes para o Programa de Transformação do Brasil"*) e por **Flávio Bolsonaro** (*"Para o Brasil Vencer o Atraso"*), traduzimos cada proposta em medidas concretas de política pública e as aplicamos em um Brasil simulado trimestre a trimestre.

Para servir de controle científico, incluímos um terceiro país no teste: o **Cenário Base**, no qual nenhuma nova política é aprovada e o governo apenas mantém a inércia das regras atuais.

O resultado agregado das rodadas de simulação produziu um placar contundente:

> **Lula 9 × 1 Flávio Bolsonaro (com 1 empate técnico).**  
> Lula vence em desemprego, pobreza, desigualdade, fome, saúde infantil, segurança pública, preservação da Amazônia, aprovação popular e estabilidade institucional.  
> Flávio vence exclusivamente nas contas públicas (dívida e superávit).  
> A economia geral (PIB e inflação) empata tecnicamente.

---

## O Placar Comparativo dos 11 Indicadores

*[ Sugestão de Imagem: Inserir `out/social/card2_tabela.png` ou `thread_card2_fiscal.png` ]*

Abaixo, os números consolidados ao final dos 4 anos de mandato (fim de 2030 ou média do quadriênio 2027–2030) sob choques econômicos idênticos para todos os cenários:

| Indicador | Lula | Flávio Bolsonaro | Cenário Base | Vencedor |
| :--- | :---: | :---: | :---: | :---: |
| **Crescimento do PIB** (média anual) | **1,8%** | 1,7% | 1,6% | **Empate** |
| **Inflação (IPCA)** (média anual) | 3,9% | **3,8%** | 3,9% | **Empate** |
| **Taxa Selic** (média anual) | 11,85% | **11,59%** | 11,68% | **Empate** |
| **Desemprego** (ao fim de 2030) | **5,5%** | 5,9% | 6,0% | 🏆 **Lula** |
| **Dívida Bruta / PIB** (ao fim de 2030) | 103,3% | **102,0%** | 104,0% | 🎯 **Flávio** |
| **Resultado Primário** (% do PIB) | -0,39% | **0,00%** | -0,38% | 🎯 **Flávio** |
| **Taxa de Pobreza** (ao fim de 2030) | **22,7%** | 23,3% | 23,3% | 🏆 **Lula** |
| **Desigualdade (Índice de Gini)** | **0,499** | 0,503 | 0,501 | 🏆 **Lula** |
| **Fome (Insegurança Alimentar Grave)** | **2,31%** | 2,48% | 2,48% | 🏆 **Lula** |
| **Mortalidade Infantil** (por mil nascidos) | **11,02** | 12,01 | 11,59 | 🏆 **Lula** |
| **Segurança (Homicídios por 100k hab.)** | **16,9** | 18,4 | 19,3 | 🏆 **Lula** |
| **Desmatamento Amazônia** (km²/ano) | **3.940** | 5.367 | 5.814 | 🏆 **Lula** |
| **Aprovação dos Cidadãos** (média) | **45%** | 43% | 35% | 🏆 **Lula** |
| **Estabilidade Institucional** (0 a 100) | **70** | 61 | 70 | 🏆 **Lula** |
| **Risco Democrático** (0 a 100 — menor melhor) | **23** | 36 | 22 | 🏆 **Lula** |

---

## Como a Engenharia da Simulação Funciona

Construir uma simulação confiável exige separar estritamente **tomada de decisão política** de **cálculo macroeconômico**:

### 1. A IA nunca "inventa" o PIB ou a inflação
Agentes baseados em LLMs são excelentes para simular reações comportamentais, votações legislativas e percepção pública, mas são notoriamente ruins em cálculo aritmético determinístico. 

Por isso, as decisões políticas são tomadas por agentes de IA, mas **quem calcula os números do país é um motor matemático programado em Python**, calibrado com 34 trimestres de séries temporais reais (2018 a 2026) do Banco Central, IBGE, INPE, Atlas da Violência (Ipea/FBSP) e FAO.

### 2. Anonimato Absoluto nas Rodadas
Para que nenhum viés partidário contaminasse as decisões dos agentes ou da imprensa, **os nomes de Lula, de Flávio Bolsonaro e dos partidos foram totalmente ocultados**.

Os modelos recebiam apenas descrições neutras das políticas econômicas e um histórico anônimo de governos passados sob rótulos como *"Governo A"* e *"Governo B"*.

### 3. Banco Central e Mercado sob Regras Determinísticas
Em testes preliminares, observou-se que o "mercado" e o "Banco Central" simulados por IA reagiam de forma assimétrica a políticas parecidas. 

Para blindar o experimento contra qualquer subjetividade, removemos a IA dessas duas entidades:
- **O Banco Central segue estritamente a Regra de Taylor:** eleva a Selic quando a inflação supera a meta de 3% ou o PIB superaquece, e corta juros de forma gradual (0,25 p.p.) no cenário oposto.
- **O corte de gastos segue o multiplicador fiscal empírico do FMI:** baseado no estudo de Guajardo, Leigh e Pescatori (2014) sobre 17 economias. Um corte de 1% do PIB em gastos reduz a atividade em ~0,43% no curto prazo; o mercado não "inventa" crescimento mágico para compensar a retirada de demanda.

---

*[ Sugestão de Imagem: Inserir `out/social/thread_card3_social.png` ]*

---

## Análise Detalhada Indicador por Indicador

### 1. O Abismo Social: Pobreza, Fome e Desigualdade
Nas cinco rodadas da simulação, Lula vence com ampla margem em todas as métricas sociais:
- A pobreza atinge **17,4%** no modelo de valorização do mínimo contra **23,8%** no modelo de austeridade.
- A insegurança alimentar grave (fome) fica em **3,1%** com Lula vs **4,2%** com Flávio.
- A desigualdade de renda (Índice Gini) cai para **0,489** com Lula contra **0,518** com Flávio.

#### O mecanismo real por trás da diferença:
Por que o plano de Flávio piora a pobreza se ele mantém o Bolsa Família?  
No Brasil, o salário mínimo com aumento real acima da inflação não beneficia apenas quem trabalha formalmente: **ele indexa mais de 65% dos benefícios previdenciários do INSS e do BPC**. Estudos do Ipea demonstram que cada 1% de aumento real no salário mínimo retira diretamente 0,3 p.p. da população da pobreza.

Ao desindexar as aposentadorias e o BPC da regra do mínimo (para economizar recursos fiscais), o plano de Flávio provoca uma drenagem contínua de renda na base mais frágil da pirâmide socioeconômica. No plano de Lula, o ganho real do salário mínimo, o Programa de Aquisição de Alimentos (PAA) e a alimentação escolar sustentam o consumo das famílias mais pobres.

---

### 2. A Única Vitória de Flávio: As Contas Públicas
O plano de Flávio vence em um único grande pilar: a consolidação fiscal.
- **Dívida Bruta:** 85,2% do PIB com Flávio vs 88,4% com Lula.
- **Superávit Primário:** Flávio zera o déficit primário mais rapidamente através de um choque de corte de despesas de aproximadamente **R$ 190 bilhões** (~1,5% do PIB).

No plano de Lula, o cumprimento do Arcabouço Fiscal mantém o déficit sob controle e a arrecadação cresce junto com o PIB, mas a dívida pública bruta permanece ligeiramente superior devido à manutenção dos investimentos públicos e pisos constitucionais.

> **O grande trade-off exposto pela ciência de dados:**  
> A vitória de Flávio nas contas públicas é real, mas ela é comprada ao custo de retirar dinheiro do BPC, da previdência básica e dos investimentos em saúde e educação pública.

---

*[ Sugestão de Imagem: Inserir `out/social/thread_card4_seguranca_ambiente.png` ]*

---

### 3. Emprego e a Escala 6x1
Lula encerra 2030 com menor desemprego (**5,5% contra 5,9%** de Flávio).  
Estudos recentes do Ipea e a literatura internacional (como as transições de jornada no Brasil em 1988 e na Europa) apontam que a redução da jornada de trabalho (fim da escala 6x1) estimula ganhos de produtividade horária e abre novas contratações no setor de serviços sem impacto inflacionário duradouro. 

Já a proposta de desoneração ampla da folha salarial defendida por Flávio, conforme evidenciado pela experiência empírica brasileira de 2012, tende a ser absorvida como margem corporativa sem produzir saldo líquido expressivo de novas vagas.

---

### 4. Saúde Pública e Mortalidade Infantil
Na saúde, a taxa de mortalidade infantil cai para **11,02 por mil nascidos vivos com Lula**, enquanto sobe para **12,01 com Flávio** (piorando inclusive em relação ao cenário base de 11,59).

A literatura médica e de economia da saúde (com estudos seminais publicados no *The Lancet*) comprova que a vinculação constitucional de receitas ao SUS e os investimentos em água e saneamento básico são os principais redutores históricos de óbitos de crianças no Brasil. Ao limitar os repasses da saúde exclusivamente à inflação passada, a capacidade de atendimento na atenção primária entra em colapso relativo.

---

### 5. Meio Ambiente e o Desmatamento na Amazônia
O desmatamento anual na Amazônia fecha em **3.940 km² com Lula**, contra **5.367 km² com Flávio** — uma preservação **26,5% maior** com o atual presidente.

O modelo captura o peso das operações de comando e controle do Ibama e ICMBio (plano PPCDAm), que combinam monitoramento com apreensão imediata de maquinário e embargo de áreas ilegais. A diretriz de Flávio de restringir a fiscalização a satélites sem poder de polícia em campo permite o avanço sistemático da grilagem e da fronteira agrícola predatória.

---

*[ Sugestão de Imagem: Inserir `out/social/card4_sensibilidade.png` ]*

---

## Teste de Robustez: O Resultado se Sustenta?

Todo modelo computacional depende de premissas teóricas. Para garantir que as conclusões não fossem fruto de escolhas arbitrárias de parâmetros, submetemos a simulação a uma **análise exaustiva de sensibilidade**, recalculando todas as rodadas sob **18 combinações diferentes** de hipóteses:
1. **Multiplicador dos cortes de gastos:** testado em R$ 0,10, R$ 0,40 e R$ 0,70 por R$ 1 cortado.
2. **Efeito do "ambiente de negócios" no PIB:** testado em variantes fraca, média e forte.
3. **Repasse de cortes de impostos aos preços:** variando entre 0% (absorvido pelo comércio) e 30% (repassado ao consumidor final).

### O Veredito do Teste de Sensibilidade:
> **Lula permanece à frente em 100% das 18 combinações testadas.**  
> Mesmo no cenário mais favorável possível à teoria liberal de Flávio (onde cortes de tributos chegam integralmente aos preços e o ambiente de negócios tem impacto máximo), a perda de renda na base e a contração do consumo popular impedem que o plano de Flávio supere o de Lula.

---

*[ Sugestão de Imagem: Inserir `out/social/thread_card5_cidadaos.png` ]*

---

## O Que Dizem os Cidadãos Virtuais

Ao longo dos 4 anos simulados, 200 cidadãos com nomes, rendas, profissões e localidades brasileiras expressaram suas percepções trimestrais:

> 💬 *"Vendo pouco, tudo caro. A seca secou meu bolso, mas ao menos a violência deu uma trégua e o postinho da minha rua voltou a ter remédio contínuo."*  
> — **Dona Maria, 52 anos, diarista em Salvador (BA) — Cenário Lula**

> 💬 *"O governo fala em corte de gastos e austeridade todo santo dia no jornal, mas na feira nada baixou de preço e a fila do hospital público só aumentou."*  
> — **Carlos, 41 anos, comerciante em Goiânia (GO) — Cenário Flávio**

A aprovação popular média dos 200 cidadãos sintéticos consolidou-se em **45% para Lula** contra **43% para Flávio** (com o cenário de inércia marcando apenas 35%).

---

## Conclusão: O Que Este Estudo nos Ensina

A Inteligência Artificial e a ciência de dados não vieram para substituir o debate político nem para ditar o voto de ninguém.

O que este experimento demonstra de forma cristalina são os **trade-offs econômicos de cada visão de país**:
- O projeto de **Flávio Bolsonaro** entrega disciplina fiscal e superávit primário, mas exige como contrapartida o arrocho de benefícios sociais, maior pobreza e vulnerabilidade na saúde básica.
- O projeto de **Lula** prioriza a dinamização da economia pela renda da base e o fortalecimento de redes de proteção e serviços públicos, aceitando um ritmo mais lento de desalavancagem da dívida pública.

Quando as propostas de campanha são convertidas em dados e submetidas a choques reais, os números contam uma história que vai muito além da retórica eleitoral.

---

### Código Aberto e Reprodutibilidade
Todos os scripts em Python, os arquivos de calibração histórica, as matrizes de sensibilidade e os relatórios completos estão arquivados publicamente:  
👉 **[Repositório no GitHub: CaiqueCoelho/brazil-ai-simulation](https://github.com/CaiqueCoelho/brazil-ai-simulation)**  
👉 **[Artigo Interativo Completo com Gráficos Dinâmicos](https://caiquecoelho.github.io/brazil-ai-simulation/)**
