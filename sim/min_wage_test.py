"""What-if test: Flávio freezes the minimum wage's real gains (his plan does not commit to them)."""

import argparse
import json
from pathlib import Path

from sim.analysis import compare
from sim.engine import Params
from sim.sensitivity import base_params, replay_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    path = parser.parse_args().results
    results = json.loads(path.read_text())
    analysis = compare(replay_all(results, base_params(results), {"flavio": {"min_wage_real": -2.5}}))
    out = {"assumption": "Flávio sem ganho real do salário mínimo (min_wage_real = -2,5% ao ano)",
           "tally": analysis["tally"], "overall": analysis["overall"],
           "winners": {m["key"]: m["winner"] for m in analysis["metrics"]},
           "gini": next(m for m in analysis["metrics"] if m["key"] == "gini")["mean"]}
    path.with_name("min_wage_test.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(out["tally"], out["overall"], "gini", {k: round(v, 4) for k, v in out["gini"].items()})
