import json
import subprocess
from pathlib import Path

ROOT = Path("/Users/caiquecoelho/Documents/Projects/directory/brazil-sim")
ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# CARD 1: FALAS E FEEDBACKS REAIS DOS CIDADÃOS
html1 = """<!doctype html>
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
    padding: 28px 40px;
    position: relative;
  }
  body::before {
    content: "";
    position: absolute;
    top: -120px; left: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
    pointer-events: none;
  }
  body::after {
    content: "";
    position: absolute;
    bottom: -120px; right: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.14) 0%, transparent 70%);
    pointer-events: none;
  }
  .header { position: relative; z-index: 2; margin-bottom: 10px; }
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

  .cards-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 14px;
    flex: 1;
    position: relative;
    z-index: 2;
    margin-bottom: 8px;
  }
  .col-card {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border-top: 4px solid transparent;
  }
  .col-lula { border-top-color: #3b82f6; }
  .col-flavio { border-top-color: #f97316; }
  .col-base { border-top-color: #10b981; }

  .col-header {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
    margin-bottom: 10px;
  }
  .col-title { font-size: 13.5px; font-weight: 800; color: #fff; }
  .col-meta { font-size: 11px; color: #94a3b8; margin-top: 2px; display: flex; justify-content: space-between; }
  .col-aprov { font-weight: 700; color: #fff; }

  .quotes-stack {
    display: flex;
    flex-direction: column;
    gap: 9px;
    flex: 1;
    justify-content: space-around;
  }
  .speech-bubble {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 8px 10px;
    position: relative;
  }
  .speaker-id {
    font-size: 10px;
    font-weight: 700;
    color: #38bdf8;
    margin-bottom: 2px;
    display: flex;
    justify-content: space-between;
  }
  .speaker-tag { color: #94a3b8; font-weight: 500; font-size: 9.5px; }
  .speech-text {
    font-size: 11px;
    line-height: 1.35;
    color: #f1f5f9;
    font-style: italic;
  }
  .speech-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
    font-size: 9.5px;
    color: #64748b;
  }
  .concern-badge {
    background: rgba(255, 255, 255, 0.07);
    padding: 1px 5px;
    border-radius: 4px;
    color: #cbd5e1;
  }

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
    <div class="badge"><span class="badge-dot"></span>Vozes dos 100 Cidadãos Sintéticos · DeepSeek & IBGE</div>
    <h1>O Que Falaram os Cidadãos: Depoimentos Reais da Simulação</h1>
    <p class="subtitle">Declarações trimestrais extraídas diretamente de results.json avaliando a vida material e o bolso</p>
  </div>

  <div class="cards-row">
    <!-- COL LULA -->
    <div class="col-card col-lula">
      <div class="col-header">
        <div class="col-title" style="color: #60a5fa;">No Governo Lula</div>
        <div class="col-meta">
          <span>Aprovação Média: <strong class="col-aprov" style="color: #60a5fa;">45,4%</strong></span>
          <span>Sentimento: <strong style="color: #34d399;">+0,12</strong></span>
        </div>
      </div>
      <div class="quotes-stack">
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Ambulante Informal · Norte</span>
            <span class="speaker-tag">Até 1 SM</span>
          </div>
          <div class="speech-text">"Salário mínimo subindo ajuda, mas na feira o povo ainda aperta o cinto com a comida cara pela seca."</div>
          <div class="speech-footer">
            <span class="concern-badge">Preços de alimentos</span>
            <span style="color: #34d399; font-weight: 700;">Aprov: 52%</span>
          </div>
        </div>
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Operadora de Call-Center · Sudeste</span>
            <span class="speaker-tag">1 a 2 SM</span>
          </div>
          <div class="speech-text">"A comida segue cara, mas o mínimo subiu um pouco e o serviço anda. Fila do SUS menor já é um bom começo."</div>
          <div class="speech-footer">
            <span class="concern-badge">Custo de vida</span>
            <span style="color: #34d399; font-weight: 700;">Aprov: 62%</span>
          </div>
        </div>
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Técnico Agropecuário · Nordeste</span>
            <span class="speaker-tag">2 a 5 SM</span>
          </div>
          <div class="speech-text">"Selic de 12% trava tudo: crédito caro e ninguém investe. E ainda aperta o agro com tanta fiscalização ambiental."</div>
          <div class="speech-footer">
            <span class="concern-badge">Juros e crédito</span>
            <span style="color: #f87171; font-weight: 700;">Aprov: 38%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- COL FLAVIO -->
    <div class="col-card col-flavio">
      <div class="col-header">
        <div class="col-title" style="color: #fb923c;">No Governo Flávio</div>
        <div class="col-meta">
          <span>Aprovação Média: <strong class="col-aprov" style="color: #fb923c;">42,6%</strong></span>
          <span>Sentimento: <strong style="color: #fbbf24;">-0,05</strong></span>
        </div>
      </div>
      <div class="quotes-stack">
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Comerciante / MEI · Centro-Oeste</span>
            <span class="speaker-tag">2 a 5 SM</span>
          </div>
          <div class="speech-text">"Vendo pouco, o povo reclama do preço e da conta de luz, mas o governo só fala em corte de dívida no jornal."</div>
          <div class="speech-footer">
            <span class="concern-badge">Vendas e contas</span>
            <span style="color: #f87171; font-weight: 700;">Aprov: 31%</span>
          </div>
        </div>
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Operadora de Call-Center · Sudeste</span>
            <span class="speaker-tag">1 a 2 SM</span>
          </div>
          <div class="speech-text">"A inflação deu uma aliviada, mas o pente-fino no INSS me deixa com medo de perder o benefício da família."</div>
          <div class="speech-footer">
            <span class="concern-badge">Previdência</span>
            <span style="color: #34d399; font-weight: 700;">Aprov: 57%</span>
          </div>
        </div>
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Técnico Agropecuário · Nordeste</span>
            <span class="speaker-tag">2 a 5 SM</span>
          </div>
          <div class="speech-text">"Corte de gastos e juros pesam, mas o controle fiscal e o pente-fino no INSS são corretos para arrumar o país."</div>
          <div class="speech-footer">
            <span class="concern-badge">Dívida pública</span>
            <span style="color: #34d399; font-weight: 700;">Aprov: 62%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- COL BASELINE -->
    <div class="col-card col-base">
      <div class="col-header">
        <div class="col-title" style="color: #34d399;">No Cenário Base (Inércia)</div>
        <div class="col-meta">
          <span>Aprovação Média: <strong class="col-aprov" style="color: #34d399;">35,4%</strong></span>
          <span>Sentimento: <strong style="color: #f87171;">-0,28</strong></span>
        </div>
      </div>
      <div class="quotes-stack">
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Técnico de Suporte em TI · Norte</span>
            <span class="speaker-tag">2 a 5 SM</span>
          </div>
          <div class="speech-text">"Continuo no mesmo: juro de 13% trava tudo, a parcela do carro e do cartão come o salário e o serviço não melhora."</div>
          <div class="speech-footer">
            <span class="concern-badge">Juros altos</span>
            <span style="color: #f87171; font-weight: 700;">Aprov: 38%</span>
          </div>
        </div>
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Ambulante Informal · Norte</span>
            <span class="speaker-tag">Até 1 SM</span>
          </div>
          <div class="speech-text">"Vendo menos, o povo tá sem dinheiro, a comida não cai de preço e esse governo parado não faz nada para ajudar."</div>
          <div class="speech-footer">
            <span class="concern-badge">Vendas fracas</span>
            <span style="color: #f87171; font-weight: 700;">Aprov: 45%</span>
          </div>
        </div>
        <div class="speech-bubble">
          <div class="speaker-id">
            <span>Produtor Agropecuário · Sudeste</span>
            <span class="speaker-tag">2 a 5 SM</span>
          </div>
          <div class="speech-text">"Juros altos seguram insumos e máquinas. Sem nenhuma reforma nova, o Brasil continua patinando no escuro."</div>
          <div class="speech-footer">
            <span class="concern-badge">Crédito travado</span>
            <span style="color: #f87171; font-weight: 700;">Aprov: 42%</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div>1.920 declarações registradas em results.json · Cidadãos avaliam condições materiais reais sem slogans partidários</div>
    <div class="footer-link">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>
"""

