"""Counterfactual replay: gives Lula and Flávio identical market and central-bank reactions (their per-quarter average) to isolate how much of the result comes from those agents."""

import argparse
import copy
import json
from pathlib import Path

from sim.analysis import compare
from sim.engine import Params
from sim.sensitivity import base_params, replay_all

AGENT_INPUTS = ("market_confidence", "selic_change")


def equalize(results: dict, keys: tuple[str, ...], scenarios=("lula", "flavio")) -> dict:
    out = copy.deepcopy(results)
    for run in out["runs"]:
        chosen = [s for s in run["scenarios"] if s["scenario"] in scenarios]
        for t in range(1, len(chosen[0]["history"])):
            for key in keys:
                mean = sum(s["history"][t]["engine_inputs"][key] for s in chosen) / len(chosen)
                for s in chosen:
                    s["history"][t]["engine_inputs"][key] = mean
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    path = parser.parse_args().results
    results = json.loads(path.read_text())
    report = {}
    for label, keys in (("mercado", ("market_confidence",)), ("banco_central", ("selic_change",)), ("ambos", AGENT_INPUTS)):
        analysis = compare(replay_all(equalize(results, keys), base_params(results)))
        report[label] = {"tally": analysis["tally"], "overall": analysis["overall"],
                         "winners": {m["key"]: m["winner"] for m in analysis["metrics"]},
                         "means": {m["key"]: {s: round(v, 2) for s, v in m["mean"].items()} for m in analysis["metrics"]}}
        print(label, analysis["tally"], "->", analysis["overall"])
        print("   ", {k: v for k, v in report[label]["winners"].items() if v not in (None, "empate")})
    path.with_name("decompose.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
