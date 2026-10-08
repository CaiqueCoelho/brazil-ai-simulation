"""Builds report.html: every chart, table and summary is rendered server-side, so the page reads fully without JavaScript (people, crawlers, LLM agents); JavaScript only adds the replay animation."""

import argparse
import html
import json
import statistics
from pathlib import Path

from sim.metrics_pt import METRICS as METRICS_PT

METRICS = [(m["key"], m["label"], m["unit"], m["dec"], m["explain"]) for m in METRICS_PT]
COLOR_VARS = ["var(--series-1)", "var(--series-2)", "var(--series-3)"]
WINNER_LABEL = {"lula": "Lula", "flavio": "Flávio", "empate": "Empate técnico", None: "Sem vencedor (por definição)"}
W, H, ML, MR, MT, MB = 320, 172, 42, 70, 10, 22


def normalize(data: dict) -> dict:
    """Accepts both the single-run smoke format and the multi-seed format; keeps only seeds where every scenario finished."""
    runs = data.get("runs") or [{"seed": data["config"].get("seed"), "scenarios": data["scenarios"]}]
    complete = [r for r in runs if all(s["completed"] for s in r["scenarios"])] or runs[:1]
    names = [s["scenario"] for s in complete[0]["scenarios"]]
    available = set(complete[0]["scenarios"][0]["history"][0]["metrics"])
    metrics = [m for m in METRICS if m[0] in available]
    series = []
    for i, name in enumerate(names):
        histories = [r["scenarios"][i]["history"] for r in complete]
        ticks = min(len(h) for h in histories)
        stats = {}
        for key, *_ in metrics:
            columns = [[h[t]["metrics"][key] for h in histories] for t in range(ticks)]
            stats[key] = {
                "mean": [round(statistics.fmean(c), 4) for c in columns],
                "lo": [round(min(c), 4) for c in columns],
                "hi": [round(max(c), 4) for c in columns],
            }
        first = complete[0]["scenarios"][i]
        series.append({
            "id": name,
            "name": first["candidate"],
            "short": first["candidate"].split(" ")[0],
            "quarters": [histories[0][t]["quarter"].replace(" Q", " T") for t in range(ticks)],
            "stats": stats,
            "narrative": [{k: v for k, v in h.items() if k not in ("spent_usd", "engine_inputs")} for h in first["history"][:ticks]],
            "narrative_seed": complete[0]["seed"],
            "policies": first.get("policies", []),
        })
    return {
        "metrics": metrics,
        "series": series,
        "seeds": [r["seed"] for r in complete],
        "seeds_total": len(runs),
        "citizens": data["config"]["citizens"],
        "ticks": data["config"]["ticks"],
        "sources": {s["candidate"]: s.get("sources", []) for s in complete[0]["scenarios"]},
    }


def fmt(value: float, dec: int) -> str:
    text = f"{value:,.{dec}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def esc(text) -> str:
    return html.escape(str(text if text is not None else ""))


def scale(data: dict, key: str):
    values = [v for s in data["series"] for v in s["stats"][key]["lo"] + s["stats"][key]["hi"]]
    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.1 or abs(hi) * 0.05 or 1
    lo, hi = lo - pad, hi + pad
    n = max(len(s["quarters"]) for s in data["series"]) - 1
    x = lambda t: ML + t / n * (W - ML - MR)  # noqa: E731
    y = lambda v: MT + (1 - (v - lo) / (hi - lo)) * (H - MT - MB)  # noqa: E731
    return lo, hi, n, x, y


def points(values, x, y) -> str:
    return " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in enumerate(values))


