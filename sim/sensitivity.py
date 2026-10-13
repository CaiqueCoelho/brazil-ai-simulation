"""Replays the recorded agent decisions through the engine under alternative assumptions. Values were fixed before the final run."""

import argparse
import copy
import itertools
import json
from pathlib import Path

from sim.analysis import compare
from sim.engine import Metrics, Params, PolicyState, TickInputs, World, load_policies
from sim.shocks import shock_schedule

DATA = Path(__file__).resolve().parent.parent / "data"

EXPLORATORY = {"fx_market_confidence": [0.0, 1.5, 3.0]}
VARIANTS = {
    "growth_business_climate": [0.3, 0.6, 0.9],
    "fiscal_multiplier": [0.1, 0.4, 0.7],
    "tax_cut_passthrough": [0.3, 0.0],
}


def replay(scenario: dict, seed: int, params: Params, extra_levers: dict | None = None, override=None) -> list[dict]:
    """override(metrics_so_far) returns engine inputs that replace the recorded ones (used to swap agents for fixed rules)."""
    raw = json.loads((DATA / f"policies_{scenario['scenario']}.json").read_text())
    baseline = json.loads((DATA / "baseline_2026q4.json").read_text())
    policies = load_policies(raw)
    if extra_levers:
        policies.append(PolicyState(id="X", title="test assumption", description="", needs_congress=False,
                                    constitutional_amendment=False, stf_risk=False, levers=dict(extra_levers),
                                    status="approved", implemented=1.0))
    world = World(Metrics.from_dict(baseline), policies, seed=seed, params=params)
    shocks = shock_schedule(seed, len(scenario["history"]) - 1)
    history = [{**scenario["history"][0], "metrics": world.metrics.rounded()}]
    seen = [world.metrics]
    for h in scenario["history"][1:]:
        for pid in h["president"]["priorities"]:
            world.push(pid)
        for pid, outcome in h["votes"].items():
            world.congress_vote(pid, outcome)
        for pid in h["suspended"]:
            world.stf_ruling(pid, "suspend")
        inputs = {**h["engine_inputs"], **(override(seen) if override else {})}
        metrics = world.step(TickInputs(shock=shocks[h["tick"] - 1], **inputs))
        seen.append(metrics)
        history.append({**h, "metrics": metrics.rounded(), "engine_inputs": inputs})
    return history


def base_params(results: dict) -> Params:
    """Runs made with the fixed market and central-bank rules use the rules' fiscal multiplier."""
    if results.get("config", {}).get("rule_agents"):
        from sim.rule_agents import load_rules, rule_params

        return rule_params(load_rules(), Params.load())
    return Params.load()


def replay_all(results: dict, params: Params, extra_levers: dict | None = None, override=None) -> dict:
    """extra_levers maps a scenario id to levers applied as an already-implemented assumption (used for what-if tests)."""
    if override is None and results.get("config", {}).get("rule_agents"):
        from sim.rule_agents import load_rules, rule_inputs

        override = rule_inputs(load_rules(), params)
    out = copy.deepcopy(results)
    for run in out["runs"]:
        for scenario in run["scenarios"]:
            if scenario["completed"]:
                scenario["history"] = replay(scenario, run["seed"], params, (extra_levers or {}).get(scenario["scenario"]), override)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    path = parser.parse_args().results
    results = json.loads(path.read_text())
    base = base_params(results)
    rows = []
    for combo in itertools.product(*VARIANTS.values()):
        changes = dict(zip(VARIANTS, combo))
        analysis = compare(replay_all(results, base.with_(**changes)))
        rows.append({"params": changes, "tally": analysis["tally"], "overall": analysis["overall"],
                     "winners": {m["key"]: m["winner"] for m in analysis["metrics"]}})
        print(changes, analysis["tally"], "->", analysis["overall"])
    overall = {k: sum(1 for r in rows if r["overall"] == k) for k in ("lula", "flavio", "empate")}
    print("overall winner across", len(rows), "variants:", overall)
    # Chosen after seeing the main result, so reported separately and labelled exploratory.
    exploratory = []
    for value in EXPLORATORY["fx_market_confidence"]:
        analysis = compare(replay_all(results, base.with_(fx_market_confidence=value)))
        exploratory.append({"fx_market_confidence": value, "tally": analysis["tally"], "overall": analysis["overall"],
                            "winners": {m["key"]: m["winner"] for m in analysis["metrics"]}})
        print("exploratory fx_market_confidence", value, analysis["tally"], "->", analysis["overall"])
    path.with_name("sensitivity.json").write_text(json.dumps({"variants": VARIANTS, "rows": rows, "overall": overall,
                                                               "exploratory": exploratory}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
