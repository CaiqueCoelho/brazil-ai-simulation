"""Generates 4 social cards as HTML files in out/social/ sized 1200x675 for export to PNG."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RUN_DIR = OUT / "blind-v10"
SOCIAL_DIR = OUT / "social"
SOCIAL_DIR.mkdir(parents=True, exist_ok=True)

# Load data
analysis = json.loads((RUN_DIR / "analysis.json").read_text())
sens = json.loads((RUN_DIR / "sensitivity.json").read_text())
results = json.loads((RUN_DIR / "results.json").read_text())

# Common HTML template wrapper
def wrap_card(content: str, title: str) -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1200px;
    height: 675px;
    overflow: hidden;
    background: #0f141c;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 38px 48px;
    position: relative;
  }}
  /* Ambient glow background */
  body::before {{
    content: "";
    position: absolute;
    top: -100px;
    left: -100px;
    width: 450px;
    height: 450px;
    background: radial-gradient(circle, rgba(42, 120, 214, 0.18) 0%, transparent 70%);
    pointer-events: none;
  }}
  body::after {{
    content: "";
    position: absolute;
    bottom: -100px;
    right: -100px;
    width: 450px;
    height: 450px;
    background: radial-gradient(circle, rgba(235, 104, 52, 0.16) 0%, transparent 70%);
    pointer-events: none;
  }}
  .header {{
    position: relative;
    z-index: 2;
  }}
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 10px;
  }}
  .badge-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #38bdf8;
  }}
  h1 {{
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.5px;
    line-height: 1.15;
    color: #ffffff;
    margin-bottom: 6px;
  }}
  .subtitle {{
    font-size: 15px;
    color: #94a3b8;
    line-height: 1.35;
  }}
  .main-content {{
    position: relative;
    z-index: 2;
    flex: 1;
    display: flex;
    align-items: center;
    margin: 14px 0;
  }}
  .footer {{
    position: relative;
    z-index: 2;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: #64748b;
  }}
  .footer-left strong {{
    color: #94a3b8;
  }}
  .footer-right {{
    color: #38bdf8;
    font-weight: 600;
  }}
  /* Custom utility classes */
  .blue {{ color: #3b82f6; }}
  .orange {{ color: #f97316; }}
  .gray {{ color: #94a3b8; }}
</style>
</head>
<body>
{content}
</body>
</html>"""