def chart_svg(data: dict, key: str, label: str, dec: int) -> str:
    lo, hi, n, x, y = scale(data, key)
    axis_dec = max(0, dec - 1) if dec > 1 else dec
    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="t-{key} d-{key}" data-metric="{key}" '
             f'data-lo="{lo:.6f}" data-hi="{hi:.6f}" preserveAspectRatio="xMidYMid meet">',
             f'<title id="t-{key}">{esc(label)} por trimestre, 2026 a 2030</title>',
             '<desc id="d-' + key + '">' + esc("; ".join(
                 f"{s['name']}: começa em {fmt(s['stats'][key]['mean'][0], dec)} e termina em {fmt(s['stats'][key]['mean'][-1], dec)} "
                 f"(faixa entre simulações {fmt(s['stats'][key]['lo'][-1], dec)} a {fmt(s['stats'][key]['hi'][-1], dec)})"
                 for s in data["series"])) + '</desc>']
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        parts.append(f'<line class="grid" x1="{ML}" x2="{W - MR}" y1="{y(v):.1f}" y2="{y(v):.1f}"/>'
                     f'<text class="ax" x="{ML - 6}" y="{y(v) + 3.5:.1f}" text-anchor="end">{fmt(v, axis_dec)}</text>')
    for t in range(0, n + 1, 4):
        parts.append(f'<text class="ax" x="{x(t):.1f}" y="{H - 5}" text-anchor="middle">{2026 + t // 4}</text>')
    parts.append(f'<line class="axis" x1="{ML}" x2="{W - MR}" y1="{H - MB}" y2="{H - MB}"/>')
    for i, s in enumerate(data["series"]):
        st = s["stats"][key]
        poly = points(st["hi"], x, y) + " " + " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in reversed(list(enumerate(st["lo"]))))
        parts.append(f'<polygon class="band" points="{poly}" fill="{COLOR_VARS[i]}"/>')
    ends = []
    for i, s in enumerate(data["series"]):
        mean = s["stats"][key]["mean"]
        dash = ' stroke-dasharray="5 3"' if s["id"] == "baseline" else ""
        parts.append(f'<polyline class="ghost" points="{points(mean, x, y)}" stroke="{COLOR_VARS[i]}"{dash}/>'
                     f'<polyline class="line draw" data-series="{i}" pathLength="1" points="{points(mean, x, y)}" stroke="{COLOR_VARS[i]}"/>'
                     f'<circle class="head" data-series="{i}" cx="{x(n):.1f}" cy="{y(mean[-1]):.1f}" r="4" fill="{COLOR_VARS[i]}"/>')
        ends.append([y(mean[-1]), i, s])
    ends.sort(key=lambda e: e[0])
    for j in range(1, len(ends)):
        ends[j][0] = max(ends[j][0], ends[j - 1][0] + 12)
    for ey, i, s in ends:
        parts.append(f'<text class="lab" data-series="{i}" x="{W - MR + 8}" y="{ey + 4:.1f}">{esc(s["short"])}</text>')
    parts.append(f'<line class="scan" x1="{x(n):.1f}" x2="{x(n):.1f}" y1="{MT}" y2="{H - MB}"/>')
    parts.append(f'<rect class="hit" x="{ML}" y="0" width="{W - ML - MR}" height="{H}"/></svg>')
    return "".join(parts)


def analysis_rows(run_dir: Path) -> dict:
    path = run_dir / "analysis.json"
    if not path.exists():
        return {}
    return {m["key"]: m for m in json.loads(path.read_text())["metrics"]}


def summary_table(data: dict, rows_by_key: dict) -> str:
    """Shows each metric on the same basis the winner was decided on: 2027-2030 average for flows, end of 2030 for stocks."""
    head = "".join(f"<th scope='col' title='{esc(s['name'])}'>{esc(s['short'])}</th>" for s in data["series"])
    rows = []
    for key, label, unit, dec, _ in data["metrics"]:
        a = rows_by_key.get(key)
        values = [a["mean"][s["id"]] if a else s["stats"][key]["mean"][-1] for s in data["series"]]
        basis = a["basis"] if a else "fim de 2030"
        cells = "".join(f"<td>{fmt(v, dec)}</td>" for v in values)
        w = f"<td>{esc(WINNER_LABEL.get(a['winner'], '—'))}</td>" if rows_by_key else ""
        rows.append(f"<tr data-metric='{key}'><th scope='row'>{esc(label)}<br><span class='muted'>{esc(unit)} · {esc(basis)}</span></th>{cells}{w}</tr>")
    whead = "<th scope='col'>Vencedor<br><span class='muted'>regra de empate</span></th>" if rows_by_key else ""
    legend = " · ".join(f"{esc(s['short'])} = {esc(s['name'])}" for s in data["series"] if s["short"] != s["name"])
    return (f"<p class='muted'>Médias das {len(data['seeds'])} simulações por cenário ({legend}). Fluxos (crescimento, inflação, juros, resultado primário, aprovação) pela média de 2027 a 2030; estoques pelo fim de 2030.</p>"
            f"<div class='scroll'><table class='summary'>"
            f"<thead><tr><th scope='col'>Indicador</th>{head}{whead}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")


def full_tables(data: dict) -> str:
    out = []
    for s in data["series"]:
        head = "".join(f"<th scope='col'>{esc(m[1])}</th>" for m in data["metrics"])
        body = "".join(
            f"<tr><th scope='row'>{q}</th>" + "".join(f"<td>{fmt(s['stats'][m[0]]['mean'][t], m[3])}</td>" for m in data["metrics"]) + "</tr>"
            for t, q in enumerate(s["quarters"]))
        out.append(f"<h3>{esc(s['name'])}</h3><div class='scroll'><table class='full'><thead><tr><th scope='col'>Trimestre</th>{head}</tr></thead><tbody>{body}</tbody></table></div>")
    return "".join(out)


