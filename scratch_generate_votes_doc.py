import json
from pathlib import Path

ROOT = Path("/Users/caiquecoelho/Documents/Projects/directory/brazil-sim")
ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")

results_data = json.load(open(ROOT / "out" / "blind-v10" / "results.json"))
policies_lula = {p['id']: p for p in json.load(open(ROOT / "data" / "policies_lula.json"))['policies']}
policies_flavio = {p['id']: p for p in json.load(open(ROOT / "data" / "policies_flavio.json"))['policies']}

def pt_vote(v):
    return {"approve": "Aprovar (Sim)", "amend": "Emendar (Modificar)", "reject": "Rejeitar (Não)"}.get(v, v)

def pt_outcome(o):
    return {"approve": "✅ Aprovado Integral", "amend": "⚠️ Aprovado com Emendas (Desidratado)", "reject": "❌ Rejeitado"}.get(o, o)

def pt_title(cand, pid):
    mapping = {
        "lula": {
            "P02": "Fim da escala 6x1 / Jornada de 40h com 2 dias de folga",
            "P03": "Criação do Ministério da Segurança Pública Federal",
            "P16": "Inclusão da Escola em Tempo Integral no Fundeb"
        },
        "flavio": {
            "P01": "Corte de gastos de 1,5% do PIB (R$ 190 bi) e nova regra fiscal",
            "P02": "Fusão ou extinção de pelo menos dez ministérios",
            "P03": "Redução de tributos sobre consumo, combustíveis e energia",
            "P04": "Retomada de privatizações de estatais",
            "P07": "Enquadramento de facções como terrorismo e novos presídios",
            "P08": "Redução da maioridade penal",
            "P09": "Penas mais duras e rigorosas para crimes graves",
            "P10": "Restrição de decisões e poderes monocráticos do STF",
            "P11": "Fim da reeleição para presidente da República",
            "P16": "Flexibilização do licenciamento ambiental",
            "P17": "Redução de custos trabalhistas / desoneração da folha",
            "P18": "Vouchers para creches e escolas privadas",
            "P19": "Financiamento estudantil vinculado à renda futura"
        }
    }
    return mapping.get(cand, {}).get(pid, pid)

def get_policy_type(cand, pid):
    p = policies_lula.get(pid) if cand == 'lula' else policies_flavio.get(pid)
    if not p: return "Projeto de Lei"
    if p.get('constitutional_amendment'):
        return "PEC (3/5 dos votos)"
    return "Projeto de Lei (Maioria)"

doc = []
doc.append("# Mapa Completo das Votações no Congresso Nacional: Projetos de Lei e PECs (`brazil-sim`)")
doc.append("\n> **Metodologia Institucional:** O Congresso Nacional simulado é composto pelas 513 cadeiras da Câmara dos Deputados com a correlação de forças eleita em 4 de outubro de 2026:")
doc.append("> - **Esquerda:** 24,2% (124 deputados — PT, PSB, PDT, PSOL, PCdoB, PV, Rede)")
doc.append("> - **Centrão:** 50,1% (257 deputados — PP, União Brasil, PSD, MDB, Republicanos, Podemos)")
doc.append("> - **Direita:** 25,7% (132 deputados — PL, Novo e aliados conservadores)")
doc.append(">")
doc.append("> As matérias de lei ordinária exigem **maioria simples (> 50%)**; Emendas à Constituição (**PECs**) exigem **quórum qualificado de 3/5 (≥ 60%)**.")

doc.append("\n---")
doc.append("\n## 1. Princípios da Votação Legislativa e o Papel do Centrão")
doc.append("1. **O Centrão é o fiel absoluto da balança:** Com 50,1% das cadeiras, o Centrão decide sozinho o destino de projetos ordinários e é peça obrigatória para qualquer PEC. Como a Esquerda tem apenas 24,2% e a Direita 25,7%, nenhum dos polos ideológicos consegue aprovar absolutamente nada sem negociar com o centro fisiológico.")
doc.append("2. **A estratégia do 'Emendar' (`amend`):** Em vez de confrontar o Executivo com rejeições diretas, o Centrão atua majoritariamente desidratando os projetos (reduzindo a força da alavanca em 50%) e condicionando os votos à liberação de **0,10% a 0,20% do PIB em emendas parlamentares**.")
doc.append("3. **O Filtro Constitucional do STF:** Projetos com risco de inconstitucionalidade flagrante aprovados pelo Congresso são encaminhados ao Supremo Tribunal Federal, que pode suspendê-los liminarmente.")

doc.append("\n---")
doc.append("\n## 2. Resumo dos Resultados por Plataforma de Governo")

