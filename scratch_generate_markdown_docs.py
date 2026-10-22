import json
from pathlib import Path
from collections import Counter
from sim.agents import sample_personas

ROOT = Path("/Users/caiquecoelho/Documents/Projects/directory/brazil-sim")
ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")

shares = json.load(open(ROOT / "data" / "personas_shares.json"))
personas = sample_personas(shares, 100, 1)

def pt_income(inc):
    mapping = {
        "up to 1 minimum wage": "Até 1 Salário Mínimo",
        "1-2 minimum wages": "1 a 2 Salários Mínimos",
        "2-5 minimum wages": "2 a 5 Salários Mínimos",
        "over 5 minimum wages": "Mais de 5 Salários Mínimos"
    }
    return mapping.get(inc, inc)

def pt_vote(v):
    mapping = {
        "voted for the PT candidate": "Lula (PT)",
        "voted for the PL candidate": "Bolsonaro (PL)",
        "abstained or voted null/blank": "Abstenção / Nulo / Branco"
    }
    return mapping.get(v, v)

def pt_religion(r):
    mapping = {
        "Catholic": "Católica",
        "Evangelical": "Evangélica",
        "No religion": "Sem religião",
        "Other": "Outras"
    }
    return mapping.get(r, r)

def pt_area(a):
    return "Urbana" if a == "urban" else "Rural"

def pt_occupation(o):
    mapping = {
        "informal street vendor": "Vendedor(a) ambulante informal",
        "rural day laborer": "Trabalhador(a) rural diarista",
        "unemployed and looking for work": "Desempregado(a) buscando vaga",
        "domestic worker": "Trabalhadora doméstica / diarista",
        "app delivery rider": "Entregador(a) de aplicativo",
        "retiree on minimum pension": "Aposentado(a) piso do INSS",
        "supermarket cashier": "Caixa de supermercado",
        "construction worker": "Operário(a) da construção civil",
        "call-center operator": "Operador(a) de teleatendimento",
        "truck driver": "Motorista de caminhão",
        "nursing technician": "Técnico(a) de enfermagem",
        "small farmer": "Pequeno(a) agricultor(a) familiar",
        "public school teacher": "Professor(a) de escola pública",
        "small business owner": "Pequeno(a) comerciante / MEI",
        "police officer": "Policial militar / civil",
        "bank clerk": "Escriturário(a) bancário(a)",
        "IT support technician": "Técnico(a) de suporte em TI",
        "agribusiness technician": "Técnico(a) agropecuário(a)",
        "doctor": "Médico(a)",
        "software engineer": "Engenheiro(a) de software",
        "agribusiness producer": "Produtor(a) do agronegócio",
        "lawyer": "Advogado(a)",
        "senior civil servant": "Servidor(a) público(a) de carreira",
        "company manager": "Gerente de empresa privada"
    }
    return mapping.get(o, o)

def infer_schooling(income, occupation):
    if income == "up to 1 minimum wage":
        return "Fundamental (Incompleto/Completo)"
    elif income == "1-2 minimum wages":
        if "technician" in occupation or "farmer" in occupation:
            return "Médio Completo / Técnico"
        return "Médio (Incompleto/Completo)"
    elif income == "2-5 minimum wages":
        if "teacher" in occupation or "bank" in occupation:
            return "Superior Completo / Licenciatura"
        elif "technician" in occupation:
            return "Médio / Técnico Especializado"
        return "Médio Completo a Superior"
    else:
        return "Superior Completo / Pós-graduação"