def feed_html(data: dict, t: int) -> str:
    cards = []
    outcome = {"approve": "aprovado", "amend": "aprovado com mudanças", "reject": "rejeitado"}
    for i, s in enumerate(data["series"]):
        r = s["narrative"][min(t, len(s["narrative"]) - 1)]
        titles = {p["id"]: p.get("title_pt", p["title"]) for p in s["policies"]}
        named = lambda ids: "; ".join(titles.get(x, x) for x in ids) or "nada"  # noqa: E731
        head = f"<h3><i class='sw' style='--c:{COLOR_VARS[i]}'></i>{esc(s['name'])} · <span class='q'>{esc(s['quarters'][min(t, len(s['quarters']) - 1)])}</span></h3>"
        if not r.get("media"):
            cards.append(f"<article class='feed'>{head}<p class='muted'>Ponto de partida.</p></article>")
            continue
        votes = "; ".join(f"{titles.get(k, k)}: {outcome.get(v, v)}" for k, v in r.get("votes", {}).items()) or "nenhuma votação"
        quotes = "".join(f"<li>“{esc(q['quote'])}” <span class='muted'>(aprovação {fmt(q['approval'], 0)})</span></li>" for q in r.get("quotes", [])[:4])
        cards.append(
            f"<article class='feed'>{head}<p class='headline'>“{esc(r['media']['headline'])}”</p>"
            f"<ul class='log'><li><b>contexto</b> <span data-f='shock'>{esc(r['shock'])}</span></li>"
            f"<li><b>presidente</b> <span data-f='pres'>{esc(named(r['president'].get('priorities', [])))}</span></li>"
            f"<li><b>decreto</b> <span data-f='enacted'>{esc(named(r.get('enacted', [])))}</span></li>"
            f"<li><b>congresso</b> <span data-f='votes'>{esc(votes)}</span></li>"
            f"<li><b>stf</b> <span data-f='stf'>suspendeu {esc(named(r.get('suspended', [])))}</span></li>"
            f"<li><b>banco central</b> <span data-f='bc'>Selic {r['central_bank']['selic_change_pp']:+.2f} p.p.: {esc(r['central_bank']['note'])}</span></li>"
            f"<li><b>mercado</b> <span data-f='mkt'>confiança {fmt(r['markets']['confidence'], 2)}: {esc(r['markets']['note'])}</span></li></ul>"
            f"<p class='muted'>Vozes dos cidadãos</p><ul class='quotes'>{quotes}</ul></article>")
    return "".join(cards)


AREAS = ["Economia", "Contas públicas", "Social", "Saúde", "Segurança", "Meio ambiente", "Política", "Democracia"]
AREA_OF = {m["key"]: m["group"] for m in METRICS_PT}
CHIP = {"lula": ("w-l", "Lula"), "flavio": ("w-f", "Flávio"), "empate": ("w-t", "Empate"), None: ("w-t", "—")}


def area_winners(winners: dict) -> dict:
    per = {}
    for key, w in winners.items():
        if w in (None, "sem dados"):
            continue
        per.setdefault(AREA_OF.get(key, "Outros"), []).append(w)
    out = {}
    for area, ws in per.items():
        lula, flavio = ws.count("lula"), ws.count("flavio")
        out[area] = "lula" if lula > flavio else "flavio" if flavio > lula else "empate"
    return out