# CARD 2: DISTRIBUIÇÃO MÉDIA DA APROVAÇÃO POR VOTO EM 2022
html2 = """<!doctype html>
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
    top: -120px; right: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.14) 0%, transparent 70%);
    pointer-events: none;
  }
  body::after {
    content: "";
    position: absolute;
    bottom: -120px; left: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .header { position: relative; z-index: 2; margin-bottom: 12px; }
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 3px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #a855f7; margin-bottom: 5px;
  }
  .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #a855f7; }
  h1 { font-size: 25px; font-weight: 800; color: #ffffff; letter-spacing: -0.4px; margin-bottom: 2px; }
  .subtitle { font-size: 12.5px; color: #94a3b8; }

  .content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
    flex: 1;
    position: relative;
    z-index: 2;
    margin-bottom: 10px;
  }
  .voter-card {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .voter-title {
    font-size: 14px;
    font-weight: 800;
    color: #f8fafc;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 8px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .voter-share { font-size: 11px; color: #94a3b8; font-weight: 500; }

  .bars-stack { display: flex; flex-direction: column; gap: 14px; flex: 1; justify-content: center; }
  .bar-item { display: flex; flex-direction: column; gap: 4px; }
  .bar-info { display: flex; justify-content: space-between; font-size: 12px; }
  .bar-name { font-weight: 600; color: #cbd5e1; }
  .bar-score { font-weight: 800; font-size: 13.5px; }
  .bar-track {
    width: 100%;
    height: 10px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
  }
  .bar-fill { height: 100%; border-radius: 999px; }

  .fill-lula { background: linear-gradient(90deg, #1d4ed8, #60a5fa); }
  .fill-flavio { background: linear-gradient(90deg, #c2410c, #fb923c); }
  .fill-base { background: linear-gradient(90deg, #047857, #34d399); }

  .insight-box {
    background: rgba(0, 0, 0, 0.25);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 10.5px;
    color: #94a3b8;
    line-height: 1.35;
    margin-top: 10px;
  }

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
  .footer-link { color: #a855f7; font-weight: 600; }
</style>
</head>
<body>
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>Correlação Eleitoral · Amostra PNAD / TSE</div>
    <h1>Como Cada Eleitor de 2022 Avaliou os Governos Simulados</h1>
    <p class="subtitle">Média de aprovação popular (0 a 100%) cruzando a memória de voto com os resultados de cada mandato</p>
  </div>

  <div class="content-grid">
    <!-- PANEL 1: ELEITORES PT -->
    <div class="voter-card">
      <div class="voter-title">
        Eleitores de Lula (2022)
        <span class="voter-share">40% do eleitorado</span>
      </div>
      <div class="bars-stack">
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">Sob Governo Lula</span>
            <span class="bar-score" style="color: #60a5fa;">55,0%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-lula" style="width: 55%;"></div></div>
        </div>
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">No Cenário Base</span>
            <span class="bar-score" style="color: #34d399;">41,5%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-base" style="width: 41.5%;"></div></div>
        </div>
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">Sob Governo Flávio</span>
            <span class="bar-score" style="color: #fb923c;">40,6%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-flavio" style="width: 40.6%;"></div></div>
        </div>
      </div>
      <div class="insight-box">
        <strong>Fidelidade e Demanda:</strong> Lula manteve ampla aprovação entre sua base graças ao aumento real do salário mínimo e saúde, mas sofreu desgaste pelas secas e preços de alimentos.
      </div>
    </div>

    <!-- PANEL 2: ELEITORES PL -->
    <div class="voter-card">
      <div class="voter-title">
        Eleitores de Bolsonaro (2022)
        <span class="voter-share">37% do eleitorado</span>
      </div>
      <div class="bars-stack">
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">Sob Governo Flávio</span>
            <span class="bar-score" style="color: #fb923c;">44,8%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-flavio" style="width: 44.8%;"></div></div>
        </div>
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">Sob Governo Lula</span>
            <span class="bar-score" style="color: #60a5fa;">34,8%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-lula" style="width: 34.8%;"></div></div>
        </div>
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">No Cenário Base</span>
            <span class="bar-score" style="color: #34d399;">26,4%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-base" style="width: 26.4%;"></div></div>
        </div>
      </div>
      <div class="insight-box">
        <strong>Apoio Fiscal e Rigidez:</strong> Flávio obteve sua maior nota neste grupo pelo corte de gastos e combate ao déficit, mas perdeu fôlego no fim do mandato com filas hospitalares.
      </div>
    </div>

    <!-- PANEL 3: ABSTENÇÃO / ISENTOS -->
    <div class="voter-card">
      <div class="voter-title">
        Abstenção / Nulos / Brancos
        <span class="voter-share">23% do eleitorado</span>
      </div>
      <div class="bars-stack">
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">Sob Governo Lula</span>
            <span class="bar-score" style="color: #60a5fa;">48,4%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-lula" style="width: 48.4%;"></div></div>
        </div>
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">Sob Governo Flávio</span>
            <span class="bar-score" style="color: #fb923c;">46,4%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-flavio" style="width: 46.4%;"></div></div>
        </div>
        <div class="bar-item">
          <div class="bar-info">
            <span class="bar-name">No Cenário Base</span>
            <span class="bar-score" style="color: #34d399;">35,7%</span>
          </div>
          <div class="bar-track"><div class="bar-fill fill-base" style="width: 35.7%;"></div></div>
        </div>
      </div>
      <div class="insight-box">
        <strong>O Pêndulo da Opinião:</strong> Os moderados premiaram o desemprego menor de Lula (5,5%), mas também aprovaram os cortes de tributos nos combustíveis de Flávio. O Cenário Base foi reprovado.
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Aprovação média consolidada nos 16 trimestres da simulação · Semente com 100 agentes e 5 repetições</div>
    <div class="footer-link">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>
"""

