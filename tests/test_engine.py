import json
from pathlib import Path

from sim.engine import Metrics, TickInputs, World, load_policies
from sim.shocks import shock_schedule

DATA = Path(__file__).resolve().parent.parent / "data"


def make_world(candidate: str = "lula", seed: int = 42) -> World:
    baseline = json.loads((DATA / "baseline_2026q4.json").read_text())
    raw = json.loads((DATA / f"policies_{candidate}.json").read_text())
    return World(Metrics.from_dict(baseline), load_policies(raw), seed=seed)


def neutral_inputs(shock) -> TickInputs:
    return TickInputs(shock=shock, selic_change=0.0, fiscal_adjust=0.0, amendment_spending=0.0,
                      market_confidence=0.0, citizen_sentiment=0.0, approval=50.0)


def run(world: World, ticks: int = 16) -> list[dict]:
    return [world.step(neutral_inputs(s)).rounded() for s in shock_schedule(42, ticks)]


def test_same_seed_gives_identical_metrics():
    assert run(make_world()) == run(make_world())


def test_different_seed_changes_noise():
    assert run(make_world(seed=1)) != run(make_world(seed=2))


def test_shock_schedule_is_shared_by_seed():
    assert shock_schedule(42, 16) == shock_schedule(42, 16)


def test_executive_policy_is_enacted_immediately_and_ramps_to_full():
    world = make_world()
    assert world.push("P04").status == "approved"
    for s in shock_schedule(42, 5):
        world.step(neutral_inputs(s))
    assert world.policy("P04").implemented == 1.0
    assert world.levers()["security"] == world.policy("P04").levers["security"]


def test_congress_policy_waits_for_vote_and_amend_halves_strength():
    world = make_world("flavio")
    assert world.push("P01").status == "pending_vote"
    world.congress_vote("P01", "amend")
    for s in shock_schedule(42, 4):
        world.step(neutral_inputs(s))
    assert world.levers()["spending"] == 0.5 * world.policy("P01").levers["spending"]


def test_rejected_policy_has_cooldown():
    world = make_world("flavio")
    world.push("P03")
    world.congress_vote("P03", "reject")
    assert world.push("P03") is None
    for s in shock_schedule(42, 2):
        world.step(neutral_inputs(s))
    assert world.push("P03") is not None


def test_stf_suspension_resets_implementation():
    world = make_world("flavio")
    world.push("P08")
    world.congress_vote("P08", "approve")
    world.step(neutral_inputs(shock_schedule(42, 1)[0]))
    assert world.stf_ruling("P08", "suspend") is True
    assert world.policy("P08").implemented == 0.0
    assert world.policy("P08").status == "suspended"


def test_stf_cannot_rule_on_unchallengeable_policy():
    world = make_world("lula")
    world.push("P04")
    assert world.stf_ruling("P04", "suspend") is False


def test_tight_money_lowers_inflation_versus_loose_money():
    tight, loose = make_world(), make_world()
    for s in shock_schedule(42, 8):
        tight.step(TickInputs(s, 1.0, 0, 0, 0, 0, 50))
        loose.step(TickInputs(s, -1.0, 0, 0, 0, 0, 50))
    assert tight.metrics.inflation < loose.metrics.inflation
    assert tight.metrics.gdp_growth < loose.metrics.gdp_growth


def test_metrics_stay_within_bounds_under_extreme_inputs():
    world = make_world()
    for s in shock_schedule(42, 16):
        m = world.step(TickInputs(s, 1.5, 0.5, 0.3, -1.0, -1.0, 150))
    assert 0 <= m.approval <= 100
    assert 3 <= m.unemployment <= 20
    assert 2 <= m.selic <= 25


SEATS = {"left": 0.27, "centrao": 0.48, "right": 0.25}