# ==========================================
# CARD 1: PLACAR GERAL (HERO SCORECARD)
# ==========================================
def make_card1():
    content = """
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>EXPERIMENTO COM IA · BRASIL 2027–2030</div>
    <h1>Placar Final: Lula 9 × 1 Flávio Bolsonaro</h1>
    <p class="subtitle">4 anos de governo simulados com as propostas do TSE sob as mesmas regras e choques externos</p>
  </div>

  <div class="main-content" style="display: flex; gap: 32px; width: 100%;">
    <!-- Big Score Panel -->
    <div style="flex: 0 0 440px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px 28px; display: flex; flex-direction: column; justify-content: space-between;">
      <div style="display: flex; justify-content: space-between; align-items: baseline;">
        <div>
          <div style="font-size: 14px; font-weight: 800; color: #3b82f6; letter-spacing: 1.5px; text-transform: uppercase;">LULA</div>
          <div style="font-size: 88px; font-weight: 900; line-height: 1; color: #ffffff; margin-top: 4px;">9</div>
          <div style="font-size: 13px; color: #94a3b8; font-weight: 600; margin-top: 4px;">vitórias em 11 itens</div>
        </div>
        <div style="font-size: 28px; font-weight: 300; color: #475569; margin: 0 10px;">×</div>
        <div style="text-align: right;">
          <div style="font-size: 14px; font-weight: 800; color: #f97316; letter-spacing: 1.5px; text-transform: uppercase;">FLÁVIO</div>
          <div style="font-size: 88px; font-weight: 900; line-height: 1; color: #ffffff; margin-top: 4px;">1</div>
          <div style="font-size: 13px; color: #94a3b8; font-weight: 600; margin-top: 4px;">vitória em 11 itens</div>
        </div>
      </div>

      <!-- Segmented Bar -->
      <div style="margin-top: 18px;">
        <div style="display: flex; gap: 5px; height: 16px;">
          <div style="flex: 9; background: #3b82f6; border-radius: 4px;" title="9 vitórias Lula"></div>
          <div style="flex: 1; background: #64748b; border-radius: 4px;" title="1 empate"></div>
          <div style="flex: 1; background: #f97316; border-radius: 4px;" title="1 vitória Flávio"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: #64748b; margin-top: 6px;">
          <span>9 Lula (azul)</span>
          <span>1 Empate técnico (cinza)</span>
          <span>1 Flávio (laranja)</span>
        </div>
      </div>
    </div>

    <!-- Items Breakdown -->
    <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; gap: 10px;">
      <!-- Lula group -->
      <div style="background: rgba(59, 130, 246, 0.08); border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 0 10px 10px 0;">
        <div style="font-size: 12px; font-weight: 800; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px;">
          🔵 Onde o plano de Lula venceu (9 itens)
        </div>
        <div style="font-size: 13px; color: #e2e8f0; line-height: 1.4;">
          <strong>Desemprego</strong> (5,8%), <strong>Pobreza</strong> (17,4%), <strong>Desigualdade Gini</strong> (0,489), <strong>Fome</strong> (3,1%), <strong>Saúde</strong> (mortalidade 10,9), <strong>Segurança</strong> (homicídios 16,8), <strong>Meio Ambiente</strong> (desmatamento cai 44%), <strong>Aprovação</strong> (44%) e <strong>Democracia</strong>.
        </div>
      </div>

      <!-- Flávio group -->
      <div style="background: rgba(249, 115, 22, 0.08); border-left: 4px solid #f97316; padding: 10px 14px; border-radius: 0 10px 10px 0;">
        <div style="font-size: 12px; font-weight: 800; color: #fb923c; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px;">
          🟠 Onde o plano de Flávio venceu (1 item)
        </div>
        <div style="font-size: 13px; color: #e2e8f0; line-height: 1.4;">
          <strong>Contas Públicas</strong>: o corte de 1,5% do PIB zera o déficit fiscal e reduz a dívida bruta para <strong>85,2% do PIB</strong> (contra 88,4% com Lula).
        </div>
      </div>

      <!-- Empate -->
      <div style="background: rgba(148, 163, 184, 0.08); border-left: 4px solid #94a3b8; padding: 8px 14px; border-radius: 0 10px 10px 0;">
        <div style="font-size: 12px; font-weight: 800; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 2px;">
          ⚪ Onde houve empate técnico (1 item)
        </div>
        <div style="font-size: 13px; color: #cbd5e1; line-height: 1.35;">
          <strong>Economia Geral</strong>: Lula tem maior PIB médio (1,8% vs 1,7%); Flávio tem inflação e Selic ligeiramente menores.
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer-left">
      <strong>Aviso:</strong> Não é previsão nem pesquisa eleitoral · Modelagem de IA com dados públicos oficiais (2018–2026)
    </div>
    <div class="footer-right">
      github.com/CaiqueCoelho/brazil-ai-simulation
    </div>
  </div>
"""
    return wrap_card(content, "Card 1 - Placar Geral")


