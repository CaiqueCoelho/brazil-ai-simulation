import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path("/Users/caiquecoelho/Documents/Projects/directory/brazil-sim")
ARTIFACT_DIR = Path("/Users/caiquecoelho/.gemini/antigravity/brain/bd608ae0-4bdf-4dd6-ac9a-79f71d837a11")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

html_file = ARTIFACT_DIR / "guia_definitivo_economia_simulacao.html"
pdf_file = ARTIFACT_DIR / "guia_definitivo_economia_simulacao.pdf"

img_demografia = (ARTIFACT_DIR / "distribuicao_cidadaos_demografia.png").as_uri()
img_socio = (ARTIFACT_DIR / "distribuicao_cidadaos_socioeconomico.png").as_uri()
img_congresso = (ARTIFACT_DIR / "congresso_composicao_2026.png").as_uri()

html_content = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>O Guia Descomplicado da Simulação do Brasil: Metodologia, Equações e Resultados</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-center {{
      content: counter(page);
      font-size: 8.5pt;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #71717a;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font: 10.5pt/1.58 Georgia, "Times New Roman", serif;
    color: #18181b;
    margin: 0;
    padding: 0;
  }}
  
  /* Headings */
  h1, h2, h3, h4 {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #09090b;
    letter-spacing: -0.3px;
  }}
  h1 {{ font-size: 24pt; line-height: 1.15; font-weight: 800; margin: 0 0 10px; }}
  h2 {{ font-size: 15pt; line-height: 1.25; font-weight: 700; margin: 24px 0 8px; border-bottom: 2px solid #e4e4e7; padding-bottom: 4px; break-after: avoid; }}
  h3 {{ font-size: 12pt; line-height: 1.3; font-weight: 700; margin: 16px 0 6px; break-after: avoid; color: #1e293b; }}
  h4 {{ font-size: 10.5pt; font-weight: 700; margin: 12px 0 4px; break-after: avoid; color: #334155; }}
  
  p {{ margin: 0 0 10px; text-align: justify; hyphens: auto; }}
  
  .lead {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 11.5pt;
    line-height: 1.45;
    color: #475569;
    margin-bottom: 16px;
  }}
  
  .badge {{
    display: inline-block;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 8pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    background: #0284c7;
    color: #fff;
    padding: 3px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
  }}
  
  /* Callout Boxes */
  .box {{
    background: #f8fafc;
    border-left: 4px solid #0284c7;
    border-radius: 0 6px 6px 0;
    padding: 12px 14px;
    margin: 12px 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 9.5pt;
    line-height: 1.45;
    break-inside: avoid;
  }}
  .box.warn {{ border-left-color: #ea580c; background: #fff7ed; }}
  .box.success {{ border-left-color: #10b981; background: #ecfdf5; }}
  .box-title {{ font-weight: 700; font-size: 10pt; margin-bottom: 4px; color: #0f172a; display: flex; align-items: center; gap: 5px; }}
  
  /* Equations and Analogies */
  .equation-box {{
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 12px 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    break-inside: avoid;
  }}
  .eq-title {{
    font-size: 11pt;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
  }}
  .eq-formula {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 12px;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 9.5pt;
    font-weight: 700;
    color: #1e293b;
    margin: 6px 0 8px;
  }}
  .analogy {{
    background: #fefce8;
    border-left: 4px solid #eab308;
    padding: 8px 12px;
    border-radius: 0 6px 6px 0;
    font-size: 9.3pt;
    color: #713f12;
    margin-top: 6px;
  }}

  /* Tables */
  table.score-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 8.8pt;
    margin: 12px 0;
    break-inside: avoid;
  }}
  table.score-table th {{
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
    text-align: left;
    padding: 6px 8px;
    border-bottom: 2px solid #cbd5e1;
  }}
  table.score-table td {{
    padding: 5px 8px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: middle;
  }}
  table.score-table tr:nth-child(even) {{ background: #fafafa; }}
  .win-lula {{ color: #2563eb; font-weight: 700; }}
  .win-flavio {{ color: #ea580c; font-weight: 700; }}
  .win-tie {{ color: #64748b; font-weight: 700; }}
  
  /* Images */
  .fig {{
    margin: 14px 0;
    text-align: center;
    break-inside: avoid;
  }}
  .fig img {{
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .fig-cap {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 8.2pt;
    color: #64748b;
    margin-top: 4px;
    text-align: center;
  }}

  .pagebreak {{ break-before: page; }}

  ul, ol {{ margin: 0 0 10px 18px; padding: 0; }}
  li {{ margin-bottom: 4px; }}
  
  .highlight {{ background: #fef08a; padding: 0 3px; border-radius: 2px; }}
  
  .quote {{
    font-style: italic;
    color: #334155;
    background: #f8fafc;
    border-left: 3px solid #94a3b8;
    padding: 6px 12px;
    margin: 6px 0;
    font-size: 9.3pt;
  }}
</style>
</head>
<body>

  <!-- CAPA E INTRODUÇÃO -->
  <div class="badge">Relatório Técnico & Didático Exclusivo</div>
  <h1>O Guia Descomplicado da Simulação do Brasil (2027–2030)</h1>
  <p class="lead">Entenda a metodologia completa, como funcionam as equações matemáticas (explicadas com exemplos do dia a dia) e os motivos reais por trás do placar final de 9 a 1 entre os planos de Lula e Flávio Bolsonaro.</p>

  <div class="box warn">
    <div class="box-title">⚠️ Antes de Tudo: O que é e o que NÃO é este estudo</div>
    <ul>
      <li><strong>Não é previsão do futuro nem bola de cristal:</strong> É um teste de laboratório científico em computador.</li>
      <li><strong>Não é pesquisa eleitoral de opinião:</strong> Nenhuma pessoa real foi entrevistada. A "aprovação" mede a reação simulada de personagens virtuais criados a partir dos dados do Censo do IBGE.</li>
      <li><strong>Não julga a pessoa física nem o caráter:</strong> O teste analisou unicamente as <em>propostas escritas</em> oficiais registradas no TSE em 2026.</li>
    </ul>
  </div>

  <h2>1. Como Foi Feito o Experimento? (A Metodologia em Linguagem Simples)</h2>
  <p>Imagine que você pudesse criar uma cópia virtual do Brasil dentro de um videogame ultrarrealista. Você coloca para rodar quatro anos de mandato (de janeiro de 2027 até o fim de 2030, divididos de três em três meses) sob as propostas de governo registradas no TSE por <strong>Lula</strong> e por <strong>Flávio Bolsonaro</strong>, além de um terceiro Brasil de controle — o <strong>Cenário Base</strong> — onde o governo não faz nada de novo e apenas deixa as coisas como estão.</p>

  <h3>A Regra de Ouro: "Os Agentes de IA Decidem, as Equações Calculam"</h3>
  <p>Muitas pessoas acham que a Inteligência Artificial (como o DeepSeek ou o ChatGPT) simplesmente "chutou" os números do PIB, da inflação e do desemprego. <strong>Isso não aconteceu.</strong></p>
  <p>Modelos de inteligência artificial são excelentes para interpretar papéis sociais (como negociar no Congresso ou falar como um comerciante bravo com a conta de luz), mas são péssimos em fazer contas matemáticas sem inventar números. Por isso, o experimento fez uma divisão rigorosa:</p>
  <ul>
    <li><strong>A Política foi feita por Inteligência Artificial:</strong> O Presidente decide quais projetos enviar; os 3 blocos do Congresso votam conforme suas bancadas; o STF julga se as leis ferem a Constituição; e 100 cidadãos virtuais dizem se suas vidas melhoraram ou pioraram.</li>
    <li><strong>A Economia foi calculada por um Motor Matemático em Python:</strong> Nenhuma IA inventa a inflação ou o PIB. Todas as decisões dos políticos viram números que entram em um sistema de equações calibrado com 34 trimestres de dados oficiais reais (de 2018 a 2026) do Banco Central e do IBGE.</li>
  </ul>

  <h3>Blindagem Científica: Ninguém Sabia Quem Estava Governando</h3>
  <p>Para evitar que a inteligência artificial torcesse por um candidato ou tivesse preconceito político:</p>
  <ol>
    <li><strong>Cegueira Total de Nomes:</strong> A IA nunca lia a palavra "Lula", "Bolsonaro", "PT" ou "PL". O governante era chamado apenas de <em>"o Presidente"</em>.</li>
    <li><strong>Linguagem Neutra:</strong> Todas as propostas do TSE foram limpas de slogans publicitários. Nada de "Pátria Amada" ou "O Brasil da Esperança" — apenas o texto frio da medida (exemplo: <em>"reduzir a jornada legal de trabalho para 40 horas semanais com dois dias de folga"</em>).</li>
    <li><strong>Histórico Anônimo:</strong> Cada grupo político recebeu um histórico de números reais de governos passados sob rótulos como <em>"Governo A"</em> e <em>"Governo B"</em>, com os anos trocados por "Ano 1, Ano 2", sem citar pandemias ou crises nominais.</li>
    <li><strong>Mundo Idêntico:</strong> Os três Brasis sofreram rigorosamente os mesmos choques climáticos (a mesma seca), os mesmos juros mundiais dos EUA e o mesmo preço internacional do petróleo.</li>
  </ol>

  <div class="pagebreak"></div>

  <h2>2. A Sociedade e o Congresso no Computador</h2>

  <h3>Quem Eram os 100 Cidadãos Virtuais?</h3>
  <p>Para medir o sentimento do povo sem fazer pesquisa falsa de rua, o modelo sorteou uma amostra de 100 personagens virtuais rigorosamente espelhados na pirâmide da sociedade brasileira apurada pelo <strong>Censo 2022 do IBGE</strong> e pela <strong>PNAD Contínua</strong>:</p>

  <div class="fig">
    <img src="{img_demografia}" alt="Perfil Demográfico dos 100 Cidadãos">
    <div class="fig-cap">Figura 1: Distribuição de renda, localização geográfica, religião e voto de 2022 dos 100 cidadãos simulados.</div>
  </div>

  <div class="fig">
    <img src="{img_socio}" alt="Perfil Socioeconômico dos Cidadãos">
    <div class="fig-cap">Figura 2: As 23 ocupações reais simuladas, níveis de escolaridade e divisão urbano/rural (87% x 13%).</div>
  </div>

  <p>Havia desde a diarista e o ambulante que ganham até 1 salário mínimo, passando pelo caminhoneiro e pela técnica de enfermagem (1 a 2 salários), pelo professor de escola pública e policial (2 a 5 salários), até o médico e o advogado (mais de 5 salários). Cada um deles avaliava a vida de acordo com o seu bolso: se o feijão subiu, o ambulante reclama; se a taxa de juros subiu, o pequeno empresário reclama do crediário travado.</p>

  <h3>O Congresso Nacional Eleito em 2026</h3>
  <p>Nenhum presidente governa sozinho como se fosse um rei. Todos os projetos que precisavam de lei foram votados pelas 513 cadeiras da Câmara dos Deputados eleitas em outubro de 2026:</p>

  <div class="fig">
    <img src="{img_congresso}" alt="Composição Política da Câmara">
    <div class="fig-cap">Figura 3: Correlação de forças na Câmara dos Deputados: Esquerda (24%), Centrão (50%) e Direita (26%).</div>
  </div>

  <p>O <strong>Centrão (50,1%)</strong> foi o dono da chave do cofre. Para aprovar qualquer projeto, tanto Lula quanto Flávio precisavam negociar com ele. O Centrão usou a estratégia clássica da política brasileira: cobrou emendas parlamentares (entre 0,1% e 0,2% do PIB) e preferiu <strong>desidratar e emendar</strong> os projetos mais radicais em vez de rejeitá-los de cara.</p>

  <div class="pagebreak"></div>

  <h2>3. As Grandes Equações da Economia Explicadas para Quem É Leigo</h2>
  <p>Aqui está o coração do estudo. Em vez de usar letras gregas e fórmulas complicadas, vamos entender o que cada equação realmente faz na vida real, usando exemplos simples de padaria, do carrinho de feira e do cartão de crédito.</p>

  <!-- EQUAÇÃO 1: O PIB -->
  <div class="equation-box">
    <div class="eq-title">1. O Crescimento da Economia (O Tamanho do Bolo / PIB)</div>
    <div class="eq-formula">Crescimento do PIB = Crescimento Natural (2,1%) + Efeito do Gasto Público + Investimentos + Clima de Negócios + Confiança - Freio dos Juros Altos ± Choques da Natureza</div>
    
    <p><strong>O que isso significa na vida real?</strong><br>
    O PIB é a soma de tudo o que o país produz: pães, carros, consultas médicas, cortes de cabelo e sacos de soja. No Brasil, se ninguém atrapalhar, a economia tende a crescer sozinha cerca de <strong>2,1% ao ano</strong> apenas pelo aumento natural da população e máquinas novas.</p>
    
    <p>O que acelera ou freia esse bolo?</p>
    <ul>
      <li><strong>Obras e compras públicas:</strong> Quando o governo constrói pontes e ferrovias, empresas faturam e contratam.</li>
      <li><strong>O freio dos juros:</strong> Se a taxa de juros do Banco Central estiver muito alta, ninguém compra carro financiado nem pega empréstimo para abrir loja, e o bolo encolhe.</li>
      <li><strong>A confiança:</strong> Se empresários e o povo sentem segurança no futuro, gastam mais hoje.</li>
    </ul>

    <div class="analogy">
      <strong>💡 A Conta Famosa: Por que 1% de corte de gastos derruba o PIB em 0,43% no curto prazo?</strong><br>
      Imagine que a economia do Brasil vale <strong>R$ 11 trilhões</strong>. 1% do PIB são <strong>R$ 110 bilhões</strong>.<br>
      Se o governo decide cortar R$ 110 bilhões de uma vez em obras, compras e serviços terceirizados para equilibrar o orçamento:<br>
      • <em>O Efeito Direto:</em> As empreiteiras param as obras e demitem pedreiros; fornecedores de merenda e empresas de segurança vendem menos.<br>
      • <em>O Efeito Cascata:</em> O pedreiro demitido corta a carne no açougue e não compra roupa para os filhos. O comerciante da esquina fatura menos e também congela contratações.<br>
      • <em>E o Mercado?</em> O mercado financeiro fica feliz que as contas estão em ordem, mas nenhum empresário constrói uma fábrica nova no dia seguinte se as lojas da cidade estão vazias.<br>
      • <em>O Resultado Medido:</em> O estudo do FMI (Guajardo et al., 2014) provou em 17 países que o saldo final é de <strong>0,43% de queda na atividade</strong> (R$ 47 bilhões a menos de riqueza girando) e 300 mil pessoas a mais desempregadas nos dois primeiros anos. Foi exatamente isso que freou o PIB de Flávio Bolsonaro (1,67% contra 1,84% de Lula).
    </div>
  </div>

  <!-- EQUAÇÃO 2: A INFLAÇÃO -->
  <div class="equation-box">
    <div class="eq-title">2. A Inflação (A Alta dos Preços na Feira)</div>
    <div class="eq-formula">Inflação Hoje = 82% da Inflação Passada + Puxão da Demanda + Subida do Dólar + Seca nas Plantações + Salto Único de Impostos</div>
    
    <p><strong>O que isso significa na vida real?</strong><br>
    A inflação mede a velocidade com que o seu dinheiro perde valor de compra. No Brasil, ela tem uma característica perversa: a <strong>inércia</strong>. Como quase tudo é reajustado pelo índice do ano anterior (aluguéis, mensalidades, tarifas e contratos), 82% da inflação passada continua rolando automaticamente para o trimestre seguinte, como um caminhão pesado descendo a serra.</p>
    
    <p>O que mexe nos preços?</p>
    <ul>
      <li><strong>Dólar alto:</strong> Como o trigo do pão e o óleo de soja seguem preços mundiais, se o dólar sobe, o café da manhã encarece.</li>
      <li><strong>Seca:</strong> Se não chove na rocha, queima o pasto e o tomate, e a conta de luz sobe com termelétricas ligadas.</li>
    </ul>

    <div class="analogy">
      <strong>💡 A Regra do "Efeito Único" (O que aconteceu com os combustíveis):</strong><br>
      Se o governo corta impostos da gasolina ou da conta de luz (como Flávio propôs, e como aconteceu em 2022), o preço cai na bomba naquele mês. Mas a gasolina não continua caindo 10% todo mês para sempre! Ela cai uma vez e para. O motor corrigiu isso para não dar uma falsa sensação de que a inflação sumiu.
    </div>
  </div>

  <div class="pagebreak"></div>

  <!-- EQUAÇÃO 3: A TAXA SELIC -->
  <div class="equation-box">
    <div class="eq-title">3. A Taxa Selic e a Regra de Taylor (O Termostato do Banco Central)</div>
    <div class="eq-formula">Juros Ideais = Juro Neutro (6,4%) + Inflação + 1,5 × (Inflação acima da Meta de 3%) + 0,5 × (PIB superaquecido)</div>
    
    <p><strong>O que isso significa na vida real?</strong><br>
    Pense no Banco Central como um aparelho de ar-condicionado com termostato:<br>
    • Se a sala começa a esquentar demais (a inflação passa da meta de 3%), o aparelho liga no modo frio máximo (o BC sobe a Selic para 12%, 13% ou 14%). O empréstimo fica caro, as compras parceladas travam, as empresas vendem menos e são forçadas a segurar os preços.<br>
    • Se a sala esfria demais (recessão e desemprego alto), o aparelho diminui a potência (corta a Selic) para incentivar as pessoas a voltarem a consumir.</p>

    <div class="analogy">
      <strong>💡 Por que o peso da inflação tem que ser 1,5?</strong><br>
      Se a inflação sobe 1 ponto e o BC sobe os juros em apenas 1 ponto, o juro real não mudou nada! Você continuaria no zero a zero. O BC precisa subir 1,5 ponto para que o juro suba <em>acima</em> da inflação e dê uma "freada" de verdade na economia.
    </div>
  </div>

  <!-- EQUAÇÃO 4: A DÍVIDA PÚBLICA -->
  <div class="equation-box">
    <div class="eq-title">4. A Dívida Pública e o Resultado Primário (O Cartão de Crédito do Governo)</div>
    <div class="eq-formula">Nova Dívida = Dívida Anterior + (Juros da Dívida - Crescimento do PIB) - Economia do Governo (Superávit)</div>
    
    <p><strong>O que isso significa na vida real?</strong><br>
    Pense na dívida pública como a fatura do cartão de crédito de uma família:<br>
    • <strong>Resultado Primário:</strong> É a diferença entre o que o governo ganha de impostos e o que gasta no mês (sem contar os juros da dívida). Se sobra dinheiro, temos <em>superávit</em>; se falta, temos <em>déficit</em>.<br>
    • <strong>A Bola de Neve dos Juros:</strong> Se os juros do seu cartão de crédito forem de 12% ao ano e o seu salário crescer apenas 2%, a sua dívida cresce sozinha como uma bola de neve, mesmo que você não faça nenhuma compra nova!</p>

    <div class="analogy">
      <strong>💡 A Única Vitória de Flávio:</strong><br>
      O plano de Flávio Bolsonaro foi o único que conseguiu estancar essa bola de neve. Cortando R$ 190 bilhões, ele zerou o déficit primário (0,0%) e fez a dívida terminar 2030 menor (102% do PIB contra 103,3% de Lula). Foi a vitória incontestável de Flávio. O problema foi o preço social pago para conseguir isso.
    </div>
  </div>

  <!-- EQUAÇÃO 5: POBREZA E SALÁRIO MÍNIMO -->
  <div class="equation-box">
    <div class="eq-title">5. Pobreza, Fome e o Salário Mínimo (A Boia de Salvação da Pirâmide)</div>
    <div class="eq-formula">Pobreza = Pobreza Anterior + Efeito do Desemprego - Ganho Real do Salário Mínimo - Reajuste de Aposentadorias e BPC - Bolsa Família</div>
    
    <p><strong>O que isso significa na vida real?</strong><br>
    No Brasil, o salário mínimo não serve apenas para quem bate ponto com carteira assinada. <strong>Ele rege por lei mais de 65% de todas as aposentadorias do INSS e o BPC</strong> (o benefício pago a idosos e pessoas com deficiência na extrema pobreza).</p>
    
    <p>Quando o salário mínimo tem aumento real (acima da inflação), o dinheiro pinga direto no prato de comida e na farmácia das famílias mais pobres do país inteiro.</p>

    <div class="analogy">
      <strong>💡 Por que o plano de Flávio aumentou a pobreza se ele prometeu manter o Bolsa Família?</strong><br>
      Para conseguir economizar R$ 190 bilhões sem quebrar o país, a equipe de Flávio propôs que as aposentadorias e o BPC fossem corrigidos <em>apenas pela inflação passada</em>, sem o ganho real do salário mínimo. Isso tirou o poder de compra de milhões de famílias humildes ao longo de 4 anos. Já Lula manteve a valorização do mínimo acima da inflação, fazendo a pobreza cair para <strong>22,7% contra 23,3% de Flávio</strong> e reduzindo a fome para <strong>2,31% contra 2,48%</strong>.
    </div>
  </div>

  <div class="pagebreak"></div>

  <h2>4. O Placar Geral dos 11 Indicadores e Por Que Deu 9 a 1</h2>
  <p>Ao final dos 4 anos simulados, somando todas as repetições e comparando indicador por indicador sob as regras oficiais de margem de tolerância, o resultado consolidou-se em:</p>

  <div class="box success">
    <div class="box-title">🏆 Placar Final Auditado: Lula 9 × 1 Flávio Bolsonaro (com 1 Empate Técnico)</div>
    <p>Lula vence em 9 categorias: <strong>Desemprego, Pobreza, Desigualdade (Gini), Fome, Mortalidade Infantil, Homicídios, Amazônia, Popularidade e Democracia</strong>.<br>
    Flávio vence em 1 categoria: <strong>Contas Públicas (Dívida e Déficit)</strong>.<br>
    A <strong>Economia</strong> termina empatada (Lula tem PIB maior; Flávio tem inflação e Selic ligeiramente menores).</p>
  </div>

  <table class="score-table">
    <thead>
      <tr>
        <th>Área Avaliada</th>
        <th>Indicador Oficial</th>
        <th style="text-align: right;">Lula</th>
        <th style="text-align: right;">Flávio</th>
        <th style="text-align: right;">Cenário Base</th>
        <th style="text-align: center;">Vencedor</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Economia</strong></td>
        <td>Crescimento do PIB (média anual)</td>
        <td style="text-align: right;"><strong>1,84%</strong></td>
        <td style="text-align: right;">1,67%</td>
        <td style="text-align: right;">1,59%</td>
        <td style="text-align: center;" class="win-tie">Empate Técnico</td>
      </tr>
      <tr>
        <td></td>
        <td>Inflação IPCA (média anual)</td>
        <td style="text-align: right;">3,88%</td>
        <td style="text-align: right;"><strong>3,80%</strong></td>
        <td style="text-align: right;">3,86%</td>
        <td style="text-align: center;" class="win-tie">(Dentro da margem)</td>
      </tr>
      <tr>
        <td></td>
        <td>Taxa Selic (média anual)</td>
        <td style="text-align: right;">11,85%</td>
        <td style="text-align: right;"><strong>11,59%</strong></td>
        <td style="text-align: right;">11,68%</td>
        <td style="text-align: center;" class="win-tie"></td>
      </tr>
      <tr>
        <td><strong>Trabalho</strong></td>
        <td>Desemprego (fim de 2030)</td>
        <td style="text-align: right;"><strong>5,51%</strong></td>
        <td style="text-align: right;">5,87%</td>
        <td style="text-align: right;">6,05%</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td><strong>Contas Públicas</strong></td>
        <td>Dívida Pública Bruta (% do PIB)</td>
        <td style="text-align: right;">103,3%</td>
        <td style="text-align: right;"><strong>102,0%</strong></td>
        <td style="text-align: right;">104,0%</td>
        <td style="text-align: center;" class="win-flavio">🎯 Flávio</td>
      </tr>
      <tr>
        <td></td>
        <td>Resultado Primário (% do PIB)</td>
        <td style="text-align: right;">-0,39%</td>
        <td style="text-align: right;"><strong>0,00%</strong></td>
        <td style="text-align: right;">-0,38%</td>
        <td style="text-align: center;" class="win-flavio">🎯 Flávio</td>
      </tr>
      <tr>
        <td><strong>Social</strong></td>
        <td>Taxa de Pobreza (% da população)</td>
        <td style="text-align: right;"><strong>22,75%</strong></td>
        <td style="text-align: right;">23,27%</td>
        <td style="text-align: right;">23,29%</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td></td>
        <td>Desigualdade de Renda (Índice de Gini)</td>
        <td style="text-align: right;"><strong>0,499</strong></td>
        <td style="text-align: right;">0,503</td>
        <td style="text-align: right;">0,501</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td><strong>Saúde</strong></td>
        <td>Fome / Insegurança alimentar severa</td>
        <td style="text-align: right;"><strong>2,31%</strong></td>
        <td style="text-align: right;">2,48%</td>
        <td style="text-align: right;">2,48%</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td></td>
        <td>Mortalidade Infantil (por mil nascidos)</td>
        <td style="text-align: right;"><strong>11,02</strong></td>
        <td style="text-align: right;">12,01</td>
        <td style="text-align: right;">11,59</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td><strong>Segurança</strong></td>
        <td>Homicídios (por 100 mil hab.)</td>
        <td style="text-align: right;"><strong>16,88</strong></td>
        <td style="text-align: right;">18,42</td>
        <td style="text-align: right;">19,31</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td><strong>Meio Ambiente</strong></td>
        <td>Desmatamento Amazônia (km²/ano)</td>
        <td style="text-align: right;"><strong>3.940</strong></td>
        <td style="text-align: right;">5.367</td>
        <td style="text-align: right;">5.814</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td><strong>Sociedade</strong></td>
        <td>Aprovação popular média (cidadãos IA)</td>
        <td style="text-align: right;"><strong>45,4%</strong></td>
        <td style="text-align: right;">42,6%</td>
        <td style="text-align: right;">35,4%</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td><strong>Democracia</strong></td>
        <td>Estabilidade Institucional (0 a 100)</td>
        <td style="text-align: right;"><strong>69,8</strong></td>
        <td style="text-align: right;">60,6</td>
        <td style="text-align: right;">69,8</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
      <tr>
        <td></td>
        <td>Risco Democrático (0 a 100 — menor melhor)</td>
        <td style="text-align: right;"><strong>22,9</strong></td>
        <td style="text-align: right;">35,9</td>
        <td style="text-align: right;">22,1</td>
        <td style="text-align: center;" class="win-lula">🏆 Lula</td>
      </tr>
    </tbody>
  </table>

  <h3>O Teste das 18 Variações de Realidade (Sensibilidade)</h3>
  <p>Algum crítico poderia dizer: <em>"Ah, mas vocês calibraram o modelo para favorecer as teses de esquerda!"</em></p>
  <p>Para responder a isso com rigor científico, o código foi reexecutado sob <strong>18 combinações diferentes de teorias econômicas</strong>:</p>
  <ul>
    <li>Testou-se corte de gastos que quase não freia a economia (multiplicador de apenas R$ 0,10 por R$ 1 cortado);</li>
    <li>Testou-se corte de impostos onde os empresários repassam 100% do desconto para o preço final das lojas;</li>
    <li>Testou-se o impacto da desregulamentação e do "ambiente de negócios" no seu nível máximo de força.</li>
  </ul>
  <p><strong>O Veredito dos Testes: Lula venceu em 100% das 18 variações (18 a 0).</strong></p>
  <p>Mesmo no cenário dos sonhos da teoria liberal, a retirada massiva de renda de milhões de aposentados e beneficiários do BPC destruiu tanto o consumo popular que o plano de Flávio nunca conseguiu superar o desempenho social e humano do plano de Lula.</p>

  <div class="pagebreak"></div>

  <h2>5. Conclusão: O Que os Dois Projetos Realmente Significam</h2>
  <p>No final das contas, este experimento de inteligência artificial traduziu o debate eleitoral em uma verdade econômica incontornável: <strong>não existe almoço grátis em economia</strong>.</p>

  <div class="box">
    <div class="box-title">🎯 O Projeto de Flávio Bolsonaro (Austeridade e Mercado)</div>
    <p><strong>A Entrega:</strong> Cumpre com louvor o que promete aos investidores da Faria Lima. Zera o déficit primário, contém o endividamento do Estado e dá um alívio modesto nos juros e na inflação.</p>
    <p><strong>A Conta Paga:</strong> Para conseguir economizar R$ 190 bilhões, o governo é obrigado a arrochar as aposentadorias básicas, o BPC e a limitar as verbas de saúde e educação à inflação passada. O resultado são hospitais mais cheios, mortalidade de crianças mais alta, mais fome e aumento da pobreza.</p>
  </div>

  <div class="box">
    <div class="box-title">🏆 O Projeto de Lula (Demanda Interna e Rede Social)</div>
    <p><strong>A Entrega:</strong> Sustenta o motor da economia pela base da pirâmide. O ganho real do salário mínimo, os pisos da saúde e a fiscalização ativa da Amazônia geram menor desemprego, menos fome, menos miséria, preservação de florestas e estabilidade institucional com os tribunais.</p>
    <p><strong>A Conta Paga:</strong> A dívida pública encerra o período ligeiramente mais elevada (103,3% do PIB) e a economia aquecida obriga o Banco Central a manter a taxa Selic em patamar médio mais alto (11,85% vs 11,59%) para evitar que a inflação fuja da meta.</p>
  </div>

  <hr style="border: 0; border-top: 1px solid #cbd5e1; margin: 24px 0 16px;">
  <p style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 8.5pt; color: #64748b; text-align: center;">
    <strong>Projeto brazil-sim</strong> · Artigo científico, código-fonte e simulação abertos em: <a href="https://github.com/CaiqueCoelho/brazil-ai-simulation" style="color: #0284c7; text-decoration: none;">github.com/CaiqueCoelho/brazil-ai-simulation</a><br>
    Executado com IA (Claude e DeepSeek) sobre dados oficiais do BCB, IBGE, INPE, Ipea e TSE.
  </p>

</body>
</html>
"""

html_file.write_text(html_content, encoding="utf-8")
print(f"Wrote HTML to {html_file}")

with tempfile.TemporaryDirectory() as profile:
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--user-data-dir={profile}",
        f"--print-to-pdf={pdf_file}",
        html_file.as_uri()
    ]
    subprocess.run(cmd, check=True)

print(f"Generated PDF successfully: {pdf_file}")
print(f"PDF exists: {pdf_file.exists()}, Size: {pdf_file.stat().st_size} bytes")
