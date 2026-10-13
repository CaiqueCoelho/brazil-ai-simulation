"""Real-record comparison of each group's latest government, following data/track_record_rules.json exactly."""

import json
import statistics
from pathlib import Path

from sim.metrics_pt import item_of

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = DATA / "bcb"


def monthly(name: str) -> dict[tuple[int, int], float]:
    out = {}
    for row in json.loads((RAW / f"{name}.json").read_text()):
        day, month, year = row["data"].split("/")
        out[(int(year), int(month))] = float(row["valor"])
    return out


def bcb_annual() -> dict[str, dict[int, float]]:
    ipca, selic, unemp, debt, primary = (monthly(n) for n in ("ipca_12m", "selic", "unemployment", "debt_gdp", "primary_central_12m"))
    gdp_q = {}
    for row in json.loads((RAW / "gdp_index.json").read_text()):
        day, month, year = row["data"].split("/")
        gdp_q.setdefault(int(year), []).append(float(row["valor"]))
    years = range(2017, 2026)
    return {
        "gdp_growth": {y: (sum(gdp_q[y]) / sum(gdp_q[y - 1]) - 1) * 100 for y in years if len(gdp_q.get(y, [])) == 4 and len(gdp_q.get(y - 1, [])) == 4},
        "inflation": {y: ipca[(y, 12)] for y in years if (y, 12) in ipca},
        "selic": {y: statistics.fmean(v for (yy, _), v in selic.items() if yy == y) for y in years},
        "unemployment": {y: unemp[(y, 12)] for y in years if (y, 12) in unemp},
        "debt_gdp": {y: debt[(y, 12)] for y in years if (y, 12) in debt},
        "primary_balance": {y: -primary[(y, 12)] for y in years if (y, 12) in primary},
    }


def group_value(series: dict[int, float], years: list[int], kind: str, metric: dict) -> tuple[float | None, list[int]]:
    if kind == "flow":
        used = [y for y in years if y in series]
        if not used:
            return None, []
        if metric["better"] == "target":
            return statistics.fmean(abs(series[y] - metric["target"]) for y in used), used
        return statistics.fmean(series[y] for y in used), used
    used = [y for y in years if y in series and y - 1 in series]
    if not used:
        return None, []
    return statistics.fmean(series[y] - series[y - 1] for y in used), used


def item_tally(rows: list[dict]) -> dict[str, int]:
    """Same single-count rule as the simulations: indicators that measure the same thing form one item."""
    per: dict[str, list[str]] = {}
    for r in rows:
        if r["winner"] != "sem dados":
            per.setdefault(item_of(r["key"]), []).append(r["winner"])
    items = {i: "pt" if w.count("pt") > w.count("pl") else "pl" if w.count("pl") > w.count("pt") else "empate" for i, w in per.items()}
    tally = {k: sum(1 for v in items.values() if v == k) for k in ("pt", "pl", "empate")}
    tally["sem dados"] = sum(1 for r in rows if r["winner"] == "sem dados")
    return tally


def compare(rules: dict | None = None) -> dict:
    rules = rules or json.loads((DATA / "track_record_rules.json").read_text())
    manual = json.loads((DATA / "track_record_data.json").read_text())
    series = bcb_annual() | {k: {int(y): v for y, v in d["values"].items()} for k, d in manual.items() if not k.startswith("_")}
    groups = rules["groups"]
    rows = []
    for m in rules["metrics"]:
        values = {g: group_value(series.get(m["key"], {}), groups[g]["years"], m["kind"], m) for g in groups}
        pl, pt = values["pl"][0], values["pt"][0]
        if pl is None or pt is None:
            winner = "sem dados"
        elif abs(pl - pt) < m["tie_below"]:
            winner = "empate"
        else:
            lower_is_better = m["better"] in ("lower", "target")
            winner = ("pl" if pl < pt else "pt") if lower_is_better else ("pl" if pl > pt else "pt")
        rows.append({
            "key": m["key"], "kind": m["kind"], "better": m["better"],
            "pl": None if pl is None else round(pl, 3), "pt": None if pt is None else round(pt, 3),
            "pl_years": values["pl"][1], "pt_years": values["pt"][1], "winner": winner,
            "annual": {str(y): round(v, 3) for y, v in sorted(series.get(m["key"], {}).items())},
            "rebound_2022": m["kind"] == "stock" and 2022 in values["pl"][1],
        })
    return {"rules": rules, "rows": rows, "tally": item_tally(rows)}