# CARD 3: AVALIAÇÃO POR FAIXA DE RENDA E TOP PREOCUPAÇÕES
html3 = """<!doctype html>
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
    width: 600px; height: 350px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.14) 0%, transparent 70%);
    pointer-events: none;
  }
  .header { position: relative; z-index: 2; margin-bottom: 10px; }
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 3px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #34d399; margin-bottom: 5px;
  }
  .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #34d399; }
  h1 { font-size: 25px; font-weight: 800; color: #ffffff; letter-spacing: -0.4px; margin-bottom: 2px; }
  .subtitle { font-size: 12.5px; color: #94a3b8; }

  .content-grid {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 18px;
    flex: 1;
    position: relative;
    z-index: 2;
    margin-bottom: 10px;
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
    font-size: 13.5px;
    font-weight: 800;
    color: #f8fafc;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 6px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
  }
  .panel-title span { font-size: 11px; color: #64748b; font-weight: 500; }

  /* Income groups comparison table */
  .income-rows { display: flex; flex-direction: column; gap: 9px; }
  .inc-row {
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 8px 12px;
  }
  .inc-header { display: flex; justify-content: space-between; font-size: 11.5px; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; }
  .inc-sub { font-size: 10px; color: #94a3b8; font-weight: normal; }
  .inc-bars { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .bar-side { display: flex; align-items: center; gap: 8px; font-size: 11px; }
  .mini-track { flex: 1; height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 4px; overflow: hidden; }
  .mini-fill { height: 100%; border-radius: 4px; }

  /* Concerns ranking */
  .concern-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 7px 10px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    margin-bottom: 6px;
  }
  .concern-rank { font-weight: 800; color: #34d399; font-size: 12px; margin-right: 8px; }
  .concern-text { font-size: 11.5px; color: #e2e8f0; font-weight: 600; flex: 1; }
  .concern-freq { font-size: 10.5px; color: #94a3b8; background: rgba(255, 255, 255, 0.06); padding: 2px 6px; border-radius: 4px; }

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
  .footer-link { color: #34d399; font-weight: 600; }
</style>
</head>
<body>
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>Estrutura Social & Ansiedades · brazil-sim</div>
    <h1>Aprovação por Classe de Renda e as Maiores Preocupações</h1>
    <p class="subtitle">Como cada fatia socioeconômica reagiu às políticas e o ranking das queixas mais frequentes</p>
  </div>

  <div class="content-grid">
    <!-- LEFT: INCOME BREAKDOWN -->
    <div class="panel">
      <div class="panel-title">
        Aprovação Média por Estrato Social
        <span>Lula vs. Flávio</span>
      </div>
      <div class="income-rows">
        <div class="inc-row">
          <div class="inc-header">
            <span>Até 1 Salário Mínimo (31% da população)</span>
            <span class="inc-sub">Ambulantes, diaristas, rurais</span>
          </div>
          <div class="inc-bars">
            <div class="bar-side">
              <span style="color: #60a5fa; font-weight: 700; width: 45px;">Lula</span>
              <div class="mini-track"><div class="mini-fill" style="width: 38.8%; background: #3b82f6;"></div></div>
              <strong style="color: #60a5fa;">38,8%</strong>
            </div>
            <div class="bar-side">
              <span style="color: #fb923c; font-weight: 700; width: 45px;">Flávio</span>
              <div class="mini-track"><div class="mini-fill" style="width: 43.1%; background: #f97316;"></div></div>
              <strong style="color: #fb923c;">43,1%</strong>
            </div>
          </div>
        </div>

        <div class="inc-row">
          <div class="inc-header">
            <span>1 a 2 Salários Mínimos (25% da população)</span>
            <span class="inc-sub">Caixas, call-center, motoristas</span>
          </div>
          <div class="inc-bars">
            <div class="bar-side">
              <span style="color: #60a5fa; font-weight: 700; width: 45px;">Lula</span>
              <div class="mini-track"><div class="mini-fill" style="width: 48.1%; background: #3b82f6;"></div></div>
              <strong style="color: #60a5fa;">48,1%</strong>
            </div>
            <div class="bar-side">
              <span style="color: #fb923c; font-weight: 700; width: 45px;">Flávio</span>
              <div class="mini-track"><div class="mini-fill" style="width: 42.5%; background: #f97316;"></div></div>
              <strong style="color: #fb923c;">42,5%</strong>
            </div>
          </div>
        </div>

        <div class="inc-row">
          <div class="inc-header">
            <span>2 a 5 Salários Mínimos (33% da população)</span>
            <span class="inc-sub">Professores, policiais, técnicos</span>
          </div>
          <div class="inc-bars">
            <div class="bar-side">
              <span style="color: #60a5fa; font-weight: 700; width: 45px;">Lula</span>
              <div class="mini-track"><div class="mini-fill" style="width: 46.4%; background: #3b82f6;"></div></div>
              <strong style="color: #60a5fa;">46,4%</strong>
            </div>
            <div class="bar-side">
              <span style="color: #fb923c; font-weight: 700; width: 45px;">Flávio</span>
              <div class="mini-track"><div class="mini-fill" style="width: 47.7%; background: #f97316;"></div></div>
              <strong style="color: #fb923c;">47,7%</strong>
            </div>
          </div>
        </div>

        <div class="inc-row">
          <div class="inc-header">
            <span>Mais de 5 Salários Mínimos (11% da população)</span>
            <span class="inc-sub">Médicos, advogados, gerentes</span>
          </div>
          <div class="inc-bars">
            <div class="bar-side">
              <span style="color: #60a5fa; font-weight: 700; width: 45px;">Lula</span>
              <div class="mini-track"><div class="mini-fill" style="width: 57.6%; background: #3b82f6;"></div></div>
              <strong style="color: #60a5fa;">57,6%</strong>
            </div>
            <div class="bar-side">
              <span style="color: #fb923c; font-weight: 700; width: 45px;">Flávio</span>
              <div class="mini-track"><div class="mini-fill" style="width: 40.1%; background: #f97316;"></div></div>
              <strong style="color: #fb923c;">40,1%</strong>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT: TOP CONCERNS -->
    <div class="panel">
      <div class="panel-title">
        Ranking das Maiores Preocupações
        <span>Frequência nas Citações</span>
      </div>

      <div class="concerns-list">
        <div class="concern-item">
          <span class="concern-rank">1º</span>
          <span class="concern-text">Preço dos Alimentos & Custo de Vida</span>
          <span class="concern-freq">38% das queixas</span>
        </div>
        <div class="concern-item">
          <span class="concern-rank">2º</span>
          <span class="concern-text">Taxa Selic & Juros Altos no Crédito</span>
          <span class="concern-freq">24% das queixas</span>
        </div>
        <div class="concern-item">
          <span class="concern-rank">3º</span>
          <span class="concern-text">Filas e Atendimento no SUS</span>
          <span class="concern-freq">16% das queixas</span>
        </div>
        <div class="concern-item">
          <span class="concern-rank">4º</span>
          <span class="concern-text">Insegurança com Aposentadoria / INSS</span>
          <span class="concern-freq">12% das queixas</span>
        </div>
        <div class="concern-item">
          <span class="concern-rank">5º</span>
          <span class="concern-text">Violência Urbana & Facções Criminosas</span>
          <span class="concern-freq">10% das queixas</span>
        </div>
      </div>

      <div style="font-size: 10px; color: #94a3b8; margin-top: 8px; line-height: 1.35; background: rgba(0,0,0,0.25); padding: 8px; border-radius: 6px;">
        * O choque climático de seca dominou a inflação nos dois governos; os mais ricos premiaram a estabilidade democrática de Lula, enquanto a classe média valorizou o rigor fiscal inicial de Flávio.
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Mapeamento gerado a partir de microdados de aprovação e sentimentos · Experimento brazil-sim</div>
    <div class="footer-link">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>
"""

# Write HTML files
f1_html = ARTIFACT_DIR / "feedback_card1_falas_cidadaos.html"
f2_html = ARTIFACT_DIR / "feedback_card2_aprovacao_voto_2022.html"
f3_html = ARTIFACT_DIR / "feedback_card3_renda_preocupacoes.html"

f1_png = ARTIFACT_DIR / "feedback_card1_falas_cidadaos.png"
f2_png = ARTIFACT_DIR / "feedback_card2_aprovacao_voto_2022.png"
f3_png = ARTIFACT_DIR / "feedback_card3_renda_preocupacoes.png"

f1_html.write_text(html1, encoding="utf-8")
f2_html.write_text(html2, encoding="utf-8")
f3_html.write_text(html3, encoding="utf-8")

print("Wrote HTMLs.")

for html_p, png_p in [(f1_html, f1_png), (f2_html, f2_png), (f3_html, f3_png)]:
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1200,675",
        f"--screenshot={png_p}",
        html_p.as_uri()
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated {png_p}: exists={png_p.exists()}, size={png_p.stat().st_size}")

