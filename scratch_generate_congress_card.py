import json
import subprocess
from pathlib import Path

ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

html = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1200px;
    height: 675px;
    overflow: hidden;
    background: #0b0f17;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 30px 42px;
    position: relative;
  }
  body::before {
    content: "";
    position: absolute;
    top: -120px; left: 50%;
    transform: translateX(-50%);
    width: 700px; height: 350px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .header { position: relative; z-index: 2; margin-bottom: 8px; }
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 3px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #38bdf8; margin-bottom: 5px;
  }
  .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #38bdf8; }
  h1 { font-size: 25px; font-weight: 800; color: #ffffff; letter-spacing: -0.4px; margin-bottom: 2px; }
  .subtitle { font-size: 12.5px; color: #94a3b8; }

  /* Main grid */
  .content-grid {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 18px;
    flex: 1;
    position: relative;
    z-index: 2;
    margin-bottom: 8px;
  }

  .panel {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .panel-title {
    font-size: 13px;
    font-weight: 700;
    color: #f8fafc;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 5px;
    margin-bottom: 8px;
  }
  .panel-title span { font-size: 11px; color: #64748b; font-weight: 500; }

  /* Visual Hemicycle Bar */
  .hemicycle-box {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 10px;
  }
  .seats-bar {
    display: flex;
    width: 100%;
    height: 38px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    border: 1px solid rgba(255,255,255,0.1);
  }
  .seat-seg {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    color: #fff;
    text-shadow: 0 1px 2px rgba(0,0,0,0.6);
    position: relative;
  }
  .seg-left { width: 24.2%; background: linear-gradient(135deg, #dc2626, #ef4444); }
  .seg-centrao { width: 50.1%; background: linear-gradient(135deg, #0284c7, #38bdf8); color: #082f49; text-shadow: none; font-weight: 900; }
  .seg-right { width: 25.7%; background: linear-gradient(135deg, #ea580c, #f97316); }

  /* Blocs cards */
  .bloc-cards {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin-bottom: 10px;
  }
  .bloc-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 8px 10px;
    border-top: 3px solid transparent;
  }
  .card-left { border-top-color: #ef4444; }
  .card-centrao { border-top-color: #38bdf8; }
  .card-right { border-top-color: #f97316; }

  .bloc-name { font-size: 11px; font-weight: 700; color: #f8fafc; margin-bottom: 2px; }
  .bloc-pct { font-size: 16px; font-weight: 800; }
  .color-left { color: #ef4444; }
  .color-centrao { color: #38bdf8; }
  .color-right { color: #f97316; }
  .bloc-seats { font-size: 10px; color: #94a3b8; margin-bottom: 3px; }
  .bloc-parties { font-size: 9.5px; color: #cbd5e1; line-height: 1.25; }

  /* Thresholds explanation */
  .thresholds-box {
    display: flex;
    flex-direction: column;
    gap: 6px;
    background: rgba(0,0,0,0.3);
    border-radius: 8px;
    padding: 8px 12px;
  }
  .thresh-line {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #e2e8f0;
  }
  .thresh-tag {
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 9.5px;
  }
  .tag-law { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
  .tag-pec { background: rgba(249, 115, 22, 0.2); color: #fb923c; }

  /* Right Column: Dynamics in Simulation */
  .dyn-section { display: flex; flex-direction: column; gap: 8px; flex: 1; }
  .dyn-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    padding: 10px 12px;
    border-left: 3px solid transparent;
  }
  .dyn-card.lula { border-left-color: #3b82f6; }
  .dyn-card.flavio { border-left-color: #f97316; }
  .dyn-card.centrao { border-left-color: #38bdf8; }

  .dyn-title { font-size: 11.5px; font-weight: 700; color: #f8fafc; margin-bottom: 3px; }
  .dyn-desc { font-size: 10.5px; color: #94a3b8; line-height: 1.35; }
  .dyn-desc strong { color: #f1f5f9; }

  .footer {
    position: relative;
    z-index: 2;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 6px;
    display: flex;
    justify-content: space-between;
    font-size: 10.5px;
    color: #64748b;
  }
  .footer-link { color: #38bdf8; font-weight: 600; }
</style>
</head>
<body>
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>Câmara dos Deputados · Eleições 2026</div>
    <h1>Composição Política e Correlação de Forças no Congresso</h1>
    <p class="subtitle">As bancadas reais que votaram Projetos de Lei e Emendas Constitucionais (PECs) de 2027 a 2030</p>
  </div>

  <div class="content-grid">
    <!-- Left: Composition & Quorums -->
    <div class="panel">
      <div class="panel-title">
        Distribuição das 513 Cadeiras da Câmara
        <span>Câmara Eleita em Out/2026</span>
      </div>

      <div class="hemicycle-box">
        <div class="seats-bar">
          <div class="seat-seg seg-left">24%</div>
          <div class="seat-seg seg-centrao">50% · CENTRÃO</div>
          <div class="seat-seg seg-right">26%</div>
        </div>
      </div>

      <div class="bloc-cards">
        <div class="bloc-card card-left">
          <div class="bloc-name">Esquerda</div>
          <div class="bloc-pct color-left">24,2%</div>
          <div class="bloc-seats">124 deputados</div>
          <div class="bloc-parties">PT, PSB, PDT, PSOL, PCdoB, PV, Rede</div>
        </div>
        <div class="bloc-card card-centrao">
          <div class="bloc-name">Centrão (Pêndulo)</div>
          <div class="bloc-pct color-centrao">50,1%</div>
          <div class="bloc-seats">257 deputados</div>
          <div class="bloc-parties">PP, União Brasil, PSD, MDB, Rep., Podemos</div>
        </div>
        <div class="bloc-card card-right">
          <div class="bloc-name">Direita</div>
          <div class="bloc-pct color-right">25,7%</div>
          <div class="bloc-seats">132 deputados</div>
          <div class="bloc-parties">PL, Novo e aliados conservadores</div>
        </div>
      </div>

      <div class="panel-title" style="margin-top: 4px;">
        Regras de Votação e Quóruns Constitucionais
      </div>
      <div class="thresholds-box">
        <div class="thresh-line">
          <span><strong>Projeto de Lei Ordinária:</strong> Maioria Simples (&gt; 50% dos presentes)</span>
          <span class="thresh-tag tag-law">&gt; 256 votos</span>
        </div>
        <div class="thresh-line">
          <span><strong>Emenda Constitucional (PEC):</strong> Quórum Qualificado de 3/5 em 2 turnos</span>
          <span class="thresh-tag tag-pec">&ge; 308 votos (60%)</span>
        </div>
      </div>
      <div style="font-size: 10px; color: #94a3b8; margin-top: 6px; line-height: 1.3;">
        * O Centrão é o fiel da balança: nenhuma PEC aprova sem ele. Com a Esquerda soma <strong>74,3%</strong>; com a Direita soma <strong>75,8%</strong>.
      </div>
    </div>

    <!-- Right: Legislative Dynamics -->
    <div class="panel">
      <div class="panel-title">
        Como a Correlação de Forças Operou na Simulação
        <span>Comportamento dos Agentes</span>
      </div>

      <div class="dyn-section">
        <div class="dyn-card centrao">
          <div class="dyn-title" style="color: #38bdf8;">O Poder do Centrão: Exigência de Emendas e Desidratação</div>
          <div class="dyn-desc">
            Detentor de 50,1% das cadeiras, o Centrão condicionou o apoio à liberação de <strong>0,10% a 0,20% do PIB em emendas parlamentares</strong>. Raramente rejeitou matérias de cara: preferiu <strong>emendar e desidratar</strong> as propostas mais radicais de ambos os governos.
          </div>
        </div>

        <div class="dyn-card lula">
          <div class="dyn-title" style="color: #60a5fa;">No Governo Lula: Fim da 6x1 e Fundeb Aprovados com Mudanças</div>
          <div class="dyn-desc">
            A aliança Esquerda + Centrão aprovou a PEC do Fundeb integral e o Ministério da Segurança Pública. A <strong>PEC do fim da escala 6x1</strong> passou de forma emendada pelo Centrão, reduzindo a resistência empresarial e atenuando o impacto inicial de custos.
          </div>
        </div>

        <div class="dyn-card flavio">
          <div class="dyn-title" style="color: #fb923c;">No Governo Flávio: Corte de Gastos Passou, Ofensiva ao STF Barrou</div>
          <div class="dyn-desc">
            A aliança Direita + Centrão aprovou o corte de gastos de 1,5% do PIB (PEC) e incentivos ao agro. Porém, a <strong>PEC para limitar decisões do STF</strong> foi rejeitada pelo Centrão ou suspensa pela própria Corte por violação da separação dos Poderes.
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Votações simuladas por agentes de IA com pesos proporcionais das bancadas · Modelo determinístico de contagem de votos</div>
    <div class="footer-link">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>
"""

card_html = ARTIFACT_DIR / "congresso_composicao_2026.html"
card_png = ARTIFACT_DIR / "congresso_composicao_2026.png"

card_html.write_text(html, encoding="utf-8")
print(f"Wrote {card_html}")

cmd = [
    CHROME,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1200,675",
    f"--screenshot={card_png}",
    card_html.as_uri()
]

subprocess.run(cmd, check=True)
print(f"Generated {card_png}: exists={card_png.exists()}, size={card_png.stat().st_size}")
