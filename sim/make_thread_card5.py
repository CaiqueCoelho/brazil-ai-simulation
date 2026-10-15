"""Generates thread card 5 with approval, democracy risk and virtual citizen quotes"""

import json
from pathlib import Path
from sim.article import chart

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RUN_DIR = OUT / "blind-v10"
SOCIAL_DIR = OUT / "social"

results = json.loads((RUN_DIR / "results.json").read_text())

c1 = chart(results, "approval")
c2 = chart(results, "democracy_risk")

html = f"""<!doctype html>
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
    padding: 14px 20px;
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
  
  .quotes-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }}
  .quote-card {{
    background: rgba(255, 255, 255, 0.04);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 12px;
    line-height: 1.4;
  }}
  .quote-card.lula {{
    border-left: 3px solid #3b82f6;
  }}
  .quote-card.flavio {{
    border-left: 3px solid #f97316;
  }}
  .quote-title {{
    font-weight: 800;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.6px;
    margin-bottom: 3px;
  }}
  .quote-text {{
    color: #e2e8f0;
    font-style: italic;
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
    <div class="badge"><span class="badge-dot"></span>A VOZ DOS 200 CIDADÃOS VIRTUAIS · IA</div>
    <h1>Popularidade Popular e Estabilidade Democrática</h1>
    <p class="subtitle">Como personagens de IA representando a demografia do IBGE reagiram a cada governo simulado</p>
  </div>

  <div class="main-content">
    <div class="charts-row">
      {c1 + c2}
    </div>
    
    <div class="quotes-row">
      <div class="quote-card lula">
        <div class="quote-title" style="color: #60a5fa;">Cidadão Virtual no Brasil de Lula (Aprovação: 44%)</div>
        <div class="quote-text">"Vendo pouco, tudo caro. A seca secou meu bolso, mas ao menos a violência deu uma trégua."</div>
      </div>
      <div class="quote-card flavio">
        <div class="quote-title" style="color: #fb923c;">Cidadão Virtual no Brasil de Flávio (Aprovação: 31%)</div>
        <div class="quote-text">"Vendo pouco, o povo reclama do preço e da conta de luz, mas o governo só fala em dívida."</div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Nenhuma pessoa real foi entrevistada · Cidadãos virtuais gerados por IA refletindo a pirâmide do IBGE</div>
    <div style="color: #38bdf8; font-weight: 600;">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>"""

(SOCIAL_DIR / "thread_card5_cidadaos.html").write_text(html, encoding="utf-8")
print("Generated thread_card5_cidadaos.html")
