import argparse
import json
import statistics
from pathlib import Path

from sim.metrics_pt import METRICS, item_of

CONTENDERS = ("lula", "flavio")
# Official tolerance bands: the arcabouço counts a primary-balance target as met within ±0.25 pp of GDP; the inflation target band is ±1.5 pp.
TOLERANCE = {"primary_balance": 0.25, "inflation": 1.5}


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


def item_winners(rows: list[dict]) -> dict[str, str]:
    """Indicators that measure the same thing form one item, won by whoever wins more of them; equal counts are a tie."""
    per: dict[str, list[str]] = {}
    for row in rows:
        if row["winner"] is not None:
            per.setdefault(row["item"], []).append(row["winner"])
    out = {}
    for item, winners in per.items():
        a, b = (winners.count(c) for c in CONTENDERS)
        out[item] = CONTENDERS[0] if a > b else CONTENDERS[1] if b > a else "empate"
    return out


def paired_winner(metric: dict, lula: list[float], flavio: list[float]) -> tuple[str, dict[str, int]]:
    """Each seed shares shocks and noise across scenarios, so seeds are compared in pairs: a side wins if it is better on average, beyond any official tolerance, and in most seeds."""
    diffs = [score(metric, x) - score(metric, y) for x, y in zip(lula, flavio)]
    better = {"lula": sum(d > 0 for d in diffs), "flavio": sum(d < 0 for d in diffs)}
    mean = statistics.fmean(diffs)
    if abs(mean) < TOLERANCE.get(metric["key"], 0.0):
        return "empate", better
    if mean > 0 and better["lula"] > len(diffs) / 2:
        return "lula", better
    if mean < 0 and better["flavio"] > len(diffs) / 2:
        return "flavio", better
    return "empate", better


def compare(data: dict) -> dict:
    """Paired by seed: a side wins a metric if it is better on average and in most seeds (see paired_winner)."""
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
        row = {
            "key": m["key"], "label": m["label"], "unit": m["unit"], "dec": m["dec"], "group": m["group"], "item": item_of(m["key"]),
            "basis": "média 2027-2030" if use_term_average else "fim de 2030",
            "mean": {s: round(v, 4) for s, v in means.items()},
            "min": {s: round(min(v), 4) for s, v in per.items()},
            "max": {s: round(max(v), 4) for s, v in per.items()},
        }
        if m["better"] is None:
            row["winner"] = None
        else:
            a, b = CONTENDERS
            row["winner"], row["seeds_better"] = paired_winner(m, per[a], per[b])
            if "baseline" in means:
                row["vs_baseline"] = {c: score(m, means[c]) > score(m, means["baseline"]) for c in CONTENDERS}
        rows.append(row)
    items = item_winners(rows)
    for winner in items.values():
        tally[winner] += 1
    overall = max(CONTENDERS, key=lambda c: tally[c])
    if tally[CONTENDERS[0]] == tally[CONTENDERS[1]]:
        overall = "empate"
    return {
        "names": names,
        "seeds": [r["seed"] for r in runs],
        "metrics": rows,
        "items": items,
        "tally": tally,
        "overall": overall,
        "rule": "Vence quem é melhor na média e na maioria das simulações, comparadas uma a uma (mesmos choques para os dois); diferenças menores que a tolerância oficial (resultado primário ±0,25 ponto do PIB, inflação ±1,5 ponto) são empate. Indicadores que medem a mesma coisa contam uma vez só.",
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
