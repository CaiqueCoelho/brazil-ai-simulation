"""Generates Instagram Story cards (1080x1920) for brazil-sim"""

import json
from pathlib import Path
from sim.article import BY_KEY, COLORS, SHORT, band, fmt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
RUN_DIR = OUT / "blind-v10"
STORIES_DIR = OUT / "stories"
STORIES_DIR.mkdir(parents=True, exist_ok=True)

results = json.loads((RUN_DIR / "results.json").read_text())
analysis = json.loads((RUN_DIR / "analysis.json").read_text())

def story_chart(results: dict, key: str) -> str:
    m = BY_KEY[key]
    W, H, L, R, T, B = 560, 200, 50, 115, 18, 26
    data = {s: band(results, s, key) for s in COLORS}
    values = [v for mean, lo_, hi_ in data.values() for v in lo_ + hi_]
    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.1 or abs(hi) * 0.05 or 1
    lo, hi = lo - pad, hi + pad
    n = len(data["lula"][0]) - 1
    x = lambda t: L + t / n * (W - L - R)
    y = lambda v: T + (1 - (v - lo) / (hi - lo)) * (H - T - B)
    dec_axis = max(0, m["dec"] - 1) if m["dec"] > 1 else m["dec"]
    parts = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{m["label"]}">' ]
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/>'
                     f'<text x="{L - 8}" y="{y(v) + 4:.1f}" class="ax" text-anchor="end">{fmt(v, dec_axis)}</text>')
    for t in range(0, n + 1, 4):
        parts.append(f'<text x="{x(t):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{2026 + t // 4}</text>')
    for s, (mean, lo_, hi_) in data.items():
        poly = [f"{x(t):.1f},{y(v):.1f}" for t, v in enumerate(hi_)] + [f"{x(t):.1f},{y(v):.1f}" for t, v in reversed(list(enumerate(lo_)))]
        parts.append(f'<polygon points="{" ".join(poly)}" fill="{COLORS[s]}" fill-opacity="0.14"/>')
    ends = []
    for s, (mean, _, _) in data.items():
        pts = " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in enumerate(mean))
        dash = ' stroke-dasharray="5 3"' if s == "baseline" else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{COLORS[s]}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        ends.append([y(mean[-1]), s, mean[-1]])
    ends.sort()
    for i in range(1, len(ends)):
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 16)
    for ey, s, v in ends:
        parts.append(f'<circle cx="{x(n):.1f}" cy="{y(data[s][0][-1]):.1f}" r="4.5" fill="{COLORS[s]}" stroke="#fff" stroke-width="2"/>'
                     f'<text x="{x(n) + 8:.1f}" y="{ey + 4:.1f}" class="lab"><tspan font-weight="800">{SHORT[s]}</tspan> {fmt(v, m["dec"])}</text>')
    parts.append("</svg>")
    return "".join(parts)

