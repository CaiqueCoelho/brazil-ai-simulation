METRICS = [
    {"key": "gdp_growth", "item": "Economia", "label": "Crescimento do PIB", "unit": "% ao ano", "dec": 1, "better": "higher", "group": "Economia",
     "explain": "Quanto a produção total do país cresce em um ano. Mais crescimento costuma significar mais empregos e renda."},
    {"key": "inflation", "item": "Economia", "label": "Inflação (IPCA)", "unit": "% em 12 meses", "dec": 1, "better": "target", "target": 3.0, "group": "Economia",
     "explain": "Quanto os preços sobem em 12 meses. O melhor é ficar perto da meta oficial de 3%: muito acima corrói salários, muito abaixo indica economia fraca."},
    {"key": "selic", "item": "Economia", "label": "Taxa Selic", "unit": "% ao ano", "dec": 2, "better": "lower", "group": "Economia",
     "explain": "Juro básico definido pelo Banco Central. Mais baixo barateia crédito e financiamentos; sobe quando a inflação ameaça sair do controle."},
    {"key": "unemployment", "label": "Desemprego", "unit": "% da força de trabalho", "dec": 1, "better": "lower", "group": "Economia",
     "explain": "Parcela de quem procura trabalho e não encontra (PNAD Contínua/IBGE)."},
    {"key": "debt_gdp", "item": "Contas públicas", "label": "Dívida pública bruta", "unit": "% do PIB", "dec": 1, "better": "lower", "group": "Contas públicas",
     "explain": "Tudo o que o governo deve, comparado ao tamanho da economia. Quanto maior, mais caro fica se financiar e menor a margem para crises."},
    {"key": "primary_balance", "item": "Contas públicas", "label": "Resultado primário", "unit": "% do PIB", "dec": 2, "better": "higher", "group": "Contas públicas",
     "explain": "Receitas menos despesas do governo, sem contar juros. Positivo = superávit (sobra dinheiro); negativo = déficit."},
    {"key": "poverty_rate", "label": "Pobreza", "unit": "% da população", "dec": 1, "better": "lower", "group": "Social",
     "explain": "Parcela da população abaixo da linha de pobreza."},
    {"key": "gini", "label": "Desigualdade (Gini)", "unit": "índice de 0 a 1", "dec": 3, "better": "lower", "group": "Social",
     "explain": "Mede a concentração de renda: 0 = todos ganham igual; 1 = uma pessoa fica com tudo."},
    {"key": "infant_mortality", "label": "Mortalidade infantil", "unit": "mortes por mil nascidos vivos", "dec": 2, "better": "lower", "group": "Saúde",
     "explain": "Indicador clássico de saúde pública: bebês que morrem antes de completar 1 ano. Reage a pobreza, saneamento e acesso ao SUS."},
    {"key": "food_insecurity", "label": "Fome (subalimentação)", "unit": "% da população", "dec": 2, "better": "lower", "group": "Saúde",
     "explain": "Parcela da população sem acesso a comida suficiente, no padrão da FAO/ONU. Abaixo de 2,5%, o país fica fora do Mapa da Fome."},
    {"key": "homicides_per_100k", "label": "Homicídios", "unit": "por 100 mil habitantes", "dec": 1, "better": "lower", "group": "Segurança",
     "explain": "Assassinatos por ano para cada 100 mil pessoas."},
    {"key": "deforestation_km2", "label": "Desmatamento na Amazônia", "unit": "km² por ano", "dec": 0, "better": "lower", "group": "Meio ambiente",
     "explain": "Área de floresta derrubada por ano (padrão PRODES/INPE)."},
    {"key": "approval", "label": "Aprovação do presidente", "unit": "% dos cidadãos simulados", "dec": 0, "better": "higher", "group": "Política",
     "explain": "Média da aprovação dada pelos 200 cidadãos virtuais a cada trimestre."},
    {"key": "institutional_stability", "item": "Democracia", "label": "Estabilidade institucional", "unit": "índice de 0 a 100", "dec": 0, "better": "higher", "group": "Democracia",
     "explain": "Quão harmônica é a relação entre os Poderes. Cai com conflitos com o STF, decisões suspensas pela Justiça e escândalos."},
    {"key": "democracy_risk", "item": "Democracia", "label": "Risco democrático", "unit": "índice de 0 a 100", "dec": 0, "better": "lower", "group": "Democracia",
     "explain": "Combina instabilidade entre os Poderes, polarização da opinião pública e tentativas de limitar tribunais (mesmo as que fracassam). Quanto maior, mais risco."},
]

BY_KEY = {m["key"]: m for m in METRICS}

ITEM_EXPLAIN = {
    "Economia": "Crescimento, inflação e juros andam juntos, então contam como um item só.",
    "Contas públicas": "Dívida e resultado primário medem a mesma coisa, então contam como um item só.",
    "Democracia": "Estabilidade institucional e risco democrático medem a mesma coisa, então contam como um item só.",
}


def item_of(key: str) -> str:
    return BY_KEY[key].get("item", BY_KEY[key]["label"])
