from sim.analysis import item_winners
from sim.metrics_pt import item_of


def rows(winners: dict) -> list[dict]:
    return [{"item": item_of(k), "winner": w} for k, w in winners.items()]


def test_indicators_of_the_same_item_count_once():
    items = item_winners(rows({"gdp_growth": "flavio", "inflation": "flavio", "selic": "flavio", "gini": "lula"}))
    assert items == {"Economia": "flavio", "Desigualdade (Gini)": "lula"}


def test_item_with_split_indicators_is_a_tie():
    items = item_winners(rows({"debt_gdp": "flavio", "primary_balance": "lula"}))
    assert items == {"Contas públicas": "empate"}


def test_paired_rule_needs_the_average_and_most_seeds():
    from sim.analysis import paired_winner
    from sim.metrics_pt import BY_KEY
    m = BY_KEY["homicides_per_100k"]
    assert paired_winner(m, [16, 17, 15], [17, 18, 16])[0] == "lula"
    assert paired_winner(m, [16, 19, 15], [17, 18, 16])[0] == "lula"
    assert paired_winner(m, [16, 16.5, 25], [17, 17, 18])[0] == "empate"


def test_gap_inside_the_official_tolerance_is_a_tie():
    from sim.analysis import paired_winner
    from sim.metrics_pt import BY_KEY
    m = BY_KEY["primary_balance"]
    assert paired_winner(m, [-0.5, -0.5], [-0.3, -0.3])[0] == "empate"
    assert paired_winner(m, [-0.9, -0.9], [-0.3, -0.3])[0] == "flavio"