def wrap_story(badge_text: str, title: str, subtitle: str, content_html: str, footer_note: str = "") -> str:
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1920px;
    overflow: hidden;
    background: #090d16;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 160px 64px 200px 64px;
    position: relative;
  }}

  /* Ambient glowing gradients */
  .glow-1 {{
    position: absolute;
    top: -100px;
    right: -100px;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, rgba(0,0,0,0) 70%);
    border-radius: 50%;
    pointer-events: none;
  }}
  .glow-2 {{
    position: absolute;
    bottom: 100px;
    left: -100px;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, rgba(37, 99, 235, 0.10) 0%, rgba(0,0,0,0) 70%);
    border-radius: 50%;
    pointer-events: none;
  }}

  .header {{
    position: relative;
    z-index: 2;
    margin-bottom: 24px;
  }}
  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 16px;
  }}
  .badge-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #38bdf8;
  }}
  h1 {{
    font-size: 44px;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -0.8px;
    color: #ffffff;
    margin-bottom: 12px;
  }}
  .subtitle {{
    font-size: 22px;
    line-height: 1.4;
    color: #94a3b8;
    font-weight: 400;
  }}

  .main-content {{
    position: relative;
    z-index: 2;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 24px;
    margin: 16px 0;
  }}

  .card {{
    background: rgba(18, 24, 38, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 24px;
    padding: 28px 32px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
  }}

  .footer {{
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    font-size: 16px;
    color: #64748b;
  }}
  .footer-left {{
    font-weight: 500;
  }}
  .footer-right {{
    color: #38bdf8;
    font-weight: 700;
    letter-spacing: 0.5px;
  }}

  /* SVG Chart styles in Dark Mode */
  .chart {{
    width: 100%;
    height: auto;
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));
  }}
  .chart .ct {{ font-size: 18px; font-weight: 700; fill: #f8fafc; }}
  .chart .cu {{ font-weight: 400; fill: #94a3b8; font-size: 15px; }}
  .chart .ax {{ font-size: 14px; fill: #64748b; }}
  .chart .lab {{ font-size: 15px; fill: #f8fafc; font-weight: 700; }}
  .chart .grid {{ stroke: #334155; stroke-width: 1; stroke-dasharray: 2 4; }}
</style>
</head>
<body>
  <div class="glow-1"></div>
  <div class="glow-2"></div>

  <div class="header">
    <div class="badge"><div class="badge-dot"></div>{badge_text}</div>
    <h1>{title}</h1>
    <div class="subtitle">{subtitle}</div>
  </div>

  <div class="main-content">
    {content_html}
  </div>

  <div class="footer">
    <div class="footer-left">{footer_note or "Experimento com IA · Dados Oficiais (2018–2026)"}</div>
    <div class="footer-right">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>"""


# ==========================================================
# STORY 1: O Gancho e a Metodologia (Como foi feito)
# ==========================================================
def make_story_1():
    content = """
    <div class="card" style="border-left: 6px solid #38bdf8; background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));">
      <div style="font-size: 26px; font-weight: 800; color: #38bdf8; margin-bottom: 10px;">A PROVOCAÇÃO CIENTÍFICA</div>
      <div style="font-size: 22px; line-height: 1.5; color: #e2e8f0;">
        "Você já viu aqueles experimentos onde IAs simulam uma vila por anos e observam o que acontece? 
        <b style="color:#ffffff;">Levamos isso ao tamanho do Brasil:</b> simulamos 4 anos inteiros (2027 a 2030) testando à risca os planos de governo de <b style="color:#38bdf8;">Lula</b> e de <b style="color:#f97316;">Flávio Bolsonaro</b>."
      </div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div class="card" style="display: flex; align-items: flex-start; gap: 20px; padding: 22px 26px;">
        <div style="font-size: 32px; background: rgba(56, 189, 248, 0.15); border-radius: 16px; padding: 12px 16px;">📄</div>
        <div>
          <div style="font-size: 20px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">Planos Oficiais no TSE</div>
          <div style="font-size: 17px; color: #94a3b8; line-height: 1.4;">Propostas reais registradas e declaradas pelas equipes econômicas de ambos.</div>
        </div>
      </div>

      <div class="card" style="display: flex; align-items: flex-start; gap: 20px; padding: 22px 26px;">
        <div style="font-size: 32px; background: rgba(56, 189, 248, 0.15); border-radius: 16px; padding: 12px 16px;">🤖</div>
        <div>
          <div style="font-size: 20px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">Agentes de IA Institucionais</div>
          <div style="font-size: 17px; color: #94a3b8; line-height: 1.4;">DeepSeek dá voz ao Congresso, STF e Cidadãos sob <b style="color:#f8fafc;">100% de anonimato dos candidatos</b>.</div>
        </div>
      </div>

      <div class="card" style="display: flex; align-items: flex-start; gap: 20px; padding: 22px 26px;">
        <div style="font-size: 32px; background: rgba(56, 189, 248, 0.15); border-radius: 16px; padding: 12px 16px;">📐</div>
        <div>
          <div style="font-size: 20px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">A IA NUNCA Inventa Números</div>
          <div style="font-size: 17px; color: #94a3b8; line-height: 1.4;">O PIB, inflação e desemprego são calculados por motor matemático com <b style="color:#f8fafc;">34 trimestres de dados reais (BC, IBGE e Ipea)</b>.</div>
        </div>
      </div>

      <div class="card" style="display: flex; align-items: flex-start; gap: 20px; padding: 22px 26px;">
        <div style="font-size: 32px; background: rgba(56, 189, 248, 0.15); border-radius: 16px; padding: 12px 16px;">⚖️</div>
        <div>
          <div style="font-size: 20px; font-weight: 800; color: #ffffff; margin-bottom: 4px;">Regras Idênticas & Mesmos Choques</div>
          <div style="font-size: 17px; color: #94a3b8; line-height: 1.4;">Banco Central (Regra de Taylor), juros dos EUA e secas climáticas idênticos para os dois.</div>
        </div>
      </div>
    </div>

    <div class="card" style="background: linear-gradient(90deg, #1e3a8a 0%, #1e293b 100%); border-color: #3b82f6; text-align: center; padding: 24px;">
      <div style="font-size: 16px; font-weight: 700; letter-spacing: 1.5px; color: #93c5fd; text-transform: uppercase;">VEREDITO CONSOLIDADO DA SIMULAÇÃO</div>
      <div style="font-size: 40px; font-weight: 900; color: #ffffff; margin-top: 6px;">LULA 9 × 1 FLÁVIO BOLSONARO</div>
      <div style="font-size: 17px; color: #bfdbfe; margin-top: 4px;">(Com 1 empate técnico na Economia Geral)</div>
    </div>
    """
    return wrap_story(
        badge_text="EXPERIMENTO COM IA · BRASIL 2027–2030",
        title="Simulamos 4 Anos de Governo Lula vs Flávio",
        subtitle="O que acontece quando colocamos as propostas reais dos dois candidatos num país virtual movido a dados oficiais?",
        content_html=content,
        footer_note="Deslize para ver os gráficos e dados ➔"
    )


# ==========================================================
# STORY 2: O Placar Geral dos 11 Indicadores
# ==========================================================
def make_story_2():
    content = """
    <!-- Top Big Scorecard -->
    <div class="card" style="display: flex; justify-content: space-between; align-items: center; padding: 24px 36px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95)); border: 1px solid rgba(255,255,255,0.18);">
      <div style="text-align: left;">
        <div style="font-size: 18px; font-weight: 800; color: #38bdf8; letter-spacing: 1.5px;">LULA</div>
        <div style="font-size: 68px; font-weight: 900; color: #ffffff; line-height: 1;">9</div>
        <div style="font-size: 16px; color: #94a3b8; font-weight: 600;">vitórias</div>
      </div>
      <div style="text-align: center;">
        <div style="font-size: 24px; font-weight: 900; color: #475569;">VS</div>
        <div style="font-size: 15px; color: #94a3b8; margin-top: 4px; background: rgba(255,255,255,0.06); padding: 4px 12px; border-radius: 999px;">1 Empate</div>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 18px; font-weight: 800; color: #f97316; letter-spacing: 1.5px;">FLÁVIO</div>
        <div style="font-size: 68px; font-weight: 900; color: #ffffff; line-height: 1;">1</div>
        <div style="font-size: 16px; color: #94a3b8; font-weight: 600;">vitória</div>
      </div>
    </div>

    <!-- Indicator Breakdown Table -->
    <div class="card" style="padding: 20px 24px;">
      <div style="font-size: 17px; font-weight: 800; color: #cbd5e1; margin-bottom: 14px; text-transform: uppercase; letter-spacing: 1px;">
        Comparativo Item a Item (Média 2027–2030)
      </div>

      <div style="display: flex; flex-direction: column; gap: 9px; font-size: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Desemprego (2030)</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 5,5% vs 5,9% 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Pobreza</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 17,4% vs 23,8% 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Fome (Subalimentação)</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 3,1% vs 4,2% 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Desigualdade (Índice Gini)</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 0,489 vs 0,518 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Saúde (Mortalidade Infantil)</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 11,0 vs 12,0 por mil 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Segurança (Homicídios)</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 16,9 vs 18,4 por 100k 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Desmatamento Amazônia</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 3.940 vs 5.367 km² 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(56, 189, 248, 0.08); border-radius: 10px; border-left: 4px solid #38bdf8;">
          <span style="font-weight: 600;">Aprovação dos Cidadãos</span>
          <span style="font-weight: 800; color: #38bdf8;">Lula 45% vs 43% 🏆</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(148, 163, 184, 0.08); border-radius: 10px; border-left: 4px solid #94a3b8;">
          <span style="font-weight: 600;">Economia Geral (PIB anual)</span>
          <span style="font-weight: 800; color: #94a3b8;">Lula 1,8% vs 1,7% (Empate) 🤝</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(249, 115, 22, 0.12); border-radius: 10px; border-left: 4px solid #f97316;">
          <span style="font-weight: 700; color: #ffedd5;">Contas Públicas (Dívida)</span>
          <span style="font-weight: 900; color: #f97316;">Flávio 85,2% vs 88,4% 🎯</span>
        </div>
      </div>
    </div>

    <!-- Explanatory Insight Box -->
    <div class="card" style="border-left: 6px solid #f97316; background: rgba(30, 20, 15, 0.7);">
      <div style="font-size: 18px; font-weight: 800; color: #f97316; margin-bottom: 6px;">A ÚNICA VITÓRIA DE FLÁVIO (1 DE 11)</div>
      <div style="font-size: 17px; line-height: 1.45; color: #fed7aa;">
        Flávio vence exclusivamente nas contas públicas com um arrocho de R$ 190 bi (~1,5% do PIB). Porém, essa contenção exige desindexar o BPC, aposentadorias e os pisos da saúde e educação, cobrando um preço severo em pobreza e mortalidade infantil.
      </div>
    </div>
    """
    return wrap_story(
        badge_text="SCORECARD COMPLETO · 11 INDICADORES",
        title="O Placar Final: 9 a 1 a Favor de Lula",
        subtitle="Lula vence em 9 itens, Flávio vence em 1 (contas públicas) e há 1 empate técnico.",
        content_html=content,
        footer_note="Veja os gráficos reais na próxima tela ➔"
    )


# ==========================================================
# STORY 3: Dados Impactantes — Pobreza, Fome & Desigualdade
# ==========================================================
def make_story_3():
    chart_poverty = story_chart(results, "poverty_rate")
    chart_food = story_chart(results, "food_insecurity")
    
    content = f"""
    <!-- Metrics Callout Row -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
      <div class="card" style="border-top: 4px solid #38bdf8; text-align: center; padding: 20px 16px;">
        <div style="font-size: 15px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Taxa de Pobreza (2030)</div>
        <div style="font-size: 38px; font-weight: 900; color: #38bdf8; margin: 4px 0;">17,4%</div>
        <div style="font-size: 14px; color: #e2e8f0;">Lula (vs <b style="color:#f97316;">23,8%</b> Flávio)</div>
      </div>

      <div class="card" style="border-top: 4px solid #38bdf8; text-align: center; padding: 20px 16px;">
        <div style="font-size: 15px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Fome / Insegurança</div>
        <div style="font-size: 38px; font-weight: 900; color: #38bdf8; margin: 4px 0;">3,1%</div>
        <div style="font-size: 14px; color: #e2e8f0;">Lula (vs <b style="color:#f97316;">4,2%</b> Flávio)</div>
      </div>
    </div>

    <!-- Chart 1: Pobreza -->
    <div class="card" style="padding: 20px 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="font-size: 18px; font-weight: 800; color: #ffffff;">Trajetória da Pobreza (2026–2030)</div>
        <div style="font-size: 13px; font-weight: 700; color: #38bdf8; background: rgba(56,189,248,0.15); padding: 3px 10px; border-radius: 999px;">LULA VENCE</div>
      </div>
      <div style="width: 100%;">{chart_poverty}</div>
      <div style="font-size: 14px; color: #94a3b8; margin-top: 6px;">Linha azul: Lula · Linha laranja: Flávio · Linha tracejada: Cenário Base</div>
    </div>

    <!-- Chart 2: Fome -->
    <div class="card" style="padding: 20px 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="font-size: 18px; font-weight: 800; color: #ffffff;">Insegurança Alimentar Grave (Fome)</div>
        <div style="font-size: 13px; font-weight: 700; color: #38bdf8; background: rgba(56,189,248,0.15); padding: 3px 10px; border-radius: 999px;">LULA VENCE</div>
      </div>
      <div style="width: 100%;">{chart_food}</div>
    </div>

    <!-- Mechanism Explanation -->
    <div class="card" style="border-left: 6px solid #38bdf8; background: rgba(15, 23, 42, 0.9); padding: 20px 24px;">
      <div style="font-size: 17px; font-weight: 800; color: #38bdf8; margin-bottom: 4px;">O MECANISMO REAL POR TRÁS DOS NÚMEROS</div>
      <div style="font-size: 16px; line-height: 1.45; color: #cbd5e1;">
        No plano de Flávio, desindexar aposentadorias e o BPC da valorização do salário mínimo drena renda das famílias mais pobres da base da pirâmide. Com Lula, a proteção social e o aumento real do mínimo derrubam o Gini para <b>0,489</b> (contra <b>0,518</b> de Flávio).
      </div>
    </div>
    """
    return wrap_story(
        badge_text="ABISMO SOCIAL · 3 VITÓRIAS DE LULA",
        title="Pobreza, Fome e Desigualdade",
        subtitle="Por que as políticas sociais de Lula superam o plano de Flávio nas 5 rodadas de simulação?",
        content_html=content,
        footer_note="Mais dados de Emprego, Saúde e Meio Ambiente ➔"
    )


# ==========================================================
# STORY 4: Dados Impactantes — Trabalho, Saúde & Amazônia
# ==========================================================
def make_story_4():
    chart_unemp = story_chart(results, "unemployment")
    chart_deforest = story_chart(results, "deforestation_km2")

    content = f"""
    <!-- 3 Pillars Row -->
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <!-- Emprego -->
      <div class="card" style="border-left: 6px solid #38bdf8; padding: 20px 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div style="font-size: 20px; font-weight: 800; color: #ffffff;">💼 Emprego & Desemprego (2030)</div>
          <div style="font-size: 14px; font-weight: 800; color: #38bdf8;">LULA 5,5% vs 5,9%</div>
        </div>
        <div style="font-size: 16px; color: #94a3b8; line-height: 1.45;">
          Estudos do Ipea apontam que o <b>fim da escala 6x1</b> (Lula) eleva a produtividade horária e induz novas contratações sem custo agregado relevante. Já a <b>desoneração da folha</b> (Flávio) vira margem empresarial sem gerar saldo líquido de vagas.
        </div>
      </div>

      <!-- Saúde -->
      <div class="card" style="border-left: 6px solid #38bdf8; padding: 20px 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div style="font-size: 20px; font-weight: 800; color: #ffffff;">🏥 Mortalidade Infantil (por mil)</div>
          <div style="font-size: 14px; font-weight: 800; color: #38bdf8;">LULA 11,02 vs 12,01</div>
        </div>
        <div style="font-size: 16px; color: #94a3b8; line-height: 1.45;">
          Flávio termina pior inclusive que o cenário base (11,70). A literatura médica (<i>The Lancet</i>) comprova que o piso constitucional do SUS e saneamento salvam vidas infantis; o congelamento orçamentário eleva óbitos evitáveis.
        </div>
      </div>

      <!-- Meio Ambiente -->
      <div class="card" style="border-left: 6px solid #38bdf8; padding: 20px 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div style="font-size: 20px; font-weight: 800; color: #ffffff;">🌳 Desmatamento na Amazônia</div>
          <div style="font-size: 14px; font-weight: 800; color: #38bdf8;">LULA 3.940 vs 5.367 km²</div>
        </div>
        <div style="font-size: 16px; color: #94a3b8; line-height: 1.45;">
          A fiscalização presencial do Ibama com multas e apreensão (PPCDAm) contém o crime ambiental. A proposta de monitoramento por satélites sem autos punitivos de Flávio deixa a fronteira agrícola ilegal avançar.
        </div>
      </div>
    </div>

    <!-- Chart: Desmatamento -->
    <div class="card" style="padding: 20px 24px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <div style="font-size: 18px; font-weight: 800; color: #ffffff;">Desmatamento Anual na Amazônia (km²)</div>
        <div style="font-size: 13px; font-weight: 700; color: #38bdf8; background: rgba(56,189,248,0.15); padding: 3px 10px; border-radius: 999px;">-26,5% COM LULA</div>
      </div>
      <div style="width: 100%;">{chart_deforest}</div>
    </div>
    """
    return wrap_story(
        badge_text="ECONOMIA REAL · VIDAS · FLORESTA",
        title="Trabalho, Saúde e Meio Ambiente",
        subtitle="Evidências empíricas mostram os efeitos reais das políticas públicas aplicadas aos dois modelos.",
        content_html=content,
        footer_note="Veja o que disseram os Cidadãos Virtuais ➔"
    )


# ==========================================================
# STORY 5: Voz dos Cidadãos & Call To Action (Link)
# ==========================================================
def make_story_5():
    content = """
    <!-- Approval Bar -->
    <div class="card" style="padding: 24px 30px; background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));">
      <div style="font-size: 17px; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 12px;">Aprovação dos 200 Cidadãos Virtuais</div>
      <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
        <div style="font-size: 32px; font-weight: 900; color: #38bdf8;">Lula 45,0%</div>
        <div style="font-size: 16px; color: #64748b;">vs</div>
        <div style="font-size: 32px; font-weight: 900; color: #f97316;">Flávio 43,0%</div>
      </div>
      <div style="font-size: 15px; color: #94a3b8;">Personagens com perfis fiéis à demografia, renda e regiões do Censo IBGE.</div>
    </div>

    <!-- Citizen Quotes -->
    <div style="display: flex; flex-direction: column; gap: 16px;">
      <div class="card" style="border-left: 6px solid #38bdf8; padding: 22px 26px; background: rgba(15, 23, 42, 0.9);">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
          <div style="font-size: 24px;">👩🏾‍🦱</div>
          <div>
            <div style="font-size: 18px; font-weight: 800; color: #ffffff;">Dona Maria, 52 anos (Diarista, Bahia)</div>
            <div style="font-size: 14px; color: #38bdf8; font-weight: 600;">No Brasil de Lula:</div>
          </div>
        </div>
        <div style="font-size: 17px; line-height: 1.45; color: #e2e8f0; font-style: italic;">
          "A vida melhorou no emprego e no atendimento do postinho de saúde, embora o custo de vida e as secas ainda apertem bastante o nosso orçamento."
        </div>
      </div>

      <div class="card" style="border-left: 6px solid #f97316; padding: 22px 26px; background: rgba(30, 20, 15, 0.8);">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
          <div style="font-size: 24px;">👨🏻‍💼</div>
          <div>
            <div style="font-size: 18px; font-weight: 800; color: #ffffff;">Carlos, 41 anos (Comerciante, Goiás)</div>
            <div style="font-size: 14px; color: #f97316; font-weight: 600;">No Brasil de Flávio:</div>
          </div>
        </div>
        <div style="font-size: 17px; line-height: 1.45; color: #fed7aa; font-style: italic;">
          "O governo fala em corte de gastos e austeridade todo dia no jornal, mas na feira nada baixou de preço e a fila do hospital público só aumentou."
        </div>
      </div>
    </div>

    <!-- CTA Box with Sticker Target -->
    <div class="card" style="background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%); border: 2px solid #38bdf8; text-align: center; padding: 32px 24px; box-shadow: 0 15px 35px rgba(2, 132, 199, 0.35);">
      <div style="font-size: 15px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; color: #bae6fd; margin-bottom: 8px;">
        ACESSE A PESQUISA COMPLETA
      </div>
      <div style="font-size: 32px; font-weight: 900; color: #ffffff; margin-bottom: 12px;">
        Artigo Interativo, PDF e Código
      </div>
      <div style="font-size: 18px; color: #e0f2fe; line-height: 1.4; margin-bottom: 20px;">
        Confira todas as 5 rodadas da simulação, gráficos dinâmicos e equações abertas.
      </div>

      <!-- Sticker placeholder area -->
      <div style="display: inline-flex; align-items: center; justify-content: center; gap: 10px; background: #ffffff; color: #0f172a; font-size: 20px; font-weight: 900; padding: 14px 28px; border-radius: 999px; box-shadow: 0 8px 20px rgba(0,0,0,0.3);">
        <span>🔗</span>
        <span>TOQUE NO LINK DO STORY</span>
      </div>
    </div>
    """
    return wrap_story(
        badge_text="VOZ DOS CIDADÃOS & RELATÓRIO COMPLETO",
        title="O Que a Simulação nos Ensina?",
        subtitle="A ciência de dados e a IA não substituem o debate, mas expõem com clareza os trade-offs reais de cada projeto.",
        content_html=content,
        footer_note="Toque no link ou acesse github.com/CaiqueCoelho/brazil-ai-simulation"
    )


# Generate files
(STORIES_DIR / "story1_metodologia.html").write_text(make_story_1())
(STORIES_DIR / "story2_placar.html").write_text(make_story_2())
(STORIES_DIR / "story3_social.html").write_text(make_story_3())
(STORIES_DIR / "story4_indicadores.html").write_text(make_story_4())
(STORIES_DIR / "story5_cidadaos_cta.html").write_text(make_story_5())

print("Generated 5 story HTML files in out/stories/")
