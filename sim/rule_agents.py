"""Replaces the market and central-bank agents with fixed rules (data/engine_v8_rules.json) and replays the other recorded decisions at zero cost."""

import argparse
import json
from pathlib import Path

from sim.analysis import compare
from sim.engine import INFLATION_TARGET, Metrics, Params
from sim.sensitivity import replay_all

RULES_FILE = Path(__file__).resolve().parent.parent / "data" / "engine_v8_rules.json"


def load_rules(path: Path = RULES_FILE) -> dict:
    raw = json.loads(path.read_text())
    return {"taylor": raw["central_bank"]["coefficients"], "market": raw["market"]["coefficients"],
            "consolidation": raw.get("consolidation_effect")}


def rule_params(rules: dict, params: Params) -> Params:
    """With the consolidation rule on, the fiscal multiplier is the net effect measured after market reactions."""
    return params.with_(fiscal_multiplier=rules["consolidation"]["fiscal_multiplier"]) if rules.get("consolidation") else params


def central_bank(m: Metrics, params: Params, taylor: dict) -> float:
    target = (params.neutral_real_rate + m.inflation
              + taylor["inflation"] * (m.inflation - INFLATION_TARGET)
              + taylor["output_gap"] * (m.gdp_growth - params.trend_growth))
    move = round(taylor["speed"] * (target - m.selic) / taylor["step"]) * taylor["step"]
    return max(-taylor["max_move"], min(taylor["max_move"], move))


def market(history: list[Metrics], start: Metrics, params: Params, w: dict, fiscal: bool = True) -> float:
    """Zero means as confident as at the end of 2026; the debt term uses the change over the last four quarters."""
    m = history[-1]
    debt_change = m.debt_gdp - history[max(0, len(history) - 5)].debt_gdp
    score = (w["inflation_gap"] * (abs(m.inflation - INFLATION_TARGET) - abs(start.inflation - INFLATION_TARGET))
             + w["output_gap"] * (m.gdp_growth - params.trend_growth)
             + w["stability"] * (m.institutional_stability - start.institutional_stability))
    if fiscal:
        score += w["primary_balance"] * (m.primary_balance - start.primary_balance) + w["debt_change"] * debt_change
    return max(-1.0, min(1.0, score))


def rule_inputs(rules: dict, params: Params):
    def override(history: list[Metrics]) -> dict:
        out = {"selic_change": central_bank(history[-1], params, rules["taylor"]),
               "market_confidence": market(history, history[0], params, rules["market"])}
        if rules.get("consolidation"):
            out["growth_market_confidence"] = market(history, history[0], params, rules["market"], fiscal=False)
        return out
    return override


def summarize(analysis: dict) -> dict:
    return {"tally": analysis["tally"], "overall": analysis["overall"],
            "winners": {m["key"]: m["winner"] for m in analysis["metrics"]},
            "means": {m["key"]: {s: round(v, 2) for s, v in m["mean"].items()} for m in analysis["metrics"]}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    path = parser.parse_args().results
    results = json.loads(path.read_text())
    params, rules = Params.load(), load_rules()
    report = {"main": summarize(compare(replay_all(results, params, override=rule_inputs(rules, params))))}
    print("main", report["main"]["tally"], "->", report["main"]["overall"])
    variants = json.loads(RULES_FILE.read_text())["sensitivity"]
    report["sensitivity"] = []
    for name, scale in variants["market_weights_scale"].items():
        scaled = {**rules, "market": {k: v * scale for k, v in rules["market"].items()}}
        row = {"variant": name, **summarize(compare(replay_all(results, params, override=rule_inputs(scaled, params))))}
        report["sensitivity"].append(row)
        print(name, row["tally"], "->", row["overall"])
    path.with_name("rule_agents.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
