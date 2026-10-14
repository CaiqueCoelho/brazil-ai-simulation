"""Anonymised official record of each group's latest federal government, given to the agents as context."""

import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RAW = DATA / "bcb"
# 2020 and 2021 (pandemic) and the unfinished 2026 are left out.
GROUP_YEARS = {"pl": [2019, 2022], "pt": [2023, 2024, 2025]}


def monthly(name: str) -> dict[tuple[int, int], float]:
    out = {}
    for row in json.loads((RAW / f"{name}.json").read_text()):
        day, month, year = row["data"].split("/")
        out[(int(year), int(month))] = float(row["valor"])
    return out


def bcb_annual() -> dict[str, dict[int, float]]:
    ipca, unemp, debt, primary = (monthly(n) for n in ("ipca_12m", "unemployment", "debt_gdp", "primary_central_12m"))
    gdp_q = {}
    for row in json.loads((RAW / "gdp_index.json").read_text()):
        day, month, year = row["data"].split("/")
        gdp_q.setdefault(int(year), []).append(float(row["valor"]))
    years = range(2017, 2026)
    return {
        "gdp_growth": {y: (sum(gdp_q[y]) / sum(gdp_q[y - 1]) - 1) * 100 for y in years if len(gdp_q.get(y, [])) == 4 and len(gdp_q.get(y - 1, [])) == 4},
        "inflation": {y: ipca[(y, 12)] for y in years if (y, 12) in ipca},
        "unemployment": {y: unemp[(y, 12)] for y in years if (y, 12) in unemp},
        "debt_gdp": {y: debt[(y, 12)] for y in years if (y, 12) in debt},
        "primary_balance": {y: -primary[(y, 12)] for y in years if (y, 12) in primary},
    }


def annual_series() -> dict[str, dict[int, float]]:
    manual = json.loads((DATA / "group_history.json").read_text())
    return bcb_annual() | {k: {int(y): v for y, v in d["values"].items()} for k, d in manual.items() if not k.startswith("_")}


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
    annual = {k: {str(y): round(v, 3) for y, v in series.items()} for k, series in annual_series().items()}
    lines = ["REAL RECORD OF THE POLITICAL GROUP BEHIND THIS PLATFORM, from its most recent federal government (official data; years and events are anonymised):"]
    for i, year in enumerate(GROUP_YEARS[group], start=1):
        parts = [f"{label} {annual[key][str(year)]:.{dec}f}{RECORD_NOTES.get((key, year), '')}" for key, label, dec in RECORD_LINES if str(year) in annual.get(key, {})]
        lines.append(f"- Year {i}: " + "; ".join(parts))
    lines.append("Use this record as evidence about how this group tends to govern, together with the platform.")
    return "\n".join(lines)
