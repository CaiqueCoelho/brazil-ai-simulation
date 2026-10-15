"""Generates thread cards with actual simulation line charts from sim/article.py"""

import json
from pathlib import Path
from sim.article import chart

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RUN_DIR = OUT / "blind-v10"
SOCIAL_DIR = OUT / "social"
SOCIAL_DIR.mkdir(parents=True, exist_ok=True)

results = json.loads((RUN_DIR / "results.json").read_text())

def wrap_thread_card(title: str, subtitle: str, badge: str, charts_html: str, insight: str) -> str:
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
    padding: 34px 44px;
    position: relative;
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
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 8px;
  }}
  .badge-dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #38bdf8;
  }}
  h1 {{
    font-size: 27px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 4px;
    letter-spacing: -0.4px;
  }}
  .subtitle {{
    font-size: 13.5px;
    color: #94a3b8;
  }}
  .main-content {{
    position: relative;
    z-index: 2;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 12px;
    margin: 10px 0;
  }}
  .charts-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 20px;
  }}
  .chart {{
    width: 100%;
    height: auto;
  }}
  .chart .ct {{ font-size: 12px; font-weight: 700; fill: #ffffff; }}
  .chart .cu {{ font-weight: 400; fill: #94a3b8; }}
  .chart .ax {{ font-size: 9.5px; fill: #94a3b8; }}
  .chart .lab {{ font-size: 10px; fill: #ffffff; font-weight: 600; }}
  .chart .grid {{ stroke: rgba(255, 255, 255, 0.08); stroke-width: 1; }}
  .insight-box {{
    background: rgba(56, 189, 248, 0.06);
    border-left: 3px solid #38bdf8;
    padding: 8px 14px;
    border-radius: 0 8px 8px 0;
    font-size: 12.5px;
    color: #e2e8f0;
    line-height: 1.4;
  }}
  .footer {{
    position: relative;
    z-index: 2;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 10px;
    display: flex;
    justify-content: space-between;
    font-size: 11.5px;
    color: #64748b;
  }}
</style>
</head>
<body>
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>{badge}</div>
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
  </div>

  <div class="main-content">
    <div class="charts-row">
      {charts_html}
    </div>
    <div class="insight-box">
      {insight}
    </div>
  </div>

  <div class="footer">
    <div>Azul: Lula · Laranja: Flávio Bolsonaro · Tracejado verde: Cenário Base sem novas políticas</div>
    <div style="color: #38bdf8; font-weight: 600;">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>"""

def make_thread_card1():
    # Emprego & Economia
    c1 = chart(results, "gdp_growth")
    c2 = chart(results, "unemployment")
    insight = "<strong>Mecanismo Econômico:</strong> O plano de Lula termina 2030 com desemprego de <strong>5,8%</strong> (vs 8,2% de Flávio). O corte de 1,5% do PIB de Flávio freia o PIB de curto prazo (estudo FMI com 17 países), enquanto o fim da escala 6x1 (Lula) tem custo empresarial desprezível (&lt;1% segundo Ipea) e não eleva desemprego."
    return wrap_thread_card(
        "Emprego e Atividade Econômica (2027–2030)",
        "Trajetória trimestral média com bandas de confiança das 5 simulações",
        "DETALHAMENTO · EMPREGO E PIB",
        c1 + c2,
        insight
    )

def make_thread_card2():
    # Fiscal e Dívida
    c1 = chart(results, "debt_gdp")
    c2 = chart(results, "primary_balance")
    insight = """
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
        <span style="font-weight:800; color:#f97316; font-size:12.5px; text-transform:uppercase; letter-spacing:0.5px;">
          🎯 O Único Destaque de Flávio Bolsonaro (1 de 11 Indicadores)
        </span>
        <span style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.3); color:#38bdf8; font-weight:800; padding:2px 10px; border-radius:999px; font-size:11px;">
          PLACAR GERAL: LULA 9 × 1 FLÁVIO (1 EMPATE)
        </span>
      </div>
      <div>
        O corte de R$ 190 bi (1,5% do PIB) zera o déficit primário (+0,1% PIB) e reduz a dívida para <strong>85,2% do PIB</strong> (vs 88,4% com Lula e 89,7% no cenário base). Contudo, este foi o <strong>único indicador onde Flávio superou Lula</strong> em toda a simulação: todas as áreas de emprego, renda, pobreza, saúde e meio ambiente tiveram vitória de Lula.
      </div>
    """
    return wrap_thread_card(
        "A Única Vitória de Flávio (1 de 11): Contas Públicas e Dívida",
        "No placar geral onde Lula vence por 9x1, o plano de Flávio só supera o petista na trajetória fiscal e da dívida",
        "PLACAR GERAL: LULA 9 × 1 FLÁVIO · ÚNICA VITÓRIA DE FLÁVIO",
        c1 + c2,
        insight
    )


def make_thread_card3():
    # Social: Pobreza e Fome
    c1 = chart(results, "poverty_rate")
    c2 = chart(results, "food_insecurity")
    insight = "<strong>Mecanismo Social:</strong> A pobreza cai para <strong>17,4%</strong> com Lula e sobe para <strong>23,8%</strong> com Flávio. Embora Flávio mantenha o Bolsa Família, congelar o ganho real do salário mínimo, aposentadorias e BPC prejudica diretamente as famílias mais vulneráveis."
    return wrap_thread_card(
        "Impacto Social: Pobreza e Insegurança Alimentar",
        "Evolução da taxa de pobreza e da fome nos 4 anos simulados",
        "DETALHAMENTO · SOCIAL",
        c1 + c2,
        insight
    )

def make_thread_card4():
    # Segurança e Meio Ambiente
    c1 = chart(results, "homicides_per_100k")
    c2 = chart(results, "deforestation_km2")
    insight = "<strong>Mecanismo de Políticas Públicas:</strong> Lula vence em segurança (16,8 homicídios/100k) com câmeras e asfixia financeira de facções (as penas mais duras de Flávio caíram no STF). No meio ambiente, multas e fiscalização de Lula reduzem desmatamento para 4.116 km², enquanto satélites sem multas de Flávio não contiveram a devastação (7.424 km²)."
    return wrap_thread_card(
        "Segurança Pública e Desmatamento na Amazônia",
        "Efeito de políticas públicas baseadas em evidências empíricas vs medidas punitivistas",
        "DETALHAMENTO · POLÍTICAS PÚBLICAS",
        c1 + c2,
        insight
    )

def main():
    cards = {
        "thread_card1_economia.html": make_thread_card1(),
        "thread_card2_fiscal.html": make_thread_card2(),
        "thread_card3_social.html": make_thread_card3(),
        "thread_card4_seguranca_ambiente.html": make_thread_card4(),
    }
    for fname, html in cards.items():
        (SOCIAL_DIR / fname).write_text(html, encoding="utf-8")
        print(f"Generated {fname}")

if __name__ == "__main__":
    main()
