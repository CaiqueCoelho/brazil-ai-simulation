import argparse
import json
import statistics
from pathlib import Path

from sim.metrics_pt import METRICS

CONTENDERS = ("lula", "flavio")
TIE_FRACTION = 0.5


def complete_runs(data: dict) -> list[dict]:
    return [r for r in data["runs"] if all(s["completed"] for s in r["scenarios"])]


def final_values(runs: list[dict], scenario: str, key: str) -> list[float]:
    return [next(s for s in r["scenarios"] if s["scenario"] == scenario)["history"][-1]["metrics"][key] for r in runs]


def average_over_term(runs: list[dict], scenario: str, key: str) -> list[float]:
    out = []
    for r in runs:
        history = next(s for s in r["scenarios"] if s["scenario"] == scenario)["history"][1:]
        out.append(statistics.fmean(h["metrics"][key] for h in history))
    return out


def score(metric: dict, value: float) -> float:
    """Higher is better, so every metric can be compared the same way."""
    if metric["better"] == "higher":
        return value
    if metric["better"] == "lower":
        return -value
    return -abs(value - metric["target"])


def compare(data: dict) -> dict:
    """A side wins a metric only if its seed-average lead is larger than half the typical seed-to-seed spread; otherwise it is a tie."""
    runs = complete_runs(data)
    names = {s["scenario"]: s["candidate"] for s in runs[0]["scenarios"]}
    rows = []
    tally = {c: 0 for c in CONTENDERS} | {"empate": 0}
    for m in METRICS:
        # Flows (growth, inflation, approval...) are judged over the whole term; stocks (debt, poverty...) at the end of it.
        use_term_average = m["key"] in ("gdp_growth", "inflation", "approval", "primary_balance", "selic")
        pick = average_over_term if use_term_average else final_values
        per = {s: pick(runs, s, m["key"]) for s in names}
        means = {s: statistics.fmean(v) for s, v in per.items()}
        spreads = {s: (max(v) - min(v)) for s, v in per.items()}
        row = {
            "key": m["key"], "label": m["label"], "unit": m["unit"], "dec": m["dec"], "group": m["group"],
            "basis": "média 2027-2030" if use_term_average else "fim de 2030",
            "mean": {s: round(v, 4) for s, v in means.items()},
            "min": {s: round(min(v), 4) for s, v in per.items()},
            "max": {s: round(max(v), 4) for s, v in per.items()},
        }
        if m["better"] is None:
            row["winner"] = None
        else:
            a, b = CONTENDERS
            gap = abs(score(m, means[a]) - score(m, means[b]))
            noise = TIE_FRACTION * statistics.fmean([spreads[a], spreads[b]])
            if gap <= noise:
                row["winner"] = "empate"
            else:
                row["winner"] = a if score(m, means[a]) > score(m, means[b]) else b
            tally[row["winner"]] += 1
            if "baseline" in means:
                row["vs_baseline"] = {c: score(m, means[c]) > score(m, means["baseline"]) for c in CONTENDERS}
        rows.append(row)
    overall = max(CONTENDERS, key=lambda c: tally[c])
    if tally[CONTENDERS[0]] == tally[CONTENDERS[1]]:
        overall = "empate"
    return {
        "names": names,
        "seeds": [r["seed"] for r in runs],
        "metrics": rows,
        "tally": tally,
        "overall": overall,
        "rule": f"Vence quem tem vantagem maior que {TIE_FRACTION:.0%} da variação média entre seeds; caso contrário, empate.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    result = compare(json.loads(parser.parse_args().results.read_text()))
    out = parser.parse_args().results.with_name("analysis.json")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    for row in result["metrics"]:
        print(f"{row['label']:28} {row['basis']:16} " + "  ".join(f"{s}={row['mean'][s]:.{row['dec']}f}" for s in row["mean"]) + f"  -> {row['winner']}")
    print("placar:", result["tally"], "geral:", result["overall"])
    print(f"written {out}")
