"""Renders article/corpo.html into article/artigo.html, filling {{...}} placeholders from a run directory (results, analysis, sensitivity)."""

import argparse
import json
import re
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path

from sim.metrics_pt import BY_KEY, METRICS
from sim.sensitivity import base_params

ROOT = Path(__file__).resolve().parent.parent
ARTICLE = ROOT / "article"
PDF = ARTICLE / "artigo-ia-governa-brasil.pdf"
CHROME_CANDIDATES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
COLORS = {"lula": "#2a78d6", "flavio": "#eb6834", "baseline": "#1baf7a"}
TIE = "#b5b4ae"
SHORT = {"lula": "Lula", "flavio": "Flávio", "baseline": "Base"}
WINNER_LABEL = {"lula": "Lula", "flavio": "Flávio", "empate": "Empate", None: "—"}
FONT = "-apple-system, 'Helvetica Neue', Arial, sans-serif"


def fmt(value: float, dec: int) -> str:
    text = f"{value:,.{dec}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def complete(results: dict) -> list[dict]:
    return [r for r in results["runs"] if all(s["completed"] for s in r["scenarios"])]


def band(results: dict, scenario: str, key: str) -> tuple[list[float], list[float], list[float]]:
    histories = [next(s for s in r["scenarios"] if s["scenario"] == scenario)["history"] for r in complete(results)]
    ticks = min(len(h) for h in histories)
    cols = [[h[t]["metrics"][key] for h in histories] for t in range(ticks)]
    return [statistics.fmean(c) for c in cols], [min(c) for c in cols], [max(c) for c in cols]


