"""Scores by area instead of by metric, so correlated indicators of one policy (e.g. Selic, debt and primary balance) count once."""

import json
from collections import Counter
from pathlib import Path

from sim.metrics_pt import BY_KEY

TRACK_DOMAINS = {
    "gdp_growth": "Economia", "inflation": "Economia", "selic": "Economia", "unemployment": "Economia",
    "debt_gdp": "Contas públicas", "primary_balance": "Contas públicas",
    "poverty_rate": "Social", "gini": "Social", "infant_mortality": "Saúde",
    "homicides_per_100k": "Segurança", "deforestation_km2": "Meio ambiente",
}


def domain_winners(winners: dict[str, str | None], domain_of) -> dict[str, str]:
    """An area goes to whoever wins more of its decided metrics; equal counts or only ties make it a tie."""
    per = {}
    for key, w in winners.items():
        if w in (None, "sem dados"):
            continue
        per.setdefault(domain_of(key), Counter())[w] += 1
    out = {}
    for domain, c in per.items():
        a, b = c.get("lula", 0) + c.get("pt", 0), c.get("flavio", 0) + c.get("pl", 0)
        out[domain] = "lula" if a > b else "flavio" if b > a else "empate"
    return out


def tally(d: dict[str, str]) -> dict[str, int]:
    return {k: sum(1 for v in d.values() if v == k) for k in ("lula", "flavio", "empate")}


def main(suffix: str = "") -> None:
    out = Path("out")
    sim_domain = lambda k: BY_KEY[k]["group"]  # noqa: E731
    lenses = {}
    for label, path in (("principal", out / f"scale{suffix}" / "analysis.json"), ("informada", out / f"informed{suffix}" / "analysis.json")):
        a = json.loads(path.read_text())
        lenses[label] = domain_winners({m["key"]: m["winner"] for m in a["metrics"]}, sim_domain)
    for label, path in (("principal_mercado_igual", out / f"scale{suffix}" / "decompose.json"), ("informada_mercado_igual", out / f"informed{suffix}" / "decompose.json")):
        lenses[label] = domain_winners(json.loads(path.read_text())["ambos"]["winners"], sim_domain)
    track = json.loads((out / "track_record.json").read_text())
    lenses["historico_sem_rebote"] = domain_winners({r["key"]: r["winner"] for r in track["without_rebound"]["rows"]}, TRACK_DOMAINS.get)
    lenses["historico_regra_original"] = domain_winners({r["key"]: r["winner"] for r in track["rows"]}, TRACK_DOMAINS.get)
    result = {k: {"areas": v, "tally": tally(v)} for k, v in lenses.items()}
    for k, v in result.items():
        print(f"{k:26} {v['tally']}  {v['areas']}")
    (out / f"scale{suffix}" / "domains.json").write_text(json.dumps(result, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else "")
