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

# Card 1 HTML
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
    padding: 32px 42px;
    position: relative;
  }
  body::before {
    content: "";
    position: absolute;
    top: -100px; left: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.14) 0%, transparent 70%);
    pointer-events: none;
  }
  body::after {
    content: "";
    position: absolute;
    bottom: -100px; right: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(249, 115, 22, 0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .header { position: relative; z-index: 2; margin-bottom: 12px; }
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 3px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #38bdf8; margin-bottom: 6px;
  }
  .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #38bdf8; }
  h1 { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.4px; margin-bottom: 3px; }
  .subtitle { font-size: 13px; color: #94a3b8; }
  
  .grid-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
    gap: 16px;
    flex: 1;
    position: relative;
    z-index: 2;
    margin-bottom: 12px;
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
    font-weight: 700;
    color: #f8fafc;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 6px;
    margin-bottom: 10px;
  }
  .panel-title span { font-size: 11px; color: #64748b; font-weight: 500; }
  .bar-group { display: flex; flex-direction: column; gap: 7px; }
  .bar-row { display: flex; flex-direction: column; gap: 2px; }
  .bar-label-line { display: flex; justify-content: space-between; font-size: 11.5px; }
  .bar-label { color: #cbd5e1; font-weight: 500; }
  .bar-val { color: #f8fafc; font-weight: 700; }
  .bar-ref { color: #64748b; font-size: 10px; margin-left: 4px; }
  .bar-track {
    width: 100%;
    height: 7px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
  }
  .bar-fill { height: 100%; border-radius: 999px; }
  
  .fill-blue { background: linear-gradient(90deg, #2563eb, #38bdf8); }
  .fill-orange { background: linear-gradient(90deg, #ea580c, #fb923c); }
  .fill-emerald { background: linear-gradient(90deg, #059669, #34d399); }
  .fill-purple { background: linear-gradient(90deg, #7c3aed, #a78bfa); }
  .fill-pink { background: linear-gradient(90deg, #db2777, #f472b6); }
  
  .footer {
    position: relative;
    z-index: 2;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 8px;
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #64748b;
  }
  .footer-link { color: #38bdf8; font-weight: 600; }
</style>
</head>
<body>
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>Demografia Sintética · Censo IBGE & TSE</div>
    <h1>Perfil Demográfico dos 100 Cidadãos Virtuais</h1>
    <p class="subtitle">Estratificação representativa do Brasil simulado por IA trimestre a trimestre de 2027 a 2030</p>
  </div>

  <div class="grid-container">
    <!-- Panel 1: Renda -->
    <div class="panel">
      <div class="panel-title">
        Faixa de Renda Domiciliar
        <span>Amostra vs. PNAD</span>
      </div>
      <div class="bar-group">
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Até 1 Salário Mínimo</span>
            <div><span class="bar-val">31%</span> <span class="bar-ref">(PNAD: 30%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-blue" style="width: 31%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">1 a 2 Salários Mínimos</span>
            <div><span class="bar-val">25%</span> <span class="bar-ref">(PNAD: 32%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-blue" style="width: 25%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">2 a 5 Salários Mínimos</span>
            <div><span class="bar-val">33%</span> <span class="bar-ref">(PNAD: 26%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-blue" style="width: 33%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Mais de 5 Salários Mínimos</span>
            <div><span class="bar-val">11%</span> <span class="bar-ref">(PNAD: 12%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-blue" style="width: 11%;"></div></div>
        </div>
      </div>
    </div>

    <!-- Panel 2: Região -->
    <div class="panel">
      <div class="panel-title">
        Distribuição Geográfica
        <span>Por Macrorregião</span>
      </div>
      <div class="bar-group">
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Sudeste</span>
            <div><span class="bar-val">33%</span> <span class="bar-ref">(IBGE: 41,8%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-emerald" style="width: 33%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Nordeste</span>
            <div><span class="bar-val">24%</span> <span class="bar-ref">(IBGE: 26,9%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-emerald" style="width: 24%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Sul</span>
            <div><span class="bar-val">18%</span> <span class="bar-ref">(IBGE: 14,7%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-emerald" style="width: 18%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Centro-Oeste</span>
            <div><span class="bar-val">13%</span> <span class="bar-ref">(IBGE: 8,1%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-emerald" style="width: 13%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Norte</span>
            <div><span class="bar-val">12%</span> <span class="bar-ref">(IBGE: 8,5%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-emerald" style="width: 12%;"></div></div>
        </div>
      </div>
    </div>

    <!-- Panel 3: Religião -->
    <div class="panel">
      <div class="panel-title">
        Afiliação Religiosa
        <span>Censo Demográfico</span>
      </div>
      <div class="bar-group">
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Católica</span>
            <div><span class="bar-val">51%</span> <span class="bar-ref">(Censo: 50%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-purple" style="width: 51%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Evangélica</span>
            <div><span class="bar-val">27%</span> <span class="bar-ref">(Censo: 27%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-purple" style="width: 27%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Outras Religiões (Espírita, Umbanda, etc.)</span>
            <div><span class="bar-val">14%</span> <span class="bar-ref">(Censo: 13%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-purple" style="width: 14%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Sem religião</span>
            <div><span class="bar-val">8%</span> <span class="bar-ref">(Censo: 10%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-purple" style="width: 8%;"></div></div>
        </div>
      </div>
    </div>

    <!-- Panel 4: Voto 2022 -->
    <div class="panel">
      <div class="panel-title">
        Comportamento Eleitoral (2022)
        <span>2º Turno Oficial TSE</span>
      </div>
      <div class="bar-group">
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Votou no candidato do PT (Lula)</span>
            <div><span class="bar-val">40%</span> <span class="bar-ref">(TSE: 38%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-orange" style="width: 40%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Votou no candidato do PL (Bolsonaro)</span>
            <div><span class="bar-val">37%</span> <span class="bar-ref">(TSE: 37%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-orange" style="width: 37%;"></div></div>
        </div>
        <div class="bar-row">
          <div class="bar-label-line">
            <span class="bar-label">Abstenção / Voto Nulo ou Branco</span>
            <div><span class="bar-val">23%</span> <span class="bar-ref">(TSE: 25%)</span></div>
          </div>
          <div class="bar-track"><div class="bar-fill fill-orange" style="width: 23%;"></div></div>
        </div>
      </div>
      <div style="font-size: 10.5px; color: #94a3b8; margin-top: 8px; line-height: 1.3;">
        Garante que a aprovação inicial não comece enviesada para nenhum dos campos políticos.
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Amostra calibrada com microdados do IBGE e TSE · Semente determinística seed-1 (100 cidadãos sintéticos)</div>
    <div class="footer-link">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>
"""

# Card 2 HTML
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
    padding: 32px 42px;
    position: relative;
  }
  body::before {
    content: "";
    position: absolute;
    top: -100px; right: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.14) 0%, transparent 70%);
    pointer-events: none;
  }
  body::after {
    content: "";
    position: absolute;
    bottom: -100px; left: -100px;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .header { position: relative; z-index: 2; margin-bottom: 12px; }
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 3px 10px; border-radius: 999px;
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #a855f7; margin-bottom: 6px;
  }
  .badge-dot { width: 6px; height: 6px; border-radius: 50%; background: #a855f7; }
  h1 { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.4px; margin-bottom: 3px; }
  .subtitle { font-size: 13px; color: #94a3b8; }
  
  .grid-container {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 16px;
    flex: 1;
    position: relative;
    z-index: 2;
    margin-bottom: 12px;
  }
  .left-col {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .right-col {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .panel {
    background: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    flex: 1;
  }
  .panel-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #f8fafc;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 6px;
    margin-bottom: 8px;
  }
  .panel-title span { font-size: 11px; color: #64748b; font-weight: 500; }

  /* Occupations tags */
  .occ-group { margin-bottom: 6px; }
  .occ-header { font-size: 11px; font-weight: 700; color: #94a3b8; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
  .occ-badges { display: flex; flex-wrap: wrap; gap: 5px; }
  .occ-pill {
    font-size: 10.5px;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .occ-pill strong { color: #38bdf8; }

  .bar-group { display: flex; flex-direction: column; gap: 7px; }
  .bar-row { display: flex; flex-direction: column; gap: 2px; }
  .bar-label-line { display: flex; justify-content: space-between; font-size: 11.5px; }
  .bar-label { color: #cbd5e1; font-weight: 500; }
  .bar-val { color: #f8fafc; font-weight: 700; }
  .bar-track {
    width: 100%;
    height: 7px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 999px;
    overflow: hidden;
  }
  .bar-fill { height: 100%; border-radius: 999px; }
  
  .fill-purple { background: linear-gradient(90deg, #7c3aed, #c084fc); }
  .fill-cyan { background: linear-gradient(90deg, #0284c7, #38bdf8); }
  .fill-amber { background: linear-gradient(90deg, #d97706, #fbbf24); }

  .area-stat-box {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 4px;
  }
  .area-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 10px;
    text-align: center;
  }
  .area-num { font-size: 22px; font-weight: 800; color: #38bdf8; }
  .area-txt { font-size: 11px; color: #94a3b8; margin-top: 2px; }
  
  .footer {
    position: relative;
    z-index: 2;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 8px;
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #64748b;
  }
  .footer-link { color: #a855f7; font-weight: 600; }
</style>
</head>
<body>
  <div class="header">
    <div class="badge"><span class="badge-dot"></span>Ocupações & Estrutura Social · 100 Personas</div>
    <h1>Profissões, Escolaridade e Recortes Etários</h1>
    <p class="subtitle">Como a diversidade do mercado de trabalho e a formação educacional foram distribuídas no modelo</p>
  </div>

  <div class="grid-container">
    <!-- Left Col: Occupations Breakdown -->
    <div class="panel">
      <div class="panel-title">
        Mapeamento das 23 Profissões na Amostra
        <span>Por Faixa de Renda</span>
      </div>

      <div class="occ-group">
        <div class="occ-header">Base da Pirâmide (Até 1 Salário Mínimo — 31%)</div>
        <div class="occ-badges">
          <span class="occ-pill">Ambulante informal <strong>7</strong></span>
          <span class="occ-pill">Trabalhador rural <strong>7</strong></span>
          <span class="occ-pill">Desempregado <strong>5</strong></span>
          <span class="occ-pill">Diarista doméstica <strong>5</strong></span>
          <span class="occ-pill">Aposentado do INSS <strong>4</strong></span>
          <span class="occ-pill">Entregador de app <strong>3</strong></span>
        </div>
      </div>

      <div class="occ-group">
        <div class="occ-header">Trabalhadores Formais e Serviços (1 a 2 Salários Mínimos — 25%)</div>
        <div class="occ-badges">
          <span class="occ-pill">Caixa de supermercado <strong>5</strong></span>
          <span class="occ-pill">Teleatendimento / Call-center <strong>5</strong></span>
          <span class="occ-pill">Motorista de caminhão <strong>5</strong></span>
          <span class="occ-pill">Pequeno agricultor <strong>5</strong></span>
          <span class="occ-pill">Técnico de enfermagem <strong>3</strong></span>
          <span class="occ-pill">Operário de obras <strong>2</strong></span>
        </div>
      </div>

      <div class="occ-group">
        <div class="occ-header">Classe Média & Especialistas (2 a 5 Salários Mínimos — 33%)</div>
        <div class="occ-badges">
          <span class="occ-pill">Técnico agropecuário <strong>8</strong></span>
          <span class="occ-pill">Professor rede pública <strong>7</strong></span>
          <span class="occ-pill">Comerciante / MEI <strong>5</strong></span>
          <span class="occ-pill">Técnico em TI <strong>5</strong></span>
          <span class="occ-pill">Policial civil/militar <strong>4</strong></span>
          <span class="occ-pill">Bancário <strong>4</strong></span>
        </div>
      </div>

      <div class="occ-group">
        <div class="occ-header">Alta Renda & Nível Superior (> 5 Salários Mínimos — 11%)</div>
        <div class="occ-badges">
          <span class="occ-pill">Médico(a) <strong>4</strong></span>
          <span class="occ-pill">Advogado(a) <strong>3</strong></span>
          <span class="occ-pill">Gerente corporativo <strong>2</strong></span>
          <span class="occ-pill">Engenheiro de software <strong>1</strong></span>
          <span class="occ-pill">Servidor de carreira <strong>1</strong></span>
        </div>
      </div>
    </div>

    <!-- Right Col: Education, Age, Area -->
    <div class="right-col">
      <!-- Escolaridade -->
      <div class="panel">
        <div class="panel-title">
          Nível de Escolaridade Estimado
          <span>Inferência PNAD</span>
        </div>
        <div class="bar-group">
          <div class="bar-row">
            <div class="bar-label-line">
              <span class="bar-label">Fundamental (Incompleto/Completo)</span>
              <span class="bar-val">31%</span>
            </div>
            <div class="bar-track"><div class="bar-fill fill-purple" style="width: 31%;"></div></div>
          </div>
          <div class="bar-row">
            <div class="bar-label-line">
              <span class="bar-label">Ensino Médio (Regular / Técnico)</span>
              <span class="bar-val">25%</span>
            </div>
            <div class="bar-track"><div class="bar-fill fill-purple" style="width: 25%;"></div></div>
          </div>
          <div class="bar-row">
            <div class="bar-label-line">
              <span class="bar-label">Médio Completo / Superior em Andamento</span>
              <span class="bar-val">33%</span>
            </div>
            <div class="bar-track"><div class="bar-fill fill-purple" style="width: 33%;"></div></div>
          </div>
          <div class="bar-row">
            <div class="bar-label-line">
              <span class="bar-label">Superior Completo / Pós-graduação</span>
              <span class="bar-val">11%</span>
            </div>
            <div class="bar-track"><div class="bar-fill fill-purple" style="width: 11%;"></div></div>
          </div>
        </div>
      </div>

      <!-- Idade e Área -->
      <div class="panel">
        <div class="panel-title">
          Faixa Etária & Residência
          <span>Pirâmide IBGE</span>
        </div>
        <div class="bar-group" style="margin-bottom: 8px;">
          <div class="bar-row">
            <div class="bar-label-line">
              <span class="bar-label">40 a 59 anos: <strong>38%</strong> | 25 a 39 anos: <strong>24%</strong></span>
              <span class="bar-label">60+ anos: <strong>24%</strong> | 16 a 24 anos: <strong>14%</strong></span>
            </div>
            <div class="bar-track"><div class="bar-fill fill-amber" style="width: 100%;"></div></div>
          </div>
        </div>
        <div class="area-stat-box">
          <div class="area-card">
            <div class="area-num">87%</div>
            <div class="area-txt">Zona Urbana (Cidades)</div>
          </div>
          <div class="area-card">
            <div class="area-num">13%</div>
            <div class="area-txt">Zona Rural (Campo)</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    <div>Personagens avaliam suas vidas a partir de seus contextos materiais reais · Sem influência de pesquisas de voto</div>
    <div class="footer-link">github.com/CaiqueCoelho/brazil-ai-simulation</div>
  </div>
</body>
</html>
"""

# Write HTMLs
p1_html = ARTIFACT_DIR / "distribuicao_cidadaos_demografia.html"
p2_html = ARTIFACT_DIR / "distribuicao_cidadaos_socioeconomico.html"
p1_png = ARTIFACT_DIR / "distribuicao_cidadaos_demografia.png"
p2_png = ARTIFACT_DIR / "distribuicao_cidadaos_socioeconomico.png"

p1_html.write_text(html1, encoding="utf-8")
p2_html.write_text(html2, encoding="utf-8")

print(f"Wrote {p1_html}")
print(f"Wrote {p2_html}")

# Render with Chrome
cmd1 = [
    CHROME,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1200,675",
    f"--screenshot={p1_png}",
    p1_html.as_uri()
]
cmd2 = [
    CHROME,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1200,675",
    f"--screenshot={p2_png}",
    p2_html.as_uri()
]

subprocess.run(cmd1, check=True)
subprocess.run(cmd2, check=True)

print("Images generated successfully:")
print("1:", p1_png, p1_png.exists(), p1_png.stat().st_size)
print("2:", p2_png, p2_png.exists(), p2_png.stat().st_size)