doc.append("\n### A. No Governo Lula (3 Propostas Legislativas Enviadas ao Congresso)")
doc.append("- **PEC P02 (Fim da Escala 6x1 / 40h semanais):** Enviada ao Congresso, foi **aprovada com modificações (`amend`)** em todas as 5 sementes. A Esquerda votou a favor, a Direita votou contra e o Centrão votou por emendar. A soma Esquerda + Centrão atingiu **74,3% > 60%**, aprovando uma versão atenuada da redução de jornada.")
doc.append("- **Projeto de Lei P03 (Ministério da Segurança Pública Federal):** Aprovado plenamente em 4 das 5 sementes e com emendas em 1 semente, contando com apoio amplo do Centrão e da Esquerda.")
doc.append("- **PEC P16 (Escola em Tempo Integral no Fundeb):** Aprovada com folga com votos da Esquerda e do Centrão nas 5 sementes.")
doc.append("- *Atuação do STF no Governo Lula:* **Zero medidas suspensas**, pois os projetos respeitaram as balizas constitucionais e o arcabouço.")

doc.append("\n### B. No Governo Flávio Bolsonaro (13 Propostas Legislativas Enviadas)")
doc.append("- **PEC P01 (Corte de Gastos de 1,5% do PIB / Nova Regra Fiscal):** Aprovada com emendas (`amend`) em todas as 5 sementes. A Direita votou a favor, a Esquerda votou contra e o Centrão aprovou em versão desidratada para preservar parte dos repasses orçamentários.")
doc.append("- **Projeto de Lei P02 (Extinção de 10 Ministérios):** Aprovado com emendas (`amend`), pois o Centrão resistiu à extinção de pastas com influência regional.")
doc.append("- **Projeto de Lei P03 (Corte de Tributos em Combustíveis e Energia):** Aprovado com apoio da Direita e do Centrão.")
doc.append("- **Projetos Penais P07, P08 e P09 (Terrorismo para Facções, Maioridade Penal e Penas Duras):** Aprovados no Congresso pela aliança Direita + Centrão, mas **P09 (penas duras) e P08 foram sistematicamente suspensos pelo STF** por ferirem cláusulas pétreas e direitos fundamentais.")
doc.append("- **PEC P10 (Limitação dos Poderes do STF):** Sofreu resistência brutal. Foi **rejeitada pelo Congresso em 2 sementes e suspensa pelo próprio STF nas outras 3 sementes**, gerando grave crise de estabilidade institucional.")
doc.append("- **Projeto de Lei P16 (Flexibilização do Licenciamento Ambiental):** Aprovado com facilidade pela bancada ruralista (Centrão + Direita), mas **suspenso pelo STF em 100% das sementes** por violação ao artigo 225 da Constituição Federal.")

doc.append("\n---")
doc.append("\n## 3. Tabela Completa de Todas as Votações (Rodada a Rodada)")

for run in results_data['runs']:
    seed = run['seed']
    doc.append(f"\n### Simulação / Semente {seed} (Seed {seed})")
    
    for sc in run['scenarios']:
        sname = sc['scenario']
        doc.append(f"\n#### Cenário: **{sname.upper()}**")
        doc.append("| Trimestre | ID | Matéria / Proposta | Tipo | Voto Esquerda (24%) | Voto Centrão (50%) | Voto Direita (26%) | Resultado do Plenário | Posição do STF |")
        doc.append("| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        
        has_votes = False
        for h in sc['history']:
            if h.get('votes'):
                has_votes = True
                q = h['quarter']
                suspended_list = h.get('suspended', [])
                for pid, outcome in h['votes'].items():
                    title = pt_title(sname, pid)
                    ptype = get_policy_type(sname, pid)
                    bv = h.get('bloc_votes', {})
                    v_left = pt_vote(bv.get('left', {}).get(pid, 'n/a'))
                    v_cen = pt_vote(bv.get('centrao', {}).get(pid, 'n/a'))
                    v_right = pt_vote(bv.get('right', {}).get(pid, 'n/a'))
                    res = pt_outcome(outcome)
                    stf_status = "⚠️ **Suspenso**" if pid in suspended_list else "Válido"
                    doc.append(f"| {q} | `{pid}` | {title} | {ptype} | {v_left} | {v_cen} | {v_right} | {res} | {stf_status} |")
        
        if not has_votes:
            doc.append("| - | - | Nenhuma matéria enviada ao Congresso neste cenário | - | - | - | - | - | - |")

(ARTIFACT_DIR / "votacoes_congresso_pecs_leis.md").write_text("\n".join(doc), encoding="utf-8")
print("Wrote votacoes_congresso_pecs_leis.md successfully.")
