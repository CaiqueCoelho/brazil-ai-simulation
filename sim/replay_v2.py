"""Replays the recorded agent decisions of a run through the current (v2) engine into a sibling '<run>-e2' directory."""

import argparse
import json
from pathlib import Path

from sim.engine import Params
from sim.sensitivity import replay_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--suffix", default="-e2")
    parser.add_argument("--engine", default="v2 (refit with transfers channel and structural unemployment trend; agent decisions replayed)")
    args = parser.parse_args()
    run_dir = args.run_dir
    results = json.loads((run_dir / "results.json").read_text())
    replayed = replay_all(results, Params.load())
    replayed["engine"] = args.engine
    out = run_dir.with_name(run_dir.name + args.suffix)
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(replayed, ensure_ascii=False, indent=1))
    print(out / "results.json")