def who_wins(run_dir: Path, rows_by_key: dict) -> str:
    """Plain-language answer to 'who wins, and when', built from the analysis files next to the report."""
    dec_path = run_dir / "decompose.json"
    if not rows_by_key or not dec_path.exists():
        return ""
    simple = {k: r["winner"] for k, r in rows_by_key.items()}
    equal = json.loads(dec_path.read_text())["ambos"]["winners"]
    count = lambda w: {k: sum(1 for v in w.values() if v == k) for k in ("lula", "flavio", "empate")}  # noqa: E731
    cs, ce = count(simple), count(equal)
    as_, ae = area_winners(simple), area_winners(equal)
    ca, cae = count(as_), count(ae)
    verdict = lambda c: "Lula" if c["lula"] > c["flavio"] else "Flávio" if c["flavio"] > c["lula"] else "Empate"  # noqa: E731
    chip = lambda w: f"<span class='chip {CHIP[w][0]}'>{CHIP[w][1]}</span>"  # noqa: E731
    label_of = {m["key"]: m["label"] for m in METRICS_PT}

    def why(winners: dict, names: dict) -> str:
        lula = [names[k] for k, v in winners.items() if v == "lula"]
        flavio = [names[k] for k, v in winners.items() if v == "flavio"]
        parts = []
        if lula:
            parts.append("Lula vence: " + ", ".join(lula))
        if flavio:
            parts.append("Flávio vence: " + ", ".join(flavio))
        return ". ".join(parts) + "." if parts else "Tudo empatado."

    area_names = {a: a for a in AREAS}
    lens_rows = [
        ("Placar simples (como a simulação rodou)", cs, why(simple, label_of)),
        ("Mercado e Banco Central reagindo igual aos dois", ce, why(equal, label_of)),
        ("Uma vez por área (placar simples)", ca, why(as_, area_names)),
        ("Uma vez por área (mercado e BC iguais)", cae, why(ae, area_names)),
    ]
    rows = "".join(
        f"<tr><th scope='row'>{esc(label)}</th><td><strong>{verdict(c)}</strong> <span class='muted'>Lula {c['lula']} × {c['flavio']} Flávio</span></td><td class='why'>{esc(why)}</td></tr>"
        for label, c, why in lens_rows)
    grid = "".join(f"<tr><th scope='row'>{a}</th><td>{chip(as_.get(a, 'empate'))}</td><td>{chip(ae.get(a, 'empate'))}</td></tr>" for a in AREAS if a in as_ or a in ae)
    always_l = [a for a in AREAS if as_.get(a) == "lula" and ae.get(a) == "lula"]
    always_f = [a for a in AREAS if as_.get(a) == "flavio" and ae.get(a) == "flavio"]
    return (
        "<section aria-labelledby='h-quem' class='who'><h2 id='h-quem'>Quem vence, e quando</h2>"
        "<p class='lead'>Tudo depende de uma pergunta: <strong>como o \"mercado\" de IA reage a cada governo</strong>. "
        + ("Como ele confiou mais no plano de Flávio, Flávio vence o placar simples. " if verdict(cs) == "Flávio"
           else "Mesmo com ele confiando mais no plano de Flávio, o placar simples termina empatado. " if verdict(cs) == "Empate"
           else "Mesmo com ele confiando mais no plano de Flávio, Lula vence o placar simples. ")
        + f"Se ele reage igual aos dois, {verdict(ce)} vence.</p>"
        f"<div class='scroll'><table class='lens'><thead><tr><th scope='col'>Situação</th><th scope='col'>Quem vence</th><th scope='col'>Por quê</th></tr></thead><tbody>{rows}</tbody></table></div>"
        "<h3>Vencedor por área</h3>"
        f"<div class='scroll'><table class='areas'><thead><tr><th scope='col'>Área</th><th scope='col'>Placar simples</th><th scope='col'>Mercado e BC iguais</th></tr></thead><tbody>{grid}</tbody></table></div>"
        f"<p class='always'><span class='chip w-l'>Lula vence sempre</span> {esc(', '.join(always_l) or '—')}"
        f"<br><span class='chip w-f'>Flávio vence sempre</span> {esc(', '.join(always_f) or '—')}</p>"
        "<p class='muted'>\"Mercado e BC iguais\": as mesmas decisões gravadas, mas com a reação média do mercado e do Banco Central aplicada aos dois governos. "
        "\"Por área\": cada área vale um voto, para o ajuste fiscal (Selic, dívida e resultado primário) não contar três vezes.</p></section>")


def json_ld(data: dict, title: str) -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": title,
        "description": "Simulação com agentes de IA de quatro anos (2027-2030) de governo no Brasil sob os planos de Lula e de Flávio Bolsonaro registrados no TSE, mais um cenário base. Não é previsão.",
        "temporalCoverage": "2027/2030",
        "spatialCoverage": "Brasil",
        "variableMeasured": [m[1] for m in data["metrics"]],
        "isAccessibleForFree": True,
        "creator": {"@type": "Organization", "name": "Experimento conduzido por IA (Claude, Anthropic)"},
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": "results.json"}],
    }, ensure_ascii=False)


