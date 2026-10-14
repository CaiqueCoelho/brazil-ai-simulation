import itertools
import json
import math
from pathlib import Path

from sim.engine import PARAMS_FILE, Metrics, Params, TickInputs, World
from sim.shocks import Shock

HISTORY = Path(__file__).resolve().parent.parent / "data" / "history_2018_2026.json"
TRANSFERS = json.loads((HISTORY.parent / "engine_rules.json").read_text())["historical_transfers"]["values_pct_gdp_above_2019"]

GRID = {
    "trend_growth": [2.0, 2.5],
    "neutral_real_rate": [5.0, 6.0, 7.0],
    "infl_persistence": [0.6, 0.7, 0.8],
    "infl_gap": [0.1, 0.2, 0.3],
    "infl_fx": [0.04, 0.08, 0.12],
    "infl_commodity": [0.5, 1.0, 1.5],
    "growth_real_rate": [0.15, 0.25, 0.35],
    "fiscal_multiplier": [0.1, 0.2, 0.35],
    "growth_pandemic": [6.0, 10.0, 14.0],
    "effective_rate_share": [0.8, 0.9, 1.0],
}
BOUNDS = {
    "trend_growth": (1.5, 3.0),
    "neutral_real_rate": (4.0, 8.0),
    "infl_persistence": (0.5, 0.9),
    "infl_gap": (0.05, 0.5),
    "infl_fx": (0.02, 0.2),
    "infl_commodity": (0.0, 2.5),
    "growth_real_rate": (0.1, 0.6),
    "fiscal_multiplier": (0.1, 0.8),
    "growth_pandemic": (4.0, 25.0),
    "effective_rate_share": (0.7, 1.1),
    "okun": (0.02, 0.2),
    "nairu": (5.0, 12.0),
    "nairu_trend": (-0.8, 0.0),
    "growth_transfers": (0.0, 1.5),
}
LOSS_WEIGHTS = {"gdp_growth": 1.0, "inflation": 1.0, "debt_gdp": 0.5, "unemployment": 0.5}
FIT_METRICS = ("gdp_growth", "inflation", "unemployment", "debt_gdp")
WARMUP_QUARTERS = 3


def backtest(params: Params, hist: dict) -> list[dict[str, float]]:
    """Quarter-by-quarter model values, with growth as the 4-quarter average so it is comparable to official year-on-year GDP."""
    world = World(Metrics.from_dict(hist["start"]), [], seed=0, params=params.with_(noise_scale=0.0), start_year=2018.0)
    prev_fx = hist["start"]["brl_usd"]
    growth_window: list[float] = []
    out = []
    for q in hist["quarters"]:
        shock = Shock(commodity=q["commodity"], global_rate=0.0, drought=q["drought"], scandal=False, pandemic=q["pandemic"])
        transfers = TRANSFERS[q["q"][:4]]
        m = world.step(TickInputs(
            shock=shock,
            selic_change=q["selic"] - world.metrics.selic,
            fiscal_adjust=q["spending"] - transfers,
            extra_transfers=transfers,
            amendment_spending=0.0,
            market_confidence=q["confidence"],
            citizen_sentiment=q["confidence"],
            approval=50.0,
            fx_change_override=(q["brl_usd"] / prev_fx - 1) * 100,
        ))
        prev_fx = q["brl_usd"]
        growth_window = (growth_window + [m.gdp_growth])[-4:]
        out.append({
            "q": q["q"],
            "gdp_growth": sum(growth_window) / len(growth_window),
            "inflation": m.inflation,
            "unemployment": m.unemployment,
            "debt_gdp": m.debt_gdp,
        })
    return out


def errors(sim: list[dict], hist: dict) -> dict[str, float]:
    pairs = list(zip(sim, hist["quarters"]))[WARMUP_QUARTERS:]
    return {
        metric: math.sqrt(sum((s[metric] - h["target"][metric]) ** 2 for s, h in pairs) / len(pairs))
        for metric in FIT_METRICS
    }


def score(params: Params, hist: dict) -> float:
    err = errors(backtest(params, hist), hist)
    return sum(w * err[m] for m, w in LOSS_WEIGHTS.items())


def refine(params: Params, current: float, hist: dict, rounds: int = 40) -> tuple[Params, float]:
    """Coordinate search from the grid optimum, kept inside literature-plausible bounds."""
    for _ in range(rounds):
        improved = False
        for name, (lo, hi) in BOUNDS.items():
            step = (hi - lo) / 20
            for delta in (step, -step):
                candidate = params.with_(**{name: min(hi, max(lo, getattr(params, name) + delta))})
                value = score(candidate, hist)
                if value < current - 1e-6:
                    params, current, improved = candidate, value, True
        if not improved:
            break
    return params, current


def calibrate(hist: dict) -> tuple[Params, dict]:
    base = Params()
    best, best_loss = base, score(base, hist)
    keys = list(GRID)
    for combo in itertools.product(*GRID.values()):
        candidate = base.with_(**dict(zip(keys, combo)))
        current = score(candidate, hist)
        if current < best_loss:
            best, best_loss = candidate, current
    best, best_loss = refine(best, best_loss, hist)
    return best, {
        "default_rmse": errors(backtest(base, hist), hist),
        "fitted_rmse": errors(backtest(best, hist), hist),
    }


def main() -> None:
    hist = json.loads(HISTORY.read_text())
    params, report = calibrate(hist)
    fitted = backtest(params, hist)
    print(f"{'quarter':8}" + "".join(f"{m:>22}" for m in FIT_METRICS))
    for s, h in zip(fitted, hist["quarters"]):
        print(f"{s['q']:8}" + "".join(f"{h['target'][m]:>11.2f}{s[m]:>11.2f}" for m in FIT_METRICS))
    print(json.dumps({k: {m: round(v, 2) for m, v in r.items()} for k, r in report.items()}, indent=1))
    PARAMS_FILE.write_text(json.dumps({
        "params": {k: v for k, v in params.__dict__.items() if k != "noise_scale"},
        "fit": {k: {m: round(v, 3) for m, v in r.items()} for k, r in report.items()},
        "fit_window": f"{hist['quarters'][WARMUP_QUARTERS]['q']}..{hist['quarters'][-1]['q']} (quarterly, official BCB/IBGE series)",
        "series": [{"q": s["q"], "model": {m: round(s[m], 2) for m in FIT_METRICS}, "actual": h["target"]}
                   for s, h in zip(fitted, hist["quarters"])],
        "source": "sim/calibrate.py against data/history_2018_2026.json",
    }, indent=1))
    print(f"written {PARAMS_FILE}")


if __name__ == "__main__":
    main()