def chart(results: dict, key: str) -> str:
    m = BY_KEY[key]
    W, H, L, R, T, B = 520, 210, 46, 78, 28, 24
    data = {s: band(results, s, key) for s in COLORS}
    values = [v for mean, lo_, hi_ in data.values() for v in lo_ + hi_]
    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.1 or abs(hi) * 0.05 or 1
    lo, hi = lo - pad, hi + pad
    n = len(data["lula"][0]) - 1
    x = lambda t: L + t / n * (W - L - R)  # noqa: E731
    y = lambda v: T + (1 - (v - lo) / (hi - lo)) * (H - T - B)  # noqa: E731
    dec_axis = max(0, m["dec"] - 1) if m["dec"] > 1 else m["dec"]
    parts = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="{m["label"]}">',
             f'<text x="{L}" y="15" class="ct">{m["label"]} <tspan class="cu">{m["unit"]}</tspan></text>']
    for i in range(5):
        v = lo + (hi - lo) * i / 4
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/>'
                     f'<text x="{L - 6}" y="{y(v) + 3.5:.1f}" class="ax" text-anchor="end">{fmt(v, dec_axis)}</text>')
    for t in range(0, n + 1, 4):
        parts.append(f'<text x="{x(t):.1f}" y="{H - 6}" class="ax" text-anchor="middle">{2026 + t // 4}</text>')
    for s, (mean, lo_, hi_) in data.items():
        poly = [f"{x(t):.1f},{y(v):.1f}" for t, v in enumerate(hi_)] + [f"{x(t):.1f},{y(v):.1f}" for t, v in reversed(list(enumerate(lo_)))]
        parts.append(f'<polygon points="{" ".join(poly)}" fill="{COLORS[s]}" fill-opacity="0.10"/>')
    ends = []
    for s, (mean, _, _) in data.items():
        pts = " ".join(f"{x(t):.1f},{y(v):.1f}" for t, v in enumerate(mean))
        dash = ' stroke-dasharray="5 3"' if s == "baseline" else ""
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{COLORS[s]}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        ends.append([y(mean[-1]), s, mean[-1]])
    ends.sort()
    for i in range(1, len(ends)):
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 13)
    for ey, s, v in ends:
        parts.append(f'<circle cx="{x(n):.1f}" cy="{y(data[s][0][-1]):.1f}" r="4" fill="{COLORS[s]}" stroke="#fff" stroke-width="2"/>'
                     f'<text x="{x(n) + 8:.1f}" y="{ey + 4:.1f}" class="lab"><tspan font-weight="700">{SHORT[s]}</tspan> {fmt(v, m["dec"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def hero(analysis: dict) -> str:
    t = analysis["tally"]
    rows = [{"label": item, "winner": w} for item, w in analysis["items"].items()]
    W, H = 680, 150
    parts = [f'<svg viewBox="0 0 {W} {H}" class="hero" role="img" aria-label="Placar final">']
    for x0, who, label in ((0, "lula", "LULA"), (W / 2 + 10, "flavio", "FLÁVIO")):
        parts.append(f'<text x="{x0 + 4}" y="22" font-family="{FONT}" font-size="13" font-weight="700" fill="{COLORS[who]}" letter-spacing="1.5">{label}</text>'
                     f'<text x="{x0}" y="86" font-family="{FONT}" font-size="64" font-weight="800" fill="#1b1b1a">{t[who]}</text>'
                     f'<text x="{x0 + 4 + 40 * len(str(t[who]))}" y="86" font-family="{FONT}" font-size="14" fill="#52514e">{"vitória" if t[who] == 1 else "vitórias"}</text>')
    parts.append(f'<text x="{W}" y="22" text-anchor="end" font-family="{FONT}" font-size="12" fill="#52514e">{t["empate"]} {"empate técnico" if t["empate"] == 1 else "empates técnicos"}</text>')
    gap, bar_w, x = 3, W, 0.0
    seg = (bar_w - gap * (len(rows) - 1)) / len(rows)
    order = sorted(rows, key=lambda r: {"lula": 0, "empate": 1, "flavio": 2}[r["winner"]])
    for r in order:
        color = COLORS.get(r["winner"], TIE)
        parts.append(f'<rect x="{x:.1f}" y="108" width="{seg:.1f}" height="22" rx="4" fill="{color}"><title>{r["label"]}: {WINNER_LABEL[r["winner"]]}</title></rect>')
        x += seg + gap
    parts.append(f'<text x="0" y="146" font-family="{FONT}" font-size="10" fill="#77766f">Cada bloco é um item, contado uma vez ({len(rows)} itens). Azul: Lula · cinza: empate técnico · laranja: Flávio</text>')
    parts.append("</svg>")
    return "".join(parts)


def advantage(analysis: dict) -> str:
    """For each indicator, in how many simulations each candidate did better (same shocks for both)."""
    rows = [r for r in analysis["metrics"] if r["winner"] is not None]
    n = len(analysis["seeds"])
    W, row_h, L, top = 680, 24, 190, 30
    H = top + row_h * len(rows) + 30
    mid = L + (W - L - 20) / 2
    scale = ((W - L - 20) / 2 - 16) / n
    parts = [f'<svg viewBox="0 0 {W} {H}" class="adv" role="img" aria-label="Em quantas simulações cada candidato foi melhor">',
             f'<text x="{mid - 6:.1f}" y="{top - 12}" text-anchor="end" font-family="{FONT}" font-size="11" font-weight="700" fill="{COLORS["flavio"]}">◀ Flávio melhor</text>',
             f'<text x="{mid + 6:.1f}" y="{top - 12}" font-family="{FONT}" font-size="11" font-weight="700" fill="{COLORS["lula"]}">Lula melhor ▶</text>']
    for i, r in enumerate(rows):
        y = top + i * row_h
        lb, fb = r["seeds_better"]["lula"], r["seeds_better"]["flavio"]
        parts.append(f'<text x="{L - 10}" y="{y + 15}" text-anchor="end" font-family="{FONT}" font-size="11" fill="#1b1b1a">{r["label"]}</text>')
        for count, sign, who in ((lb, 1, "lula"), (fb, -1, "flavio")):
            if count:
                color = COLORS[who] if r["winner"] == who else TIE
                x0, x1 = sorted((mid, mid + sign * count * scale))
                parts.append(f'<rect x="{x0:.1f}" y="{y + 4}" width="{x1 - x0:.1f}" height="{row_h - 8}" rx="3" fill="{color}"/>'
                             f'<text x="{mid + sign * (count * scale + 6):.1f}" y="{y + 15}" text-anchor="{"start" if sign > 0 else "end"}" font-family="{FONT}" font-size="10" fill="#52514e">{count}</text>')
    parts.append(f'<line x1="{mid:.1f}" x2="{mid:.1f}" y1="{top - 6}" y2="{top + row_h * len(rows)}" stroke="#77766f" stroke-width="1"/>')
    parts.append(f'<text x="0" y="{H - 8}" font-family="{FONT}" font-size="10" fill="#77766f">Número de simulações (de {n}) em que cada candidato teve o melhor resultado. Colorido: venceu o indicador (melhor na média e na maioria das simulações); cinza: empate.</text>')
    parts.append("</svg>")
    return "".join(parts)


def sensitivity(sens: dict, main: dict) -> str:
    bc, fm, tp = sens["variants"]["growth_business_climate"], sens["variants"]["fiscal_multiplier"], sens["variants"]["tax_cut_passthrough"]
    main_fm = min(fm, key=lambda f: abs(f - main["fiscal_multiplier"]))
    strength = dict(zip(sorted(bc), ("fraco", "médio", "forte")))
    cell, gap, L, top, panel_gap = 74, 6, 112, 78, 28
    panel_w = L + len(bc) * (cell + gap)
    W, H = panel_w * len(tp) + panel_gap * (len(tp) - 1), top + len(fm) * (cell + gap) + 44
    text = lambda x, y, body, size=10, color="#52514e", anchor="start", weight=400: (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{color}">{body}</text>')
    parts = [f'<svg viewBox="0 0 {W} {H}" class="sens" role="img" aria-label="Teste de sensibilidade: placar Lula × Flávio em cada combinação de hipóteses">']
    for p_i, pass_value in enumerate(tp):
        ox = p_i * (panel_w + panel_gap)
        title = f"Corte de imposto chega aos preços ({fmt(pass_value * 100, 0)}% do corte)" if pass_value else "Corte de imposto não chega aos preços"
        parts.append(text(ox, 14, title, 11.5, "#1b1b1a", weight=700))
        parts.append(text(ox + L, 36, "Efeito do ambiente de negócios no PIB →", 9.5, "#77766f"))
        parts.append(text(ox + L - 10, top - 10, "Gasto público ↓", 9.5, "#77766f", "end"))
        for c_i, b in enumerate(bc):
            cx = ox + L + c_i * (cell + gap) + cell / 2
            parts.append(text(cx, 54, strength.get(b, fmt(b, 1)), 10.5, "#1b1b1a", "middle", 700))
            parts.append(text(cx, 66, fmt(b, 1), 9, "#77766f", "middle"))
        for r_i, f in enumerate(fm):
            y = top + r_i * (cell + gap)
            parts.append(text(ox + L - 10, y + cell / 2 - 2, f"R$ {fmt(f, 2)}", 10.5, "#1b1b1a", "end", 700))
            parts.append(text(ox + L - 10, y + cell / 2 + 11, "por R$ 1", 9, "#77766f", "end"))
            for c_i, b in enumerate(bc):
                row = next(r for r in sens["rows"] if r["params"] == {"growth_business_climate": b, "fiscal_multiplier": f, "tax_cut_passthrough": pass_value})
                x = ox + L + c_i * (cell + gap)
                ties = row["tally"]["empate"]
                is_main = b == main["growth_business_climate"] and f == main_fm and pass_value == main["tax_cut_passthrough"]
                parts.append(f'<rect x="{x:.1f}" y="{y}" width="{cell}" height="{cell}" rx="6" fill="{COLORS.get(row["overall"], TIE)}"/>')
                if is_main:
                    parts.append(f'<rect class="main" x="{x - 3:.1f}" y="{y - 3}" width="{cell + 6}" height="{cell + 6}" rx="8" fill="none" stroke="#1b1b1a" stroke-width="2.5"/>')
                parts.append(text(x + cell / 2, y + cell / 2 + 2, f'{row["tally"]["lula"]} × {row["tally"]["flavio"]}', 15, "#fff", "middle", 700))
                if ties:
                    parts.append(text(x + cell / 2, y + cell / 2 + 17, f"{ties} empate" if ties == 1 else f"{ties} empates", 9, "#fff", "middle"))
    parts.append(text(0, H - 24, "Cada quadrado é o placar Lula × Flávio com aquela combinação. Azul: Lula à frente · laranja: Flávio · cinza: empate.", 10, "#77766f"))
    parts.append(text(0, H - 9, f"Contorno preto: hipóteses mais próximas das do resultado principal (gasto público R$ {fmt(main['fiscal_multiplier'], 2)} por R$ 1).", 10, "#77766f"))
    parts.append("</svg>")
    return "".join(parts)


def sensitivity_summary(sens: dict) -> str:
    rows = sens["rows"]
    tallies = {(r["tally"]["lula"], r["tally"]["flavio"], r["tally"]["empate"]) for r in rows}
    if len(tallies) == 1:
        lula, flavio, ties = tallies.pop()
        tie_text = f", com {ties} empate" if ties == 1 else f", com {ties} empates" if ties else ""
        return f"Nas {len(rows)} combinações o placar é o mesmo: Lula {lula} × {flavio} Flávio{tie_text}. Trocar essas hipóteses não muda o resultado."
    o = sens["overall"]
    return f"Lula fica à frente em {o['lula']} das {len(rows)} combinações; Flávio, em {o['flavio']}; há empate em {o['empate']}."


def scoreboard(analysis: dict) -> str:
    rows = []
    metrics = analysis["metrics"]
    for r in metrics:
        cells = "".join(f"<td>{fmt(r['mean'][s], r['dec'])}</td>" for s in ("lula", "flavio", "baseline"))
        group = [x for x in metrics if x["item"] == r["item"]]
        win_cell = ""
        if group[0] is r:
            win = WINNER_LABEL[analysis["items"][r["item"]]]
            cls = {"Lula": "w-lula", "Flávio": "w-flavio"}.get(win, "w-tie")
            note = f"<div class='basis'>{r['item']}: conta 1 vez</div>" if len(group) > 1 else ""
            win_cell = f"<td class='{cls}' rowspan='{len(group)}'>{win}{note}</td>"
        rows.append(f"<tr><td>{r['label']}<div class='basis'>{r['unit']} · {r['basis']}</div></td>{cells}{win_cell}</tr>")
    head = "<tr><th>Indicador</th><th>Lula</th><th>Flávio</th><th>Cenário base</th><th>Vencedor</th></tr>"
    return f"<table class='score'>{head}{''.join(rows)}</table>"


VERSIONS = [
    ("Versão principal: histórico anônimo, mercado e BC por regras fixas", "analysis.json", ()),
    ("Rodada anterior (200 cidadãos), refeita com as premissas atuais e mercado e BC por regras fixas", "../blind-v8/second_review.json", ("regra_v3",)),
]


def versions_table(run_dir: Path) -> str:
    rows = []
    for label, source, keys in VERSIONS:
        data = json.loads((run_dir / source).read_text())
        for key in keys:
            data = data[key]
        t = data["tally"]
        cls, win = ("w-lula", "Lula") if t["lula"] > t["flavio"] else ("w-flavio", "Flávio") if t["flavio"] > t["lula"] else ("w-tie", "Empate")
        rows.append(f"<tr><td>{label}</td><td>{t['lula']} × {t['flavio']}</td><td class='{cls}'>{win}</td></tr>")
    head = "<tr><th>Versão</th><th>Lula × Flávio</th><th>Vencedor</th></tr>"
    return f"<table class='score'>{head}{''.join(rows)}</table>"


def glossary() -> str:
    items = "".join(f"<dt>{m['label']} <span class='cu'>({m['unit']})</span></dt><dd>{m['explain']}</dd>" for m in METRICS)
    return f"<dl class='glossary'>{items}</dl>"


def render(template: str, run_dir: Path, repo: str) -> str:
    results = json.loads((run_dir / "results.json").read_text())
    analysis = json.loads((run_dir / "analysis.json").read_text())
    sens_path = run_dir / "sensitivity.json"
    sens = json.loads(sens_path.read_text()) if sens_path.exists() else None
    dec_path = run_dir / "decompose.json"
    dec = json.loads(dec_path.read_text()) if dec_path.exists() else None
    by_key = {r["key"]: r for r in analysis["metrics"]}

    def replace(match: re.Match) -> str:
        kind, *args = match.group(1).split(":")
        if kind == "chart":
            return chart(results, args[0])
        if kind == "hero":
            return hero(analysis)
        if kind == "advantage":
            return advantage(analysis)
        if kind == "sensitivity":
            main = base_params(results)
            return sensitivity(sens, {k: getattr(main, k) for k in sens["variants"]})
        if kind == "sens_summary":
            return sensitivity_summary(sens)
        if kind == "sens_overall":
            return str(sens["overall"][args[0]])
        if kind == "sens_total":
            return str(len(sens["rows"]))
        if kind == "scoreboard":
            return scoreboard(analysis)
        if kind == "glossary":
            return glossary()
        if kind == "val":
            row = by_key[args[0]]
            return fmt(row["mean"][args[1]], int(args[2]) if len(args) > 2 else row["dec"])
        if kind == "winner":
            return WINNER_LABEL[by_key[args[0]]["winner"]]
        if kind == "better":
            return str(by_key[args[0]]["seeds_better"][args[1]])
        if kind == "citizens":
            return str(results["config"]["citizens"])
        if kind == "tally":
            return str(analysis["tally"][args[0]])
        if kind == "ties":
            n = analysis["tally"]["empate"]
            return f"{n} empate" if n == 1 else f"{n} empates"
        if kind == "versions":
            return versions_table(run_dir)
        if kind == "dec":
            return str(dec[args[0]]["tally"][args[1]])
        if kind == "calls":
            return fmt(results["budget"]["calls"], 0)
        if kind == "seeds":
            return str(len(analysis["seeds"]))
        if kind == "repo":
            return f'<a href="{repo}">{repo.removeprefix("https://")}</a>' if repo.startswith("http") else repo
        raise KeyError(match.group(0))

    return re.sub(r"\{\{([^}]+)\}\}", replace, template)


def find_chrome() -> str:
    for name in CHROME_CANDIDATES:
        found = shutil.which(name) or (name if Path(name).exists() else None)
        if found:
            return found
    raise SystemExit("Chrome not found; install it or print article/artigo.html to PDF by hand.")


def pdf_command(chrome: str, html: Path, pdf: Path, profile: Path) -> list[str]:
    return [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={profile}", f"--print-to-pdf={pdf}", html.as_uri()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--repo", default="[link do repositório no GitHub: a inserir]")
    parser.add_argument("--pdf", action="store_true", help=f"also print the article to {PDF.relative_to(ROOT)} with headless Chrome")
    args = parser.parse_args()
    body = render((ARTICLE / "corpo.html").read_text(), args.run_dir, args.repo)
    shell = (ARTICLE / "modelo.html").read_text()
    html = ARTICLE / "artigo.html"
    html.write_text(shell.replace("{{body}}", body))
    print(html)
    if args.pdf:
        with tempfile.TemporaryDirectory() as profile:
            subprocess.run(pdf_command(find_chrome(), html.resolve(), PDF.resolve(), Path(profile)), check=True, capture_output=True)
        print(PDF)
