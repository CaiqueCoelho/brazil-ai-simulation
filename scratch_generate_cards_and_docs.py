import json
import subprocess
from pathlib import Path
from collections import Counter
from sim.agents import sample_personas

ROOT = Path("/Users/caiquecoelho/Documents/Projects/directory/brazil-sim")
ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

shares = json.load(open(ROOT / "data" / "personas_shares.json"))
personas = sample_personas(shares, 100, 1)

# Helper to map education
def infer_schooling(income, occupation):
    if income == "up to 1 minimum wage":
        return "Fundamental (Incompleto/Completo)"
    elif income == "1-2 minimum wages":
        if "technician" in occupation or "small farmer" in occupation:
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
        "voted for the PT candidate": "Votou no candidato do PT (Lula)",
        "voted for the PL candidate": "Votou no candidato do PL (Bolsonaro)",
        "abstained or voted null/blank": "Absteve-se / Voto Nulo ou Branco"
    }
    return mapping.get(v, v)

def pt_religion(r):
    mapping = {
        "Catholic": "Católica",
        "Evangelical": "Evangélica",
        "No religion": "Sem religião",
        "Other": "Outras religiões (Espírita, Umbanda, etc.)"
    }
    return mapping.get(r, r)

def pt_occupation(o):
    mapping = {
        "informal street vendor": "Vendedor(a) ambulante informal",
        "rural day laborer": "Trabalhador(a) rural diarista",
        "unemployed and looking for work": "Desempregado(a) buscando vaga",
        "domestic worker": "Trabalhadora doméstica",
        "app delivery rider": "Entregador(a) de aplicativo",
        "retiree on minimum pension": "Aposentado(a) com piso mínimo",
        "supermarket cashier": "Caixa de supermercado",
        "construction worker": "Operário(a) da construção civil",
        "call-center operator": "Operador(a) de teleatendimento",
        "truck driver": "Motorista de caminhão / caminhoneiro(a)",
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

print("Setup completed successfully.")
