import asyncio

import yaml

from sim.engine import Params
from sim.llm import Budget, FakeClient, Prices
from sim.run import ROOT, simulate
from sim.sensitivity import replay


def small_run() -> dict:
    cfg = yaml.safe_load((ROOT / "config" / "scale.yaml").read_text())
    cfg.update(seeds=[7], citizens=5, ticks=6, scenarios=["lula", "flavio"])
    budget = Budget(limit_usd=float("inf"), prices=Prices(0.14, 0.0028, 0.28))
    return asyncio.run(simulate(cfg, FakeClient(budget, 7), log=lambda _: None))


def test_replay_with_calibrated_params_reproduces_the_recorded_run():
    results = small_run()
    for scenario in results["runs"][0]["scenarios"]:
        replayed = replay(scenario, 7, Params.load())
        assert [h["metrics"] for h in replayed] == [h["metrics"] for h in scenario["history"]]


def test_replay_responds_to_changed_assumptions():
    results = small_run()
    flavio = next(s for s in results["runs"][0]["scenarios"] if s["scenario"] == "flavio")
    low = replay(flavio, 7, Params.load().with_(growth_business_climate=0.0))
    high = replay(flavio, 7, Params.load().with_(growth_business_climate=2.0))
    assert low[-1]["metrics"]["gdp_growth"] != high[-1]["metrics"]["gdp_growth"]