# ==========================================
# CARD 2: TABELA COMPARATIVA COMPLETA
# ==========================================
def make_card2():
    rows_data = [
        ("PIB (crescimento médio)", "1,8% a.a.", "1,7% a.a.", "1,6% a.a.", "Lula (empate item)", "#3b82f6"),
        ("Inflação (IPCA médio)", "3,9%", "3,8%", "3,9%", "Flávio (empate item)", "#f97316"),
        ("Taxa Selic média", "8,6%", "8,3%", "8,6%", "Flávio (empate item)", "#f97316"),
        ("Contas Públicas (Primário)", "-0,6% PIB", "+0,1% PIB", "-0,9% PIB", "Flávio", "#f97316"),
        ("Dívida Pública Bruta (2030)", "88,4% PIB", "85,2% PIB", "89,7% PIB", "Flávio", "#f97316"),
        ("Taxa de Desemprego (2030)", "5,8%", "8,2%", "7,5%", "Lula", "#3b82f6"),
        ("Pobreza", "17,4%", "23,8%", "23,3%", "Lula", "#3b82f6"),
        ("Desigualdade (Índice Gini)", "0,489", "0,518", "0,516", "Lula", "#3b82f6"),
        ("Fome (Subalimentação)", "3,1%", "4,2%", "3,9%", "Lula", "#3b82f6"),
        ("Mortalidade Infantil (por mil)", "10,9", "13,2", "12,6", "Lula", "#3b82f6"),
        ("Homicídios (por 100k hab.)", "16,8", "18,2", "19,8", "Lula", "#3b82f6"),
        ("Desmatamento Amazônia", "4.116 km²", "7.424 km²", "6.136 km²", "Lula", "#3b82f6"),
        ("Aprovação Cidadãos Virtuais", "44%", "31%", "29%", "Lula", "#3b82f6"),
    ]

    tbody = ""
    for ind, lula, flav, base, win, col in rows_data:
        tbody += f"""
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.06); font-size: 12.5px;">
          <td style="padding: 4px 8px; color: #f8fafc; font-weight: 500;">{ind}</td>
          <td style="padding: 4px 8px; text-align: center; color: #93c5fd; font-weight: 700; font-variant-numeric: tabular-nums;">{lula}</td>
          <td style="padding: 4px 8px; text-align: center; color: #fdba74; font-weight: 700; font-variant-numeric: tabular-nums;">{flav}</td>
          <td style="padding: 4px 8px; text-align: center; color: #64748b; font-variant-numeric: tabular-nums;">{base}</td>
          <td style="padding: 4px 8px; text-align: right; color: {col}; font-weight: 800;">{win}</td>
        </tr>
        """

    content = f"""
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>COMPARATIVO COMPLETO DOS INDICADORES</div>
    <h1 style="font-size: 28px;">Resultados Finais após 4 Anos de Simulação (2030)</h1>
    <p class="subtitle">Média de 5 simulações sob choques externos idênticos (Banco Central, IBGE, INPE e Ipea)</p>
  </div>

  <div class="main-content" style="margin: 6px 0;">
    <table style="width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; overflow: hidden;">
      <thead>
        <tr style="background: rgba(255,255,255,0.06); font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.12);">
          <th style="padding: 6px 8px; text-align: left;">Indicador Oficial</th>
          <th style="padding: 6px 8px; text-align: center; color: #60a5fa;">Lula</th>
          <th style="padding: 6px 8px; text-align: center; color: #fb923c;">Flávio Bolsonaro</th>
          <th style="padding: 6px 8px; text-align: center;">Cenário Base</th>
          <th style="padding: 6px 8px; text-align: right;">Melhor Resultado</th>
        </tr>
      </thead>
      <tbody>
        {tbody}
      </tbody>
    </table>
  </div>

  <div class="footer">
    <div class="footer-left">
      Regra: Vence quem é melhor na média e na maioria das sementes · Margens oficiais toleradas como empate
    </div>
    <div class="footer-right">
      github.com/CaiqueCoelho/brazil-ai-simulation
    </div>
  </div>
"""
    return wrap_card(content, "Card 2 - Tabela Comparativa")


