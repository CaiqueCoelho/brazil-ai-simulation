import json
from dataclasses import replace
from pathlib import Path

from sim.engine import Metrics, Params
from sim.rule_agents import central_bank, market

ROOT = Path(__file__).resolve().parent.parent
START = Metrics.from_dict(json.loads((ROOT / "data" / "baseline_2026q4.json").read_text()))
TAYLOR = {"inflation": 1.5, "output_gap": 0.5, "speed": 0.3, "step": 0.25, "max_move": 1.5}
WEIGHTS = {"primary_balance": 0.2, "debt_change": -0.1, "inflation_gap": -0.1, "output_gap": 0.1, "stability": 0.01}


def test_central_bank_hikes_when_inflation_rises_and_respects_the_step():
    params = Params.load()
    calm = central_bank(START, params, TAYLOR)
    hot = central_bank(replace(START, inflation=START.inflation + 3), params, TAYLOR)
    assert hot > calm
    assert hot % 0.25 == 0 and abs(hot) <= 1.5


def test_market_is_neutral_at_the_start_and_reacts_the_same_way_to_any_candidate():
    params = Params.load().with_(trend_growth=START.gdp_growth)
    assert market([START], START, params, WEIGHTS) == 0.0
    worse = replace(START, primary_balance=START.primary_balance - 1, debt_gdp=START.debt_gdp + 3)
    assert market([START, worse], START, params, WEIGHTS) < 0
    unstable = replace(START, institutional_stability=START.institutional_stability - 20)
    assert market([START, unstable], START, params, WEIGHTS) < 0


def test_replay_of_a_rule_based_run_reproduces_it():
    import asyncio

    import yaml

    from sim.llm import Budget, FakeClient, Prices
    from sim.run import simulate
    from sim.sensitivity import base_params, replay_all

    cfg = yaml.safe_load((ROOT / "config" / "blind-v10.yaml").read_text())
    cfg.update(seeds=[7], citizens=5, ticks=6)
    budget = Budget(limit_usd=float("inf"), prices=Prices(0.14, 0.0028, 0.28))
    results = asyncio.run(simulate(cfg, FakeClient(budget, 7), log=lambda _: None))
    replayed = replay_all(results, base_params(results))
    for original, again in zip(results["runs"][0]["scenarios"], replayed["runs"][0]["scenarios"]):
        assert [h["metrics"] for h in again["history"]] == [h["metrics"] for h in original["history"]]
