"""Real-record comparison of each group's latest government, following data/track_record_rules.json exactly."""

import json
import statistics
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = DATA / "bcb"


def monthly(name: str) -> dict[tuple[int, int], float]:
    out = {}
    for row in json.loads((RAW / f"{name}.json").read_text()):
        day, month, year = row["data"].split("/")
        out[(int(year), int(month))] = float(row["valor"])
    return out


def bcb_annual() -> dict[str, dict[int, float]]:
    ipca, selic, unemp, debt, primary = (monthly(n) for n in ("ipca_12m", "selic", "unemployment", "debt_gdp", "primary_deficit_12m"))
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
    tally = {k: sum(1 for r in rows if r["winner"] == k) for k in ("pt", "pl", "empate", "sem dados")}
    return {"rules": rules, "rows": rows, "tally": tally}


def compare_without_rebound() -> dict:
    """Sensitivity flagged before computing: stock changes for 2022 are measured against pandemic 2021, so drop them."""
    rules = json.loads((DATA / "track_record_rules.json").read_text())
    rules["groups"]["pl"]["years"] = [2019]
    flows = {m["key"] for m in rules["metrics"] if m["kind"] == "flow"}
    base, alt = compare(), compare(rules)
    rows = [a if a["key"] not in flows else b for a, b in zip(alt["rows"], base["rows"])]
    tally = {k: sum(1 for r in rows if r["winner"] == k) for k in ("pt", "pl", "empate", "sem dados")}
    return {"rows": rows, "tally": tally}


CONTEXT = {
    "pl": [
        "2020 and 2021 (pandemic years) are not shown.",
        "Favourable: pension reform approved in 2019; Central Bank autonomy law in 2021.",
        "Favourable: homicides fell from 27.8 per 100k in 2018 to 21.7 in 2019 (Atlas da Violencia).",
        "Unfavourable: a 2021 constitutional amendment (PEC dos Precatorios) deferred court-ordered federal payments to later years.",
        "Unfavourable: Brazil re-entered the UN Hunger Map in 2019-2021 (FAO); Amazon deforestation reached 13,038 km2 in 2021 (PRODES).",
    ],
    "pt": [
        "2026 (incomplete year) is not shown.",
        "Favourable: Brazil left the UN Hunger Map again in 2025, undernourishment 2.4% in 2022-2024 (FAO).",
        "Favourable: violent deaths fell 8.2% in 2025 to 19.1 per 100k, the lowest in the series (FBSP).",
        "Unfavourable: the 2023 central-government deficit (R$ 230.5 billion, 2.1% of GDP) was the second largest since 1997; R$ 92.4 billion of it paid court-ordered debts deferred by the previous government.",
        "Unfavourable: gross debt rose from 71.7% to 78.6% of GDP in 2023-2025 and the Selic was raised to 15% in 2025.",
    ],
}
RECORD_LINES = [
    ("gdp_growth", "GDP growth %", 1),
    ("inflation", "IPCA inflation %", 1),
    ("selic", "average Selic %", 1),
    ("unemployment", "unemployment % (Dec)", 1),
    ("debt_gdp", "gross debt % GDP (Dec)", 1),
    ("primary_balance", "primary balance % GDP", 2),
    ("poverty_rate", "poverty % (IBGE)", 1),
    ("homicides_per_100k", "homicides per 100k (Atlas)", 1),
    ("deforestation_km2", "Amazon deforestation km2 (PRODES)", 0),
]


def record_text(group: str) -> str:
    """Same template for both groups: official yearly values plus documented context."""
    track = compare()
    rules = track["rules"]["groups"][group]
    annual = {r["key"]: r["annual"] for r in track["rows"]}
    lines = [f"REAL RECORD OF THE POLITICAL GROUP BEHIND THIS PLATFORM, from its most recent federal government (official data):"]
    for year in rules["years"]:
        parts = [f"{label} {annual[key][str(year)]:.{dec}f}" for key, label, dec in RECORD_LINES if str(year) in annual.get(key, {})]
        lines.append(f"- {year}: " + "; ".join(parts))
    lines += [f"- {c}" for c in CONTEXT[group]]
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