CSS = """
.viz-root{color-scheme:light;--surface-1:#fcfcfb;--surface-2:#f3f2ef;--text-primary:#0b0b0b;--text-secondary:#52514e;--text-muted:#77766f;--grid:#e4e3df;--axis:#b5b4ae;--series-1:#2a78d6;--series-2:#eb6834;--series-3:#1baf7a;--glow:#2a78d6}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;--surface-1:#1a1a19;--surface-2:#242423;--text-primary:#fff;--text-secondary:#c3c2b7;--text-muted:#9a998f;--grid:#33332f;--axis:#5c5b55;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--glow:#3987e5}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--surface-1:#1a1a19;--surface-2:#242423;--text-primary:#fff;--text-secondary:#c3c2b7;--text-muted:#9a998f;--grid:#33332f;--axis:#5c5b55;--series-1:#3987e5;--series-2:#d95926;--series-3:#199e70;--glow:#3987e5}
*{box-sizing:border-box}body{margin:0}
.viz-root{display:block;background:var(--surface-1);color:var(--text-primary);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;min-height:100vh;padding:clamp(12px,3vw,28px)}
h1{font-size:clamp(20px,3.2vw,28px);margin:0 0 4px;letter-spacing:-.3px}
h2{font-size:18px;margin:32px 0 10px}h3{font-size:14px;margin:12px 0 6px}
a{color:var(--glow)}
.muted{color:var(--text-muted);font-size:12px}.sub{color:var(--text-secondary);margin:0}
.badge{display:inline-flex;align-items:center;gap:6px;font:600 11px/1 ui-monospace,Menlo,monospace;letter-spacing:.8px;text-transform:uppercase;color:var(--glow);border:1px solid var(--axis);border-radius:999px;padding:5px 10px;margin-bottom:10px}
.badge i{width:7px;height:7px;border-radius:50%;background:var(--glow);animation:pulse 2s infinite}
.warn{border-left:3px solid var(--axis);padding:10px 14px;background:var(--surface-2);border-radius:6px;color:var(--text-secondary);margin:14px 0}
.controls{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;margin:16px 0 10px;padding:10px 12px;background:var(--surface-2);border-radius:10px;z-index:3}
@media (min-width:760px){.controls{position:sticky;top:0;box-shadow:0 1px 0 var(--grid)}}
.controls button,.controls select{font:inherit;font-size:14px;color:var(--text-primary);background:var(--surface-1);border:1px solid var(--axis);border-radius:8px;padding:5px 12px;cursor:pointer;min-height:34px}
.controls input[type=range]{flex:1 1 180px;min-width:140px;accent-color:var(--glow)}
#qlabel{font:600 14px ui-monospace,Menlo,monospace;min-width:76px}
.legend{display:flex;gap:6px 14px;flex-wrap:wrap;font-size:13px}.legend span{display:inline-flex;align-items:center;gap:6px}
@media (max-width:759px){.legend{order:5;flex-basis:100%}}
.sw{display:inline-block;width:16px;border-top:2px solid var(--c)}.sw.d{border-top-style:dashed}
.grid-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,290px),1fr));gap:14px}
.card{background:var(--surface-2);border-radius:10px;padding:12px 12px 8px;margin:0;position:relative;overflow:hidden}
.card h3{margin:0;font-size:13.5px}.card .unit{font-weight:400;color:var(--text-muted);font-size:12px}
.card .explain{font-size:12px;color:var(--text-secondary);margin:2px 0 4px}
.card svg{width:100%;height:auto;aspect-ratio:320/172;display:block;overflow:visible;touch-action:pan-y}
.card .now{font:12px/1.4 ui-monospace,Menlo,monospace;color:var(--text-secondary)}
svg .grid{stroke:var(--grid)}svg .axis{stroke:var(--axis)}svg .ax{font-size:9.5px;fill:var(--text-muted)}
svg .lab{font-size:10.5px;fill:var(--text-primary);font-weight:600}
svg .band{fill-opacity:.1}svg .ghost{fill:none;stroke-width:1.5;stroke-opacity:.28}
svg .line{fill:none;stroke-width:2.2;stroke-linejoin:round;stroke-linecap:round}
svg .line.draw{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.6s cubic-bezier(.3,.7,.2,1) .15s forwards}
svg .head{stroke:var(--surface-2);stroke-width:2}
svg .scan{stroke:var(--glow);stroke-width:1;stroke-opacity:0;stroke-dasharray:2 3;transition:stroke-opacity .3s}
.playing svg .scan{stroke-opacity:.6}.playing svg .head{animation:pulse-r 1.2s infinite}
svg .hit{fill:transparent}
.tooltip{position:fixed;pointer-events:none;background:var(--surface-1);color:var(--text-primary);border:1px solid var(--axis);border-radius:8px;padding:7px 9px;font:12px/1.45 ui-monospace,Menlo,monospace;box-shadow:0 6px 18px rgba(0,0,0,.15);display:none;z-index:9;max-width:min(92vw,340px)}
.feeds{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:14px}
.feed{background:var(--surface-2);border-radius:10px;padding:12px}
.feed h3{display:flex;align-items:center;gap:8px;margin:0 0 6px}
.feed .headline{font-weight:650;margin:6px 0 8px;min-height:2.6em}
.feed .headline.typing::after{content:"▍";color:var(--glow);animation:blink .8s steps(1) infinite}
.log{list-style:none;padding:0;margin:0 0 8px;font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--text-secondary)}
.log b{color:var(--glow);font-weight:600;margin-right:6px}.log b::before{content:"› "}
.quotes{margin:4px 0;padding-left:18px;color:var(--text-secondary);font-size:13.5px}
table{border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
th,td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--grid);vertical-align:top}
th:first-child{text-align:left}caption{text-align:left;color:var(--text-secondary);font-size:13px;margin-bottom:6px}
.summary{width:100%}.scroll{overflow-x:auto}
details{margin:8px 0}summary{cursor:pointer;color:var(--text-secondary)}
.who{background:var(--surface-2);border-radius:12px;padding:6px 16px 14px;margin:18px 0}
.who .lead{font-size:16px;margin:4px 0 12px}
.lens{width:100%}.lens td.why{text-align:left;color:var(--text-secondary);font-size:13px;min-width:220px}
.lens th,.lens td{text-align:left}.lens td:nth-child(2){white-space:nowrap}
.areas td{text-align:center}
.chip{display:inline-block;font:600 12px/1 system-ui,sans-serif;padding:4px 9px;border-radius:999px;color:#fff;white-space:nowrap}
.chip.w-l{background:var(--series-1)}.chip.w-f{background:var(--series-2)}.chip.w-t{background:var(--text-muted)}
.always{line-height:2.1;margin:12px 0 6px}
.agent{border:1px dashed var(--axis);border-radius:10px;padding:4px 14px 12px;margin-top:28px;font-size:13.5px;color:var(--text-secondary)}
.agent code{font-size:12px}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(.7)}}
@keyframes pulse-r{0%,100%{r:4}50%{r:6.5}}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion:reduce){svg .line.draw{animation:none;stroke-dashoffset:0}.badge i,.playing svg .head{animation:none}}
"""