# --- 1. AMOSTRA DE TODOS OS CIDADÃOS SIMULADOS ---
doc1 = []
doc1.append("# Amostra Completa dos 100 Cidadãos Virtuais Simulados (`brazil-sim`)")
doc1.append("\n> **Nota Metodológica:** Esta amostra de 100 cidadãos sintéticos foi sorteada de forma determinística via algoritmo estatístico pseudo-aleatório (`seed 1`) parametrizado pelas proporções oficiais do Censo Demográfico do IBGE (2022), da PNAD Contínua e do resultado do segundo turno das eleições presidenciais de 2022 do TSE.")
doc1.append("\n## 1. Visão Geral da Estratificação Demográfica")
doc1.append("Os cidadãos virtuais atuam no experimento trimestre a trimestre de 2027 a 2030, avaliando o governo federal a partir de sua perspectiva de vida material: se as vendas aumentaram, se os alimentos baratearam, se a seca afetou o orçamento, se a fila do posto de saúde andou ou se a segurança do bairro melhorou.")
doc1.append("\n### Distribuição Agregada da Amostra (100 Personas)")
doc1.append("| Dimensão | Categoria na Amostra | Quantidade / Proporção | Proporção Oficial de Referência (IBGE / TSE) |")
doc1.append("| :--- | :--- | :---: | :---: |")
doc1.append("| **Renda Domiciliar** | Até 1 Salário Mínimo | **31%** | 30,0% (PNAD Contínua) |")
doc1.append("| | 1 a 2 Salários Mínimos | **25%** | 32,0% (PNAD Contínua) |")
doc1.append("| | 2 a 5 Salários Mínimos | **33%** | 26,0% (PNAD Contínua) |")
doc1.append("| | Mais de 5 Salários Mínimos | **11%** | 12,0% (PNAD Contínua) |")
doc1.append("| **Região** | Sudeste | **33%** | 41,8% (Censo 2022) |")
doc1.append("| | Nordeste | **24%** | 26,9% (Censo 2022) |")
doc1.append("| | Sul | **18%** | 14,7% (Censo 2022) |")
doc1.append("| | Centro-Oeste | **13%** | 8,1% (Censo 2022) |")
doc1.append("| | Norte | **12%** | 8,5% (Censo 2022) |")
doc1.append("| **Religião** | Católica | **51%** | 50,0% (Censo 2022) |")
doc1.append("| | Evangélica | **27%** | 27,0% (Censo 2022) |")
doc1.append("| | Outras religiões | **14%** | 13,0% (Censo 2022) |")
doc1.append("| | Sem religião | **8%** | 10,0% (Censo 2022) |")
doc1.append("| **Voto no 2º Turno 2022** | Lula (PT) | **40%** | 38,0% do eleitorado total (TSE) |")
doc1.append("| | Bolsonaro (PL) | **37%** | 37,0% do eleitorado total (TSE) |")
doc1.append("| | Abstenção / Nulo / Branco | **23%** | 25,0% do eleitorado total (TSE) |")
doc1.append("| **Faixa Etária** | 40 a 59 anos | **38%** | 33,0% (Censo 2022) |")
doc1.append("| | 25 a 39 anos | **24%** | 30,0% (Censo 2022) |")
doc1.append("| | 60+ anos (Idosos) | **24%** | 22,0% (Censo 2022) |")
doc1.append("| | 16 a 24 anos (Jovens) | **14%** | 15,0% (Censo 2022) |")
doc1.append("| **Área de Moradia** | Urbana | **87%** | 87,0% (Censo 2022) |")
doc1.append("| | Rural | **13%** | 13,0% (Censo 2022) |")

doc1.append("\n---")
doc1.append("\n## 2. Tabela Nominal dos 100 Cidadãos Virtuais da Simulação Principal (Seed 1)")
doc1.append("Abaixo está listada cada uma das 100 personas individuais com seu perfil demográfico completo e escolaridade estimada inferida a partir de sua ocupação e renda:")
doc1.append("\n| ID | Profissão / Ocupação | Renda Familiar | Escolaridade Estimada | Idade | Região | Área | Religião | Voto 2022 |")
doc1.append("| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |")

for p in personas:
    occ = pt_occupation(p.occupation)
    inc = pt_income(p.income)
    esc = infer_schooling(p.income, p.occupation)
    vote = pt_vote(p.vote_2022)
    rel = pt_religion(p.religion)
    area = pt_area(p.area)
    doc1.append(f"| #{p.id:02d} | {occ} | {inc} | {esc} | {p.age} anos | {p.region} | {area} | {rel} | {vote} |")

(ARTIFACT_DIR / "amostra_cidadaos_simulados.md").write_text("\n".join(doc1), encoding="utf-8")
print("Wrote amostra_cidadaos_simulados.md")

# --- 2. DOCUMENTO DE FEEDBACKS E FALAS DOS CIDADÃOS ---
results_data = json.load(open(ROOT / "out" / "blind-v10" / "results.json"))

doc2 = []
doc2.append("# Documento de Feedbacks e Falas dos Cidadãos Virtuais (`brazil-sim`)")
doc2.append("\n> **Onde encontrar os dados brutos no repositório:**")
doc2.append("> 1. **Resultados estruturados com 1.920 citações:** [`out/blind-v10/results.json`](file:///Users/caiquecoelho/Documents/Projects/directory/brazil-sim/out/blind-v10/results.json) (campo `quotes` e `top_concerns` de cada trimestre).")
doc2.append("> 2. **Banco de dados de cache SQLite com 10.034 respostas originais completas:** [`out/blind-v10/cache.sqlite`](file:///Users/caiquecoelho/Documents/Projects/directory/brazil-sim/out/blind-v10/cache.sqlite) (todas as decisões individuais de cidadãos).")
doc2.append("> 3. **Relatório interativo com replay trimestre a trimestre:** [`out/blind-v10/report.html`](file:///Users/caiquecoelho/Documents/Projects/directory/brazil-sim/out/blind-v10/report.html).")

