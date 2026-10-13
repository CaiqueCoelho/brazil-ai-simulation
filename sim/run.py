import argparse
import asyncio
import json
import os
import statistics
import sys
import time
from pathlib import Path

import yaml

from sim.agents import (
    CentralBankDecision,
    CentraoDecision,
    CitizenDecision,
    CongressDecision,
    FinanceDecision,
    MarketsDecision,
    MediaDecision,
    Persona,
    PresidentDecision,
    STFDecision,
    ask,
    citizen_memory,
    fake_for,
    sample_personas,
    situation,
    system_prompt,
)
from sim.engine import Metrics, TickInputs, World, load_policies, tally
from sim.llm import Budget, BudgetExceeded, DeepSeekClient, FakeClient, LLMClient, Prices, ResponseCache
from sim.shocks import shock_schedule

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
QUOTES_PER_TICK = 8
RECORD_GROUP = {"lula": "pt", "flavio": "pl"}
INSTITUTION_ROLES = ("president", "finance", "centrao", "stf", "central_bank", "markets", "media", "citizen")


def quarter_label(tick: int) -> str:
    return f"{2027 + tick // 4} Q{tick % 4 + 1}"


async def run_scenario(name: str, seed: int, cfg: dict, client: LLMClient, personas: list[Persona], log) -> dict:
    raw = json.loads((DATA / f"policies_{name}.json").read_text())
    baseline = json.loads((DATA / "baseline_2026q4.json").read_text())
    world = World(Metrics.from_dict(baseline), load_policies(raw), seed=seed)
    rules = None
    if cfg.get("rule_agents"):
        from sim.rule_agents import load_rules, rule_inputs, rule_params

        rules = load_rules()
        world.params = rule_params(rules, world.params)
        rule_override = rule_inputs(rules, world.params)
        seen = [world.metrics]
    shocks = shock_schedule(seed, cfg["ticks"])
    mt_inst, mt_cit = cfg["max_tokens"]["institution"], cfg["max_tokens"]["citizen"]
    blocs = cfg["congress_blocs"]
    seats = {b["id"]: b["seats"] for b in blocs}
    record = ""
    group = RECORD_GROUP.get(name)
    if cfg.get("track_record") and group:
        from sim.track_record import record_text

        record = record_text(group)
    # The central bank is autonomous by law (LC 179/2021) and decides on current data, not on a party's past.
    systems = {role: system_prompt(world.policies, role, record="" if role == "central_bank" else record) for role in INSTITUTION_ROLES}
    for b in blocs:
        systems[f"bloc:{b['id']}"] = system_prompt(
            world.policies, "bloc", f"YOUR BLOC: {b['name']}, holding {b['seats']:.0%} of the seats.", record=record)
    quote_every = max(1, cfg.get("quote_every", 1))

    news: list[str] = []
    memories: dict[int, str] = {p.id: "" for p in personas}
    history = [{"tick": 0, "quarter": "2026 Q4", "metrics": world.metrics.rounded()}]
    fallbacks = 0
    result = {"scenario": name, "seed": seed, "candidate": raw["candidate"], "plan_title": raw["plan_title"],
              "sources": raw["sources"], "history": history, "completed": False}

    try:
        for t in range(cfg["ticks"]):
            q = quarter_label(t)
            shock = shocks[t]
            sit = situation(world, q, shock.describe(), news)
            public_sit = situation(world, q, shock.describe(), news, hide=("approval",))

            available = [p.id for p in world.policies if world.can_push(p)]
            pres, fb = await ask(client, "president", systems["president"],
                                 f"{sit}\nAVAILABLE TO PUSH NOW: {available}",
                                 PresidentDecision, mt_inst, fake_for("president", world))
            fallbacks += fb
            to_congress, enacted = [], []
            for pid in pres.priorities:
                policy = world.push(pid)
                if policy is not None:
                    (to_congress if policy.status == "pending_vote" else enacted).append(pid)

            after_pres = f"{sit}\nPRESIDENT THIS QUARTER: pushed {pres.priorities}; said: \"{pres.statement}\""
            (fin, fb1), (cen, fb2) = await asyncio.gather(
                ask(client, "finance", systems["finance"], after_pres, FinanceDecision, mt_inst, fake_for("finance", world)),
                ask(client, "centrao", systems["centrao"], after_pres, CentraoDecision, mt_inst, fake_for("centrao", world)),
            )
            fallbacks += fb1 + fb2

            votes: dict[str, str] = {}
            bloc_votes: dict[str, dict[str, str]] = {}
            if to_congress:
                bills = "\n".join(
                    f"- {pid}: {world.policy(pid).title}"
                    + (" [constitutional amendment, needs 3/5]" if world.policy(pid).constitutional_amendment else "")
                    + (f" [attempt {world.policy(pid).attempts}]" if world.policy(pid).attempts > 1 else "")
                    for pid in to_congress)
                bloc_user = (f"{after_pres}\nCENTRÃO STANCE: support {cen.support:.2f}, demands {cen.amendment_demand_pct_gdp:.2f}% "
                             f"of GDP in amendments; \"{cen.note}\"\nBILLS TO VOTE THIS QUARTER:\n{bills}")
                bloc_results = await asyncio.gather(*[
                    ask(client, "bloc", systems[f"bloc:{b['id']}"], bloc_user, CongressDecision, mt_inst,
                        fake_for("bloc", world, pushed=to_congress))
                    for b in blocs
                ])
                for b, (decision, fb) in zip(blocs, bloc_results):
                    fallbacks += fb
                    cast = {v.policy_id: v.outcome for v in decision.votes}
                    bloc_votes[b["id"]] = {pid: cast.get(pid, "reject") for pid in to_congress}
                for pid in to_congress:
                    outcome = tally({b: bloc_votes[b][pid] for b in bloc_votes}, seats, world.policy(pid).constitutional_amendment)
                    world.congress_vote(pid, outcome)
                    votes[pid] = outcome

            challenged = [pid for pid in to_congress + enacted
                          if world.policy(pid).stf_risk and world.policy(pid).status == "approved"]
            suspended = []
            if challenged:
                details = "\n".join(f"- {pid}: {world.policy(pid).title}. {world.policy(pid).description}" for pid in challenged)
                stf, fb = await ask(client, "stf", systems["stf"], f"{sit}\nMEASURES UNDER CHALLENGE:\n{details}",
                                    STFDecision, mt_inst, fake_for("stf", world, challenged=challenged))
                fallbacks += fb
                suspended = [r.policy_id for r in stf.rulings if r.policy_id in challenged and world.stf_ruling(r.policy_id, r.ruling)]

            decisions = (
                f"DECISIONS THIS QUARTER: President pushed {pres.priorities} (\"{pres.statement}\"); "
                f"enacted by decree {enacted}; Congress outcomes {votes}; Supreme Court suspended {suspended}; "
                f"Finance Minister extra fiscal adjustment {fin.fiscal_adjust_pct_gdp:+.2f}% GDP; "
                f"Centrão support {cen.support:.2f}."
            )
            if rules:
                fixed = rule_override(seen)
                bc = CentralBankDecision(selic_change_pp=fixed["selic_change"], note="fixed rule")
                mkt = MarketsDecision(confidence=fixed["market_confidence"], note="fixed rule")
                media, fb3 = await ask(client, "media", systems["media"], f"{public_sit}\n{decisions}", MediaDecision, mt_inst, fake_for("media", world))
                fallbacks += fb3
            else:
                (bc, fb1), (mkt, fb2), (media, fb3) = await asyncio.gather(
                    ask(client, "central_bank", systems["central_bank"], f"{sit}\n{decisions}", CentralBankDecision, mt_inst, fake_for("central_bank", world)),
                    ask(client, "markets", systems["markets"], f"{sit}\n{decisions}", MarketsDecision, mt_inst, fake_for("markets", world)),
                    ask(client, "media", systems["media"], f"{public_sit}\n{decisions}", MediaDecision, mt_inst, fake_for("media", world)),
                )
                fallbacks += fb1 + fb2 + fb3

            # Shared text first and persona last keeps the prompt prefix identical across citizens, which is what DeepSeek's cache keys on.
            shared = f"{public_sit}\n{decisions}\nHEADLINE: {media.headline}\n"

            def citizen_call(p: Persona):
                skip = "" if p.id % quote_every == 0 else '\nSet "quote" to "" this turn.'
                return ask(client, "citizen", systems["citizen"],
                           f"{shared}\nYOU: {p.describe()}\nLAST QUARTER YOU: {memories[p.id] or 'new government, no opinion yet'}{skip}",
                           CitizenDecision, mt_cit, fake_for("citizen", world))

            # DeepSeek only caches a prefix after a request using it completes, so one warm-up call lets the other citizens hit the cache.
            first = await citizen_call(personas[0])
            rest = await asyncio.gather(*[citizen_call(p) for p in personas[1:]])
            citizen_results = [first, *rest]
            fallbacks += sum(fb for _, fb in citizen_results)
            citizens = [c for c, _ in citizen_results]
            for p, c in zip(personas, citizens):
                memories[p.id] = citizen_memory(c)

            curbs = lambda ids: sum(1 for pid in ids if world.policy(pid).levers.get("institutional_conflict", 0) > 0)  # noqa: E731
            inputs = {
                "selic_change": bc.selic_change_pp,
                "fiscal_adjust": fin.fiscal_adjust_pct_gdp,
                "amendment_spending": cen.amendment_demand_pct_gdp * cen.support,
                "market_confidence": mkt.confidence,
                "citizen_sentiment": statistics.fmean(c.econ_sentiment for c in citizens),
                "approval": statistics.fmean(c.approval for c in citizens),
                "stf_suspensions": len(suspended),
                "court_curb_attempts": curbs(to_congress + enacted),
                "court_curb_struck_down": curbs(suspended),
                "approval_sd": statistics.pstdev(c.approval for c in citizens),
            }
            if rules:
                inputs["growth_market_confidence"] = fixed.get("growth_market_confidence")
            metrics = world.step(TickInputs(shock=shock, **inputs))
            if rules:
                seen.append(metrics)
            news.append(f"{q}: {media.headline}")

            concerns: dict[str, int] = {}
            for c in citizens:
                key = c.top_concern.strip().lower() or "n/a"
                concerns[key] = concerns.get(key, 0) + 1
            quoted = [(p, c) for p, c in zip(personas, citizens) if c.quote.strip()]
            history.append({
                "tick": t + 1,
                "quarter": q,
                "metrics": metrics.rounded(),
                "shock": shock.describe(),
                "president": pres.model_dump(),
                "enacted": enacted,
                "votes": votes,
                "bloc_votes": bloc_votes,
                "suspended": suspended,
                "finance": fin.model_dump(),
                "centrao": cen.model_dump(),
                "central_bank": bc.model_dump(),
                "markets": mkt.model_dump(),
                "media": media.model_dump(),
                "top_concerns": dict(sorted(concerns.items(), key=lambda kv: -kv[1])[:5]),
                "quotes": [{"persona": p.describe(), **c.model_dump()}
                           for p, c in quoted[:: max(1, len(quoted) // QUOTES_PER_TICK)]][:QUOTES_PER_TICK],
                "policy_status": {p.id: {"status": p.status, "implemented": p.implemented} for p in world.policies},
                "spent_usd": round(client.budget.spent, 4),
                "engine_inputs": inputs,
            })
            log(f"[seed {seed} {name:>8}] {q}  growth {metrics.gdp_growth:+.1f}%  infl {metrics.inflation:.1f}%  "
                f"approval {metrics.approval:.0f}  spent ${client.budget.spent:.4f}")
        result["completed"] = True
    except BudgetExceeded as exc:
        log(f"[seed {seed} {name:>8}] STOPPED by budget guard: {exc}")
        result["stopped_reason"] = str(exc)

    result["fallbacks"] = fallbacks
    result["policies"] = [{"id": p.id, "title": p.title, "levers": p.levers, "needs_congress": p.needs_congress,
                           "constitutional_amendment": p.constitutional_amendment, "stf_risk": p.stf_risk,
                           "final_status": p.status, "attempts": p.attempts, "title_pt": raw["policies"][i]["title_pt"]}
                          for i, p in enumerate(world.policies)]
    return result


async def simulate(cfg: dict, client: LLMClient, log=print, on_seed=None) -> dict:
    """Seeds run one after another, with all scenarios of a seed in parallel, so a budget stop still leaves complete seeds to compare."""
    shares = json.loads((DATA / "personas_shares.json").read_text())
    started = time.monotonic()
    runs = []
    for seed in cfg["seeds"]:
        personas = sample_personas(shares, cfg["citizens"], seed)
        scenarios = await asyncio.gather(*[run_scenario(s, seed, cfg, client, personas, log) for s in cfg["scenarios"]])
        runs.append({"seed": seed, "scenarios": scenarios})
        if on_seed is not None:
            on_seed({"config": cfg, "elapsed_seconds": round(time.monotonic() - started, 1),
                     "budget": client.budget.summary(), "runs": runs})
        if not all(s["completed"] for s in scenarios):
            break
    return {
        "config": cfg,
        "elapsed_seconds": round(time.monotonic() - started, 1),
        "budget": client.budget.summary(),
        "runs": runs,
    }


def load_config(path: Path, overrides: argparse.Namespace) -> dict:
    cfg = yaml.safe_load(path.read_text())
    if overrides.citizens is not None:
        cfg["citizens"] = overrides.citizens
    if overrides.ticks is not None:
        cfg["ticks"] = overrides.ticks
    if overrides.seeds is not None:
        cfg["seeds"] = cfg["seeds"][: overrides.seeds]
    return cfg


def prices(cfg: dict) -> Prices:
    p = cfg["prices_per_million"]
    return Prices(input=p["input"], cache_hit=p["cache_hit"], output=p["output"])


async def project_cost(cfg: dict) -> dict:
    budget = Budget(limit_usd=float("inf"), prices=prices(cfg))
    return await simulate(cfg, FakeClient(budget, cfg["seeds"][0]), log=lambda _: None)


async def main() -> int:
    parser = argparse.ArgumentParser(description="Brazil 2027-2030 multi-scenario simulation")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "smoke.yaml")
    parser.add_argument("--dry-run", action="store_true", help="fake LLM, $0, prints the cost projection")
    parser.add_argument("--list-models", action="store_true", help="print the model ids available to the API key")
    parser.add_argument("--citizens", type=int)
    parser.add_argument("--ticks", type=int)
    parser.add_argument("--seeds", type=int, help="use only the first N seeds of the config")
    parser.add_argument("--out", type=Path, default=ROOT / "out")
    args = parser.parse_args()
    cfg = load_config(args.config, args)

    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    if args.list_models:
        from openai import OpenAI

        for m in OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url=base_url).models.list():
            print(m.id)
        return 0

    projection = await project_cost(cfg)
    worst = projection["budget"]["spent_usd"]
    expected = worst * cfg["expected_cost_ratio"]
    print(f"Worst case (no cache hits, every reply at max length): ${worst:.2f} "
          f"({projection['budget']['calls']:,} calls)")
    print(f"Expected (worst x {cfg['expected_cost_ratio']} measured ratio): ${expected:.2f}   "
          f"preflight cap ${cfg['preflight_max_usd']:.2f}   hard budget ${cfg['budget_usd']:.2f}")

    name = args.config.stem
    out_dir = args.out / (f"dry-run-{name}" if args.dry_run else name)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        (out_dir / "results.json").write_text(json.dumps(projection, ensure_ascii=False, indent=1))
        print(f"Dry run written to {out_dir / 'results.json'}")
        return 0

    if expected > cfg["preflight_max_usd"]:
        print(f"Refusing to start: expected ${expected:.2f} exceeds preflight cap ${cfg['preflight_max_usd']:.2f}")
        return 2
    model = os.getenv("DEEPSEEK_MODEL")
    if not os.getenv("DEEPSEEK_API_KEY") or not model:
        print("Set DEEPSEEK_API_KEY and DEEPSEEK_MODEL in .env (use --list-models to find the model id).")
        return 2

    budget = Budget(limit_usd=cfg["budget_usd"], prices=prices(cfg))
    client = DeepSeekClient(budget, ResponseCache(out_dir / "cache.sqlite"), os.environ["DEEPSEEK_API_KEY"],
                            model, base_url, cfg["concurrency"], cfg["temperature"])
    def save(partial: dict) -> None:
        partial.update(model=model, projected_worst_usd=worst, projected_expected_usd=expected)
        (out_dir / "results.json").write_text(json.dumps(partial, ensure_ascii=False, indent=1))

    results = await simulate(cfg, client, on_seed=save)
    results["model"] = model
    results["projected_worst_usd"] = worst
    results["projected_expected_usd"] = expected
    (out_dir / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))
    print(json.dumps(results["budget"], indent=1))
    print(f"Results written to {out_dir / 'results.json'} in {results['elapsed_seconds']}s")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