JS = r"""
const DATA = JSON.parse(document.getElementById("simulation-data").textContent);
const SERIES = DATA.series, METRICS = DATA.metrics;
const maxT = Math.max(...SERIES.map(s => s.quarters.length - 1));
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const W = 320, H = 172, ML = 42, MR = 70, MT = 10, MB = 22;
const OUTCOME = { approve: "aprovado", amend: "aprovado com mudanças", reject: "rejeitado" };
const fmt = (v, d) => v == null ? "–" : Number(v).toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
const quarterAt = t => SERIES[0].quarters[Math.min(Math.floor(t), SERIES[0].quarters.length - 1)];
const valueAt = (a, t) => { const i = Math.floor(t), f = t - i; return i >= a.length - 1 ? a[a.length - 1] : a[i] + (a[i + 1] - a[i]) * f; };
let current = maxT, raf = null, last = null;

const cards = [...document.querySelectorAll(".card")].map(card => {
  const svg = card.querySelector("svg"), key = svg.dataset.metric, lo = +svg.dataset.lo, hi = +svg.dataset.hi;
  const dec = METRICS.find(m => m[0] === key)[3];
  const x = t => ML + t / maxT * (W - ML - MR), y = v => MT + (1 - (v - lo) / (hi - lo)) * (H - MT - MB);
  return { svg, key, dec, x, y, lines: [...svg.querySelectorAll(".line")], heads: [...svg.querySelectorAll(".head")],
           scan: svg.querySelector(".scan"), now: card.querySelector(".now") };
});

function render(c) {
  SERIES.forEach((s, i) => {
    const m = s.stats[c.key].mean, pts = [];
    for (let t = 0; t <= Math.min(Math.floor(current), m.length - 1); t++) pts.push(`${c.x(t).toFixed(1)},${c.y(m[t]).toFixed(1)}`);
    if (current % 1 > 0 && Math.floor(current) < m.length - 1) pts.push(`${c.x(current).toFixed(1)},${c.y(valueAt(m, current)).toFixed(1)}`);
    c.lines[i].setAttribute("points", pts.join(" "));
    c.heads[i].setAttribute("cx", c.x(current)); c.heads[i].setAttribute("cy", c.y(valueAt(m, current)));
  });
  c.scan.setAttribute("x1", c.x(current)); c.scan.setAttribute("x2", c.x(current));
  c.now.textContent = `${quarterAt(current)} › ` + SERIES.map(s => `${s.short} ${fmt(valueAt(s.stats[c.key].mean, current), c.dec)}`).join(" · ");
}

function titled(s, ids) { return (ids || []).map(id => (s.policies.find(p => p.id === id) || {}).title_pt || id).join("; ") || "nada"; }
function typeInto(el, text) {
  if (REDUCED || !raf) { el.textContent = text; return; }
  el.classList.add("typing"); let k = 0;
  const step = () => { el.textContent = text.slice(0, k += 2); if (k < text.length) setTimeout(step, 14); else el.classList.remove("typing"); };
  step();
}
let lastFeed = null;
function feed() {
  const t = Math.floor(current);
  if (t === lastFeed) return;
  lastFeed = t;
  document.querySelectorAll(".feed").forEach((el, i) => {
    const s = SERIES[i], r = s.narrative[Math.min(t, s.narrative.length - 1)];
    el.querySelector(".q").textContent = quarterAt(t);
    const hl = el.querySelector(".headline");
    if (!hl) return;
    if (!r.media) { hl.textContent = "Ponto de partida: o novo governo ainda não tomou decisões."; el.querySelectorAll("[data-f]").forEach(f => f.textContent = "—"); el.querySelector(".quotes").innerHTML = ""; return; }
    typeInto(hl, `“${r.media.headline}”`);
    const set = (f, v) => { const n = el.querySelector(`[data-f="${f}"]`); if (n) n.textContent = v; };
    set("shock", r.shock);
    set("pres", titled(s, r.president.priorities));
    set("enacted", titled(s, r.enacted));
    set("votes", Object.entries(r.votes || {}).map(([k, v]) => `${titled(s, [k])}: ${OUTCOME[v] || v}`).join("; ") || "nenhuma votação");
    set("stf", `suspendeu ${titled(s, r.suspended)}`);
    set("bc", `Selic ${r.central_bank.selic_change_pp >= 0 ? "+" : ""}${fmt(r.central_bank.selic_change_pp, 2)} p.p.: ${r.central_bank.note}`);
    set("mkt", `confiança ${fmt(r.markets.confidence, 2)}: ${r.markets.note}`);
    const q = el.querySelector(".quotes");
    q.innerHTML = "";
    (r.quotes || []).slice(0, 4).forEach(x => { const li = document.createElement("li"); li.textContent = `“${x.quote}” (aprovação ${fmt(x.approval, 0)})`; q.appendChild(li); });
  });
}

const slider = document.getElementById("slider"), play = document.getElementById("play"), speed = document.getElementById("speed");
slider.max = maxT; slider.value = maxT;
function drawAll() { cards.forEach(render); feed(); document.getElementById("qlabel").textContent = quarterAt(current); slider.value = current; }
function endIntro() { document.querySelectorAll(".line.draw").forEach(l => { l.classList.remove("draw"); l.removeAttribute("pathLength"); }); }
function stop() { cancelAnimationFrame(raf); raf = null; last = null; play.textContent = "▶ Play"; document.body.classList.remove("playing"); }
function frame(ts) {
  if (last != null) current = Math.min(maxT, current + (ts - last) / (+speed.value / 4));
  last = ts; drawAll();
  if (current >= maxT) return stop();
  raf = requestAnimationFrame(frame);
}
play.addEventListener("click", () => {
  if (raf) return stop();
  endIntro();
  if (current >= maxT) current = 0;
  play.textContent = "❚❚ Pause"; document.body.classList.add("playing");
  lastFeed = null;
  raf = requestAnimationFrame(frame);
});
slider.addEventListener("input", () => { endIntro(); current = +slider.value; drawAll(); });
document.getElementById("theme").addEventListener("click", () => {
  const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  r.dataset.theme = dark ? "light" : "dark";
});

const tip = document.getElementById("tip");
cards.forEach(c => {
  c.svg.addEventListener("pointermove", ev => {
    const r = c.svg.getBoundingClientRect(), px = (ev.clientX - r.left) / r.width * W;
    const t = Math.max(0, Math.min(maxT, Math.round((px - ML) / (W - ML - MR) * maxT)));
    tip.innerHTML = "";
    const b = document.createElement("b"); b.textContent = quarterAt(t); tip.appendChild(b);
    SERIES.forEach((s, i) => {
      const st = s.stats[c.key], row = document.createElement("div");
      row.innerHTML = `<span style="color:var(--series-${i + 1})">●</span> `;
      row.append(`${s.name}: ${fmt(st.mean[t], c.dec)} (${fmt(st.lo[t], c.dec)}–${fmt(st.hi[t], c.dec)})`);
      tip.appendChild(row);
    });
    tip.style.display = "block";
    tip.style.left = Math.max(8, Math.min(ev.clientX + 14, innerWidth - tip.offsetWidth - 8)) + "px";
    tip.style.top = ev.clientY + 14 + "px";
  });
  c.svg.addEventListener("pointerleave", () => { tip.style.display = "none"; });
});
"""

TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="alternate" type="application/json" href="results.json" title="Dados brutos da simulação">
<script type="application/ld+json">__JSONLD__</script>
<style>__CSS__</style>
</head>
<body>
<main class="viz-root">
  <div class="badge"><i></i>simulação com agentes de IA</div>
  <h1>Brasil 2027–2030: dois governos simulados por IA</h1>
  <p class="sub">__SUBTITLE__</p>
  <div class="warn">Agentes de IA (modelos de linguagem) tomam as decisões e um modelo de equações calibrado com dados oficiais de 2018 a 2026 (Banco Central/IBGE) transforma essas decisões em números. As linhas mostram a média das simulações repetidas; a faixa sombreada vai da menor à maior. É um experimento, <strong>não uma previsão</strong>.</div>

  __WHO__
  <section aria-labelledby="h-resumo">
    <h2 id="h-resumo">Resumo</h2>
    __SUMMARY__
  </section>

  <div class="controls" role="group" aria-label="Replay da simulação">
    <button id="play" type="button">▶ Play</button>
    <select id="speed" aria-label="Velocidade">
      <option value="60000" selected>1 ano = 1 minuto</option>
      <option value="10000">1 ano = 10 segundos</option>
      <option value="240000">1 ano = 4 minutos</option>
    </select>
    <input id="slider" type="range" min="0" step="0.01" aria-label="Trimestre">
    <span id="qlabel" aria-live="polite">__LASTQ__</span>
    <div class="legend">__LEGEND__</div>
    <button id="theme" type="button" title="Alternar tema" aria-label="Alternar tema">◐</button>
  </div>

  <section aria-labelledby="h-graficos">
    <h2 id="h-graficos">Indicadores trimestre a trimestre</h2>
    <div class="grid-cards">__CARDS__</div>
  </section>

  <section aria-labelledby="h-feed">
    <h2 id="h-feed">O que aconteceu no trimestre <span class="muted">(relato da simulação nº __SEED__)</span></h2>
    <div class="feeds">__FEED__</div>
  </section>

  <section aria-labelledby="h-dados">
    <h2 id="h-dados">Dados completos</h2>
    <details><summary>Tabelas trimestre a trimestre (médias das simulações)</summary>__TABLES__</details>
    <details><summary>Propostas modeladas e fontes</summary>__SOURCES__</details>
  </section>

  <section aria-labelledby="h-agentes" class="agent">
    <h2 id="h-agentes">Para agentes de IA, bots e leitores de tela</h2>
    <p>Todo o conteúdo desta página está no HTML: gráficos em SVG com título e descrição, tabelas com cabeçalhos e o resumo acima. Os dados completos estão no bloco <code>&lt;script type="application/json" id="simulation-data"&gt;</code> (séries por cenário, indicador e trimestre, com média, mínimo e máximo entre simulações) e no arquivo <code>results.json</code> da mesma pasta. Metadados em schema.org/Dataset no cabeçalho. O JavaScript só acrescenta a animação de replay.</p>
  </section>
  <div class="tooltip" id="tip" role="tooltip"></div>