# ==========================================
# CARD 3: O GRANDE TRADE-OFF (FISCAL VS SOCIAL)
# ==========================================
def make_card3():
    content = """
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>MECANISMOS ECONÔMICOS</div>
    <h1>O Grande Trade-off: Disciplina Fiscal vs Proteção Social</h1>
    <p class="subtitle">Entenda os motores econômicos que ditaram os pontos fortes e fracos de cada plano</p>
  </div>

  <div class="main-content" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; width: 100%;">
    <!-- Card Flávio: Ajuste Fiscal -->
    <div style="background: rgba(249, 115, 22, 0.05); border: 1px solid rgba(249, 115, 22, 0.25); border-radius: 14px; padding: 22px 24px; display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <span style="font-size: 13px; font-weight: 800; color: #fb923c; text-transform: uppercase; letter-spacing: 1px;">FLÁVIO BOLSONARO</span>
          <span style="background: #f97316; color: #000; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px;">VENCEDOR FISCAL</span>
        </div>
        <div style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 8px;">Corte de Gastos e Ajuste Rápido</div>
        
        <div style="font-size: 13px; color: #cbd5e1; line-height: 1.45; margin-bottom: 14px;">
          • <strong>O que funcionou:</strong> Corte de 1,5% do PIB (R$ 190 bi) e desregulamentação zeraram o déficit primário (+0,1% PIB) e reduziram a dívida para <strong>85,2%</strong>. Inflação e Selic foram levemente menores.<br><br>
          • <strong>O custo social:</strong> Como evidenciam estudos do FMI (Guajardo et al.), cortes orçamentários profundos desaceleram a economia no curto prazo. O desvinculamento do salário mínimo e aperto nos pisos de saúde elevaram o <strong>desemprego a 8,2%</strong> e a <strong>pobreza a 23,8%</strong>.
        </div>
      </div>

      <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 10px 14px; display: flex; justify-content: space-around; text-align: center;">
        <div><div style="font-size: 11px; color: #94a3b8;">Dívida / PIB</div><div style="font-size: 18px; font-weight: 800; color: #fb923c;">85,2%</div></div>
        <div><div style="font-size: 11px; color: #94a3b8;">Desemprego</div><div style="font-size: 18px; font-weight: 800; color: #ef4444;">8,2%</div></div>
        <div><div style="font-size: 11px; color: #94a3b8;">Pobreza</div><div style="font-size: 18px; font-weight: 800; color: #ef4444;">23,8%</div></div>
      </div>
    </div>

    <!-- Card Lula: Demanda e Renda -->
    <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 14px; padding: 22px 24px; display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
          <span style="font-size: 13px; font-weight: 800; color: #60a5fa; text-transform: uppercase; letter-spacing: 1px;">LULA</span>
          <span style="background: #3b82f6; color: #fff; font-size: 11px; font-weight: 800; padding: 2px 8px; border-radius: 6px;">VENCEDOR SOCIAL</span>
        </div>
        <div style="font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 8px;">Estímulo à Demanda e Redes de Proteção</div>
        
        <div style="font-size: 13px; color: #cbd5e1; line-height: 1.45; margin-bottom: 14px;">
          • <strong>O que funcionou:</strong> Valorização real do salário mínimo, saneamento e programas sociais reduziram o <strong>desemprego a 5,8%</strong> e a <strong>pobreza a 17,4%</strong>. O desmatamento caiu para 4.116 km² com fiscalização e multas ativas.<br><br>
          • <strong>O custo fiscal:</strong> Dívida bruta permaneceu mais alta (<strong>88,4% do PIB</strong>). O arcabouço fiscal manteve o déficit estável em -0,6% do PIB, compensado pela maior arrecadação vinda do crescimento econômico (PIB médio de 1,8%).
        </div>
      </div>

      <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 10px 14px; display: flex; justify-content: space-around; text-align: center;">
        <div><div style="font-size: 11px; color: #94a3b8;">Dívida / PIB</div><div style="font-size: 18px; font-weight: 800; color: #94a3b8;">88,4%</div></div>
        <div><div style="font-size: 11px; color: #94a3b8;">Desemprego</div><div style="font-size: 18px; font-weight: 800; color: #38bdf8;">5,8%</div></div>
        <div><div style="font-size: 11px; color: #94a3b8;">Pobreza</div><div style="font-size: 18px; font-weight: 800; color: #38bdf8;">17,4%</div></div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer-left">
      Regra de Taylor calibrada no Banco Central · Mercado financeiro respondeu rigorosamente aos mesmos parâmetros
    </div>
    <div class="footer-right">
      github.com/CaiqueCoelho/brazil-ai-simulation
    </div>
  </div>
"""
    return wrap_card(content, "Card 3 - Trade-offs")


