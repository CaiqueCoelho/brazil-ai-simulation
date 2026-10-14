import itertools

from sim.article import pdf_command, sensitivity, sensitivity_summary

VARIANTS = {"growth_business_climate": [0.3, 0.6, 0.9], "fiscal_multiplier": [0.1, 0.4, 0.7], "tax_cut_passthrough": [0.3, 0.0]}
MAIN = {"growth_business_climate": 0.6, "fiscal_multiplier": 0.43, "tax_cut_passthrough": 0.3}


def sens(tally=lambda params: {"lula": 9, "flavio": 1, "empate": 1}) -> dict:
    rows = []
    for combo in itertools.product(*VARIANTS.values()):
        params = dict(zip(VARIANTS, combo))
        t = tally(params)
        overall = "lula" if t["lula"] > t["flavio"] else "flavio" if t["flavio"] > t["lula"] else "empate"
        rows.append({"params": params, "tally": t, "overall": overall})
    overall = {k: sum(1 for r in rows if r["overall"] == k) for k in ("lula", "flavio", "empate")}
    return {"variants": VARIANTS, "rows": rows, "overall": overall}


def test_chart_explains_each_assumption_in_plain_words():
    svg = sensitivity(sens(), MAIN)
    for label in ("fraco", "médio", "forte", "R$ 0,10", "R$ 0,40", "R$ 0,70", "por R$ 1",
                  "chega aos preços", "não chega aos preços", "Lula × Flávio"):
        assert label in svg


def test_chart_shows_ties_in_each_square():
    assert "1 empate" in sensitivity(sens(), MAIN)


def test_chart_outlines_only_the_square_closest_to_the_main_result():
    svg = sensitivity(sens(), MAIN)
    assert svg.count('class="main"') == 1
    assert "resultado principal" in svg


def test_summary_says_the_score_never_changes_when_every_square_is_equal():
    text = sensitivity_summary(sens())
    assert "Nas 18 combinações o placar é o mesmo" in text
    assert "Lula 9 × 1 Flávio" in text
    assert "1 empate" in text


def test_summary_counts_winners_when_squares_differ():
    flip = lambda p: {"lula": 3, "flavio": 7, "empate": 1} if p["fiscal_multiplier"] == 0.7 else {"lula": 9, "flavio": 1, "empate": 1}
    text = sensitivity_summary(sens(flip))
    assert "Lula fica à frente em 12" in text
    assert "Flávio, em 6" in text


def test_pdf_command_prints_the_article_without_browser_headers(tmp_path):
    html, pdf = tmp_path / "artigo.html", tmp_path / "artigo.pdf"
    cmd = pdf_command("chrome", html, pdf, tmp_path / "profile")
    assert cmd[0] == "chrome"
    assert "--headless=new" in cmd and "--no-pdf-header-footer" in cmd
    assert f"--print-to-pdf={pdf}" in cmd
    assert f"--user-data-dir={tmp_path / 'profile'}" in cmd
    assert cmd[-1] == html.as_uri()