</main>
<script type="application/json" id="simulation-data">__DATA__</script>
<script>__JS__</script>
</body>
</html>
"""


def build(results_path: Path) -> Path:
    data = normalize(json.loads(results_path.read_text()))
    rows_by_key = analysis_rows(results_path.parent)
    win = {k: r["winner"] for k, r in rows_by_key.items()}
    names = " × ".join(s["name"] for s in data["series"])
    title = f"Brasil 2027–2030: simulação com IA ({names})"
    legend = "".join(f"<span><i class='sw{' d' if s['id'] == 'baseline' else ''}' style='--c:{COLOR_VARS[i]}'></i>{esc(s['name'])}</span>"
                     for i, s in enumerate(data["series"]))
    cards = "".join(
        f"<figure class='card' id='m-{key}'><h3>{esc(label)} <span class='unit'>{esc(unit)}</span></h3>"
        f"<p class='explain'>{esc(explain)}</p>{chart_svg(data, key, label, dec)}"
        f"<figcaption class='now'>{esc(data['series'][0]['quarters'][-1])} › "
        + " · ".join(f"{esc(s['short'])} {fmt(s['stats'][key]['mean'][-1], dec)}" for s in data["series"])
        + "</figcaption></figure>"
        for key, label, unit, dec, explain in data["metrics"])
    tally = ""
    if win:
        counts = {k: sum(1 for v in win.values() if v == k) for k in ("lula", "flavio", "empate")}
        tally = (f"<p>Pela regra de empate (vence quem tem vantagem maior que metade da variação entre simulações): "
                 f"<strong>Lula {counts['lula']}</strong>, <strong>Flávio {counts['flavio']}</strong>, <strong>{counts['empate']} empates técnicos</strong>.</p>")
    sources = "".join(
        f"<h3>{esc(s['name'])}</h3><ul>" + "".join(f"<li>{esc(p.get('title_pt', p['title']))}</li>" for p in s["policies"]) + "</ul>"
        + "<p class='muted'>" + " · ".join(f"<a href='{esc(u)}'>{esc(u)}</a>" for u in data["sources"].get(s["name"], [])) + "</p>"
        for s in data["series"])
    subtitle = f"{data['citizens']} cidadãos simulados · {data['ticks']} trimestres · {len(data['seeds'])} de {data['seeds_total']} simulações completas"
    page = (TEMPLATE
            .replace("__TITLE__", esc(title))
            .replace("__DESC__", esc(f"Simulação com agentes de IA do Brasil de 2027 a 2030: {names}. {subtitle}. Indicadores de economia, contas públicas, social, saúde, segurança, meio ambiente e democracia."))
            .replace("__JSONLD__", json_ld(data, title).replace("</", "<\\/"))
            .replace("__CSS__", CSS)
            .replace("__SUBTITLE__", esc(subtitle))
            .replace("__WHO__", who_wins(results_path.parent, rows_by_key))
            .replace("__SUMMARY__", tally + summary_table(data, rows_by_key))
            .replace("__LASTQ__", esc(data["series"][0]["quarters"][-1]))
            .replace("__LEGEND__", legend)
            .replace("__CARDS__", cards)
            .replace("__SEED__", str(data["series"][0]["narrative_seed"]))
            .replace("__FEED__", feed_html(data, data["ticks"]))
            .replace("__TABLES__", full_tables(data))
            .replace("__SOURCES__", sources)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
            .replace("__JS__", JS))
    out = results_path.with_name("report.html")
    out.write_text(page)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    print(build(parser.parse_args().results))