def compare_without_rebound() -> dict:
    """Sensitivity flagged before computing: stock changes for 2022 are measured against pandemic 2021, so drop them."""
    rules = json.loads((DATA / "track_record_rules.json").read_text())
    rules["groups"]["pl"]["years"] = [2019]
    flows = {m["key"] for m in rules["metrics"] if m["kind"] == "flow"}
    base, alt = compare(), compare(rules)
    rows = [a if a["key"] not in flows else b for a, b in zip(alt["rows"], base["rows"])]
    return {"rows": rows, "tally": item_tally(rows)}


# The Selic is set by the autonomous central bank (LC 179/2021), so it is not shown as a government's record.
RECORD_LINES = [
    ("gdp_growth", "GDP growth %", 1),
    ("inflation", "IPCA inflation %", 1),
    ("unemployment", "unemployment % (Dec)", 1),
    ("debt_gdp", "gross debt % GDP (Dec)", 1),
    ("primary_balance", "central-government primary balance % GDP", 2),
    ("poverty_rate", "poverty % (IBGE)", 1),
    ("homicides_per_100k", "homicides per 100k (Atlas)", 1),
    ("deforestation_km2", "Amazon deforestation km2 (PRODES)", 0),
]
RECORD_NOTES = {
    ("primary_balance", 2019): " (about -1.5 excluding one-off revenue)",
    ("primary_balance", 2022): " (about -0.1 excluding one-off revenue; about -0.55 also counting payments deferred to later years)",
    ("primary_balance", 2023): " (about -1.4 excluding one-off spending inherited from earlier years)",
    ("primary_balance", 2024): " (about -0.2 excluding one-off disaster spending)",
}


def record_text(group: str) -> str:
    """Same template for both groups: official yearly values with years and named events anonymised, as names are hidden too."""
    track = compare()
    rules = track["rules"]["groups"][group]
    annual = {r["key"]: r["annual"] for r in track["rows"]}
    lines = ["REAL RECORD OF THE POLITICAL GROUP BEHIND THIS PLATFORM, from its most recent federal government (official data; years and events are anonymised):"]
    for i, year in enumerate(rules["years"], start=1):
        parts = [f"{label} {annual[key][str(year)]:.{dec}f}{RECORD_NOTES.get((key, year), '')}" for key, label, dec in RECORD_LINES if str(year) in annual.get(key, {})]
        lines.append(f"- Year {i}: " + "; ".join(parts))
    lines.append("Use this record as evidence about how this group tends to govern, together with the platform.")
    return "\n".join(lines)


if __name__ == "__main__":
    result = compare()
    result["without_rebound"] = compare_without_rebound()
    for r in result["without_rebound"]["rows"]:
        print(f"  sem rebote: {r['key']:20} PL={r['pl']} {r['pl_years']}  PT={r['pt']}  -> {r['winner']}")
    print("placar sem rebote:", result["without_rebound"]["tally"])
    for r in result["rows"]:
        print(f"{r['key']:20} {r['kind']:5} PL={r['pl']} {r['pl_years']}  PT={r['pt']} {r['pt_years']}  -> {r['winner']}{'  (2022 vs 2021)' if r['rebound_2022'] else ''}")
    print("placar:", result["tally"])
    (DATA.parent / "out" / "track_record.json").write_text(json.dumps(result, ensure_ascii=False, indent=1))