def test_tally_simple_majority_needs_more_than_half_of_seats():
    from sim.engine import tally

    assert tally({"left": "approve", "centrao": "approve", "right": "reject"}, SEATS, False) == "approve"
    assert tally({"left": "approve", "centrao": "reject", "right": "approve"}, SEATS, False) == "approve"
    assert tally({"left": "approve", "centrao": "reject", "right": "reject"}, SEATS, False) == "reject"


def test_tally_amend_votes_pass_a_watered_down_bill():
    from sim.engine import tally

    assert tally({"left": "approve", "centrao": "amend", "right": "reject"}, SEATS, False) == "amend"


def test_tally_constitutional_amendment_needs_three_fifths():
    from sim.engine import tally

    assert tally({"left": "reject", "centrao": "approve", "right": "approve"}, SEATS, True) == "approve"
    assert tally({"left": "approve", "centrao": "approve", "right": "reject"}, SEATS, True) == "approve"
    assert tally({"left": "reject", "centrao": "amend", "right": "reject"}, SEATS, True) == "reject"
    assert tally({"left": "approve", "centrao": "reject", "right": "approve"}, SEATS, True) == "reject"


def test_rejected_bill_is_abandoned_after_max_attempts():
    world = make_world("flavio")
    for _ in range(2):
        world.push("P10")
        world.congress_vote("P10", "reject")
        for s in shock_schedule(42, 2):
            world.step(neutral_inputs(s))
    assert world.policy("P10").status == "abandoned"
    assert world.push("P10") is None


def world_with(levers: dict) -> World:
    from sim.engine import Params, PolicyState
    baseline = json.loads((DATA / "baseline_2026q4.json").read_text())
    policy = PolicyState(id="X", title="t", description="", needs_congress=False, constitutional_amendment=False,
                         stf_risk=False, levers=levers, status="approved", implemented=1.0)
    return World(Metrics.from_dict(baseline), [policy], seed=1, params=Params().with_(noise_scale=0.0))


def test_inflation_only_pension_floor_raises_poverty():
    frozen, kept = world_with({"pension_floor_real": -2.5}), world_with({})
    for s in shock_schedule(1, 8):
        a, b = frozen.step(neutral_inputs(s)), kept.step(neutral_inputs(s))
    assert a.poverty_rate > b.poverty_rate


def test_shorter_working_week_raises_prices_once_not_forever():
    world, base = world_with({}), world_with({})
    world.policies[0].levers = {"labor_cost": 0.5}
    world.policies[0].implemented = 0.0
    world.policies[0].status = "approved"
    gaps = []
    for s in shock_schedule(1, 16):
        gaps.append(world.step(neutral_inputs(s)).inflation - base.step(neutral_inputs(s)).inflation)
    assert gaps[3] > 0
    assert gaps[-1] < gaps[3] / 2


def test_fiscal_rule_caps_net_new_spending_by_cutting_discretionary_spending():
    world = world_with({"social_transfers": 0.3, "public_investment": 0.2})
    capped = world_with({"social_transfers": 0.3, "public_investment": 0.2})
    from sim.engine import PolicyState
    capped.policies.append(PolicyState(id="R", title="rule", description="", needs_congress=False, constitutional_amendment=False,
                                       stf_risk=False, levers={"spending_cap": 0.1}, status="approved", implemented=1.0))
    lv = capped.levers()
    assert lv["social_transfers"] == 0.3
    assert abs(lv["spending"] + lv["social_transfers"] + lv["public_investment"] - 0.1) < 1e-9
    assert world.levers()["spending"] == 0.0


def test_consumption_tax_cut_lowers_prices_once_not_forever():
    world, base = world_with({}), world_with({})
    world.policies[0].levers = {"tax": -0.3}
    world.policies[0].implemented = 0.0
    gaps = []
    for s in shock_schedule(1, 12):
        gaps.append(world.step(neutral_inputs(s)).inflation - base.step(neutral_inputs(s)).inflation)
    assert gaps[0] < 0
    assert abs(gaps[6]) < abs(gaps[0]) / 4