# ==========================================
# CARD 4: TESTE DE SENSIBILIDADE (ROBUSTEZ)
# ==========================================
def make_card4():
    content = """
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>AUDITORIA E ROBUSTEZ</div>
    <h1>O Resultado se Sustenta sob Outras Hipóteses?</h1>
    <p class="subtitle">Testamos 18 combinações de premissas teóricas para garantir que o placar não depende de vieses</p>
  </div>

  <div class="main-content" style="display: flex; gap: 32px; width: 100%; align-items: stretch;">
    <!-- Stat Callout Box -->
    <div style="flex: 0 0 380px; background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between;">
      <div>
        <div style="font-size: 13px; font-weight: 700; color: #93c5fd; text-transform: uppercase; letter-spacing: 1px;">TESTE DE ESTRESSE</div>
        <div style="font-size: 72px; font-weight: 900; color: #ffffff; line-height: 1; margin: 12px 0 6px;">18 / 18</div>
        <div style="font-size: 16px; font-weight: 700; color: #38bdf8; margin-bottom: 12px;">Cenários com vitória de Lula</div>
        <p style="font-size: 13px; color: #cbd5e1; line-height: 1.45;">
          Mesmo alterando drasticamente o multiplicador de gastos públicos, o peso do ambiente de negócios e o repasse de corte de impostos aos preços, <strong>o plano de Lula venceu em 100% das 18 combinações</strong>. Flávio não venceu em nenhuma.
        </p>
      </div>

      <div style="background: rgba(0,0,0,0.3); border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #94a3b8;">
        Placar médio em todas as 18 variações: <strong style="color: #fff;">9 a 1</strong>.
      </div>
    </div>

    <!-- Explanations of Tested Assumptions -->
    <div style="flex: 1; display: flex; flex-direction: column; justify-content: space-around; gap: 10px;">
      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 14px 18px; border-radius: 10px;">
        <div style="font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">1. Multiplicador Fiscal do Gasto Público</div>
        <div style="font-size: 12.5px; color: #94a3b8; line-height: 1.35;">
          Testamos impacto no PIB de R$ 0,10, R$ 0,40 e R$ 0,70 por cada R$ 1 gasto/cortado. Mesmo com multiplicador quase nulo (favorecendo a tese de corte de gastos), o plano de Lula mantém a liderança ampla.
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 14px 18px; border-radius: 10px;">
        <div style="font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">2. Efeito do Ambiente de Negócios e Desregulamentação</div>
        <div style="font-size: 12.5px; color: #94a3b8; line-height: 1.35;">
          Testamos efeito fraco, médio e forte da redução de burocracia proposta por Flávio. O crescimento extra não compensa o impacto social do congelamento de benefícios.
        </div>
      </div>

      <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 14px 18px; border-radius: 10px;">
        <div style="font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">3. Repasse de Corte de Tributos aos Preços</div>
        <div style="font-size: 12.5px; color: #94a3b8; line-height: 1.35;">
          Testamos se o corte de impostos reduz a inflação ou fica retido na margem das empresas. Em ambos os cenários, a conclusão do estudo se manteve idêntica.
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="footer-left">
      Auditoria de sensibilidade realizada sem alteração das decisões originais dos agentes de IA
    </div>
    <div class="footer-right">
      github.com/CaiqueCoelho/brazil-ai-simulation
    </div>
  </div>
"""
    return wrap_card(content, "Card 4 - Sensibilidade")


def main():
    cards = {
        "card1_placar.html": make_card1(),
        "card2_tabela.html": make_card2(),
        "card3_tradeoffs.html": make_card3(),
        "card4_sensibilidade.html": make_card4(),
    }
    for fname, html in cards.items():
        (SOCIAL_DIR / fname).write_text(html, encoding="utf-8")
        print(f"Created {SOCIAL_DIR / fname}")

if __name__ == "__main__":
    main()