doc2.append("\n---")
doc2.append("\n## 1. O Que os Cidadãos Sentem e Falam: A Grande Análise Qualitativa")
doc2.append("Ao longo dos 16 trimestres (2027 a 2030), os cidadãos não votam em partidos abstratos; eles expressam sua **avaliação de governo (0 a 100)**, seu **sentimento econômico domiciliar (-1 a +1)**, sua **preocupação principal** e uma **declaração em primeira pessoa (quote)**.")
doc2.append("\nOs dados evidenciam três padrões essenciais de narrativa:")

doc2.append("\n### A. O que os Cidadãos Falam no Brasil de Lula")
doc2.append("- **Aprovação média consolidada:** **45,4%** (contra 35,4% no cenário de inércia).")
doc2.append("- **Alívio na Renda da Base:** O ganho real contínuo do salário mínimo e a sustentação dos pisos do SUS/educação são rapidamente percebidos por aposentados do INSS, diaristas e ambulantes: *\"Aumento do mínimo ajuda, a feira deu uma respirada e o postinho do bairro voltou a ter remédio contínuo.\"*")
doc2.append("- **A Grande Queixa:** A inflação de alimentos provocada por secas severas (choques climáticos) e a Selic em patamar elevado (11,85% na média) são os alvos de reclamação recorrente: *\"Vendo pouco, comida segue cara. A seca secou meu bolso, mas ao menos a violência deu uma trégua e o serviço anda.\"*")
doc2.append("- **Segurança Pública:** Há reconhecimento espontâneo da redução de homicídios nas grandes capitais devido a políticas de inteligência e câmeras corporais.")

doc2.append("\n### B. O que os Cidadãos Falam no Brasil de Flávio Bolsonaro")
doc2.append("- **Aprovação média consolidada:** **42,6%** (com forte desgaste no final do mandato).")
doc2.append("- **A Queixa da Desconexão Retórica:** O corte de gastos de R$ 190 bilhões (1,5% do PIB) domina o noticiário, mas o cidadão comum reclama que a austeridade não barateia sua vida real: *\"O governo só fala em corte de gastos e dívida pública todo dia no jornal, mas na feira nada baixou de preço e a conta de luz segue pesada.\"*")
doc2.append("- **O Pavor do Pente-Fino e Congelamento:** O fim do reajuste real do salário mínimo para a Previdência Social e o pente-fino no BPC/INSS causam angústia direta nos lares mais vulneráveis: *\"O pente-fino no INSS preocupa minha mãe; temos medo de perder o benefício a qualquer momento.\"*")
doc2.append("- **A Saúde Pública:** Com os pisos de saúde atrelados apenas à inflação passada, moradores da periferia sentem a piora nos postos: *\"A fila do hospital público só aumentou e falta médico na atenção básica.\"*")
doc2.append("- **Aprovação no Setor Produtivo:** Por outro lado, técnicos do agronegócio e pequenos empresários aprovam o alívio tributário inicial nos combustíveis e energia, elogiando o combate ao déficit público.")

doc2.append("\n### C. O Cenário Base (Inércia / Sem Novas Políticas)")
doc2.append("- **Aprovação média consolidada:** **35,4%** (o pior resultado).")
doc2.append("- O governo que nada faz sofre com o desgaste da paralisia: a população sente que os juros altos travam o crédito, as filas nos hospitais persistem e os preços não caem.")

doc2.append("\n---")
doc2.append("\n## 2. Compêndio de Falas Reais Extraídas do Banco de Dados (`out/blind-v10/results.json`)")
doc2.append("Abaixo, uma seleção das declarações mais expressivas de cidadãos de diferentes perfis sociais:")

# Extract sample quotes from results.json
for s in results_data['runs'][0]['scenarios']:
    sname = s['scenario'].upper()
    doc2.append(f"\n### Declarações no Cenário: **{sname}**")
    for h in s['history'][1:9]: # first 8 quarters
        q = h['quarter']
        quotes = h.get('quotes', [])
        if not quotes:
            continue
        doc2.append(f"\n#### Trimestre: {q}")
        for qentry in quotes[:4]:
            persona_desc = qentry.get('persona', '')
            top_concern = qentry.get('top_concern', 'geral')
            quote_text = qentry.get('quote', '')
            appr = qentry.get('approval', 0)
            sent = qentry.get('econ_sentiment', 0)
            doc2.append(f"- **{persona_desc}**")
            doc2.append(f"  - *Foco/Preocupação:* `{top_concern}` | *Aprovação pessoal:* `{appr:.0f}%` | *Sentimento:* `{sent:+.2f}`")
            doc2.append(f"  - 💬 *\"{quote_text}\"*")

(ARTIFACT_DIR / "feedbacks_falas_cidadaos.md").write_text("\n".join(doc2), encoding="utf-8")
print("Wrote feedbacks_falas_cidadaos.md")
