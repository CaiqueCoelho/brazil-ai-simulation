import json
import random
from dataclasses import asdict, dataclass, field, fields, replace
from pathlib import Path

from sim.shocks import Shock

LEVERS = (
    "spending",
    "tax",
    "public_investment",
    "social_transfers",
    "security",
    "environment",
    "business_climate",
    "labor_cost",
    "institutional_conflict",
    "health",
    "private_investment",
    "pension_floor_real",
    "min_wage_real",
)

INFLATION_TARGET = 3.0
RAMP_PER_TICK = 0.25
RETRY_COOLDOWN_TICKS = 2
MAX_ATTEMPTS = 2
SIMPLE_MAJORITY = 0.5
CONSTITUTIONAL_THRESHOLD = 0.6
PARAMS_FILE = Path(__file__).resolve().parent.parent / "data" / "engine_params.json"


@dataclass(frozen=True)
class Params:
    trend_growth: float = 2.0
    neutral_real_rate: float = 5.0
    nairu: float = 6.0
    growth_real_rate: float = 0.25
    growth_confidence: float = 1.0
    growth_commodity: float = 1.0
    growth_drought: float = 1.0
    growth_pandemic: float = 6.0
    fiscal_multiplier: float = 0.35
    infl_persistence: float = 0.75
    infl_gap: float = 0.2
    infl_fx: float = 0.08
    infl_drought: float = 0.6
    infl_commodity: float = 0.5
    effective_rate_share: float = 0.9
    effective_rate_smoothing: float = 0.85
    okun: float = 0.08
    growth_business_climate: float = 0.6
    growth_investment: float = 0.5
    tax_cut_passthrough: float = 0.3
    fx_market_confidence: float = 3.0
    growth_transfers: float = 0.0
    nairu_trend: float = 0.0
    gini_transfers: float = 0.015
    gini_inflation: float = 0.0
    gini_pension_floor: float = 0.0007
    gini_min_wage: float = 0.0004
    min_wage_real_baseline: float = 2.5
    poverty_pension_floor: float = 0.03
    poverty_min_wage: float = 0.05
    stability_conflict: float = 1.0
    noise_scale: float = 1.0

    @classmethod
    def load(cls, path: Path = PARAMS_FILE) -> "Params":
        if not path.exists():
            return cls()
        raw = json.loads(path.read_text())
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in raw.get("params", raw).items() if k in known})

    def with_(self, **changes) -> "Params":
        return replace(self, **changes)


@dataclass
class Metrics:
    gdp_growth: float
    inflation: float
    selic: float
    unemployment: float
    debt_gdp: float
    primary_balance: float
    brl_usd: float
    poverty_rate: float
    gini: float
    homicides_per_100k: float
    deforestation_km2: float
    approval: float
    institutional_stability: float
    infant_mortality: float
    democracy_risk: float
    food_insecurity: float

    @classmethod
    def from_dict(cls, data: dict) -> "Metrics":
        return cls(**{k: float(data[k]) for k in cls.__dataclass_fields__})

    def rounded(self) -> dict:
        return {k: round(v, 3) for k, v in asdict(self).items()}


@dataclass
class PolicyState:
    id: str
    title: str
    description: str
    needs_congress: bool
    constitutional_amendment: bool
    stf_risk: bool
    levers: dict[str, float]
    status: str = "not_started"
    implemented: float = 0.0
    strength: float = 1.0
    blocked_until: int = -1
    attempts: int = 0


@dataclass
class TickInputs:
    shock: Shock
    selic_change: float
    fiscal_adjust: float
    amendment_spending: float
    market_confidence: float
    citizen_sentiment: float
    approval: float
    stf_suspensions: int = 0
    court_curb_attempts: int = 0
    court_curb_struck_down: int = 0
    extra_transfers: float = 0.0
    approval_sd: float = 0.0
    fx_change_override: float | None = None
    growth_market_confidence: float | None = None


@dataclass
class World:
    metrics: Metrics
    policies: list[PolicyState]
    seed: int
    params: Params = field(default_factory=Params.load)
    start_year: float = 2027.0
    tick: int = 0
    lever_history: list[dict[str, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._rng = random.Random(f"engine-{self.seed}")
        self._prev_levers = {k: 0.0 for k in LEVERS}
        self._effective_rate = self.params.effective_rate_share * self.metrics.selic
        self._court_conflict = 0.0
        self._one_off_inflation = 0.0

    def policy(self, policy_id: str) -> PolicyState | None:
        return next((p for p in self.policies if p.id == policy_id), None)

    def can_push(self, policy: PolicyState) -> bool:
        return policy.status in ("not_started", "rejected") and self.tick >= policy.blocked_until

    def push(self, policy_id: str) -> PolicyState | None:
        """Executive-only policies are enacted immediately; others go to a Congress vote."""
        policy = self.policy(policy_id)
        if policy is None or not self.can_push(policy):
            return None
        policy.attempts += 1
        policy.status = "pending_vote" if policy.needs_congress else "approved"
        return policy

    def congress_vote(self, policy_id: str, outcome: str) -> None:
        policy = self.policy(policy_id)
        if policy is None or policy.status != "pending_vote":
            return
        if outcome == "approve":
            policy.status, policy.strength = "approved", 1.0
        elif outcome == "amend":
            policy.status, policy.strength = "approved", 0.5
        elif policy.attempts >= MAX_ATTEMPTS:
            policy.status = "abandoned"
        else:
            policy.status = "rejected"
            policy.blocked_until = self.tick + RETRY_COOLDOWN_TICKS

    def stf_ruling(self, policy_id: str, ruling: str) -> bool:
        policy = self.policy(policy_id)
        if policy is None or not policy.stf_risk or policy.status != "approved":
            return False
        if ruling == "suspend":
            policy.status, policy.implemented = "suspended", 0.0
            return True
        return False

    def levers(self) -> dict[str, float]:
        """A policy with a 'spending_cap' lever (a fiscal rule) limits net new primary spending; the excess is cut from discretionary spending."""
        totals = {k: 0.0 for k in LEVERS}
        cap = None
        for p in self.policies:
            for lever, magnitude in p.levers.items():
                if lever == "spending_cap":
                    if p.status == "approved":
                        cap = magnitude
                    continue
                totals[lever] += magnitude * p.implemented * p.strength
        if cap is not None:
            excess = totals["spending"] + totals["social_transfers"] + totals["public_investment"] - cap
            if excess > 0:
                totals["spending"] -= excess
        return totals

    def step(self, inputs: TickInputs) -> Metrics:
        for p in self.policies:
            if p.status == "approved":
                p.implemented = min(1.0, p.implemented + RAMP_PER_TICK)

        k = self.params
        lv = self.levers()
        lv["spending"] += inputs.fiscal_adjust + inputs.amendment_spending
        lv["social_transfers"] += inputs.extra_transfers
        prev = self._prev_levers
        m = self.metrics
        s = inputs.shock
        noise = lambda sd: self._rng.gauss(0, sd * k.noise_scale)  # noqa: E731

        fiscal_now = lv["spending"] + lv["social_transfers"] + lv["public_investment"] - 0.5 * lv["tax"]
        fiscal_prev = prev["spending"] + prev["social_transfers"] + prev["public_investment"] - 0.5 * prev["tax"]
        # Fiscal multiplier acts on the quarterly change (impulse), not the level, so a cut drags only while it phases in.
        fiscal_impulse = (fiscal_now - fiscal_prev) * 4
        market_for_growth = inputs.market_confidence if inputs.growth_market_confidence is None else inputs.growth_market_confidence
        confidence = 0.5 * market_for_growth + 0.5 * inputs.citizen_sentiment
        real_rate = m.selic - m.inflation

        growth = (
            k.trend_growth
            + k.fiscal_multiplier * fiscal_impulse
            + k.growth_investment * (lv["public_investment"] + lv["private_investment"])
            + k.growth_business_climate * lv["business_climate"]
            + k.growth_transfers * lv["social_transfers"]
            + k.growth_confidence * confidence
            - k.growth_real_rate * (real_rate - k.neutral_real_rate)
            + k.growth_commodity * s.commodity
            - k.growth_drought * s.drought
            - k.growth_pandemic * s.pandemic
            - 0.3 * lv["labor_cost"]
            - 0.3 * lv["institutional_conflict"]
            + noise(0.3)
        )
        growth = max(-12.0, min(10.0, growth))
        output_gap = growth - k.trend_growth

        if inputs.fx_change_override is not None:
            fx_change = inputs.fx_change_override
        else:
            fx_change = (
                -k.fx_market_confidence * inputs.market_confidence
                + 2.0 * s.global_rate
                - 2.0 * s.commodity
                + 0.05 * (m.debt_gdp - 80.0)
                + 1.0 * lv["institutional_conflict"]
                + noise(1.5)
            )
        brl_usd = max(2.0, m.brl_usd * (1 + fx_change / 100))

        # Monetary policy reaches prices only through the output gap; a direct real-rate term would count it twice.
        one_off = (
            0.2 * (lv["labor_cost"] - prev["labor_cost"]) * 4
            # Only cuts pass through to prices: the modeled cuts are on consumption, the modeled increase is on top incomes.
            + k.tax_cut_passthrough * min(0.0, lv["tax"] - prev["tax"]) * 4
        )
        # Tax and labor-cost changes move the price level once, so last quarter's jump is not carried forward.
        inflation = (
            k.infl_persistence * (m.inflation - self._one_off_inflation)
            + (1 - k.infl_persistence) * INFLATION_TARGET
            + k.infl_gap * output_gap
            + k.infl_fx * fx_change
            + k.infl_drought * s.drought
            + k.infl_commodity * s.commodity
            + one_off
            + noise(0.2)
        )
        inflation = max(-1.0, min(25.0, inflation))
        self._one_off_inflation = one_off

        selic = max(2.0, min(25.0, m.selic + inputs.selic_change))

        year = self.start_year + self.tick / 4
        nairu = max(4.5, k.nairu + k.nairu_trend * (year - 2018))
        unemployment = (
            m.unemployment
            - k.okun * output_gap
            + 0.05 * (nairu - m.unemployment)
            + noise(0.1)
        )
        unemployment = max(3.0, min(20.0, unemployment))
        d_unemployment = unemployment - m.unemployment

        primary_balance = -0.4 - lv["spending"] + lv["tax"] - lv["social_transfers"] - lv["public_investment"] + 0.2 * output_gap

        # Debt reprices gradually, so the implicit interest rate follows the Selic with a lag.
        self._effective_rate = (
            k.effective_rate_smoothing * self._effective_rate
            + (1 - k.effective_rate_smoothing) * k.effective_rate_share * selic
        )
        nominal_growth = growth + inflation
        debt_gdp = m.debt_gdp + ((self._effective_rate - nominal_growth) * m.debt_gdp / 100 - primary_balance) / 4
        debt_gdp = max(30.0, min(200.0, debt_gdp))

        d_social = lv["social_transfers"] - prev["social_transfers"]
        poverty_rate = (
            m.poverty_rate
            + 0.5 * d_unemployment
            - 2.0 * d_social
            - 0.03 * output_gap
            + 0.03 * (inflation - 4.0)
            - k.poverty_min_wage * (k.min_wage_real_baseline + lv["min_wage_real"]) / 4
            - k.poverty_pension_floor * lv["pension_floor_real"] / 4
            + noise(0.1)
        )
        poverty_rate = max(2.0, min(60.0, poverty_rate))

        gini = (
            m.gini
            + 0.002 * d_unemployment
            - k.gini_transfers * d_social
            + k.gini_inflation * (inflation - 4.0)
            - k.gini_min_wage * (k.min_wage_real_baseline + lv["min_wage_real"]) / 4
            - k.gini_pension_floor * lv["pension_floor_real"] / 4
            + noise(0.001)
        )
        gini = max(0.35, min(0.70, gini))

        homicides = m.homicides_per_100k * (
            1 - 0.0025 - 0.02 * lv["security"] - 0.005 * output_gap + 0.005 * d_unemployment + noise(0.01)
        )
        homicides = max(2.0, homicides)

        deforestation = m.deforestation_km2 * (
            1 - 0.04 * lv["environment"] + 0.01 * s.commodity + 0.02 * s.drought + noise(0.03)
        )
        deforestation = max(500.0, deforestation)

        # Attempts to curb the courts count even when they fail and fade slowly: executive aggrandizement is a lasting risk signal in democracy indices.
        self._court_conflict = 0.9 * self._court_conflict + 10.0 * inputs.court_curb_attempts + 10.0 * inputs.court_curb_struck_down
        stability_target = (
            70.0 - 15.0 * lv["institutional_conflict"] - 10.0 * s.scandal - 3.0 * inputs.stf_suspensions
            - k.stability_conflict * self._court_conflict
        )
        stability = 0.7 * m.institutional_stability + 0.3 * stability_target

        infant_mortality = m.infant_mortality * (
            1 - 0.005 - 0.02 * lv["health"] + 0.02 * (poverty_rate - m.poverty_rate) + 0.01 * s.pandemic + noise(0.003)
        )
        infant_mortality = max(3.0, infant_mortality)

        # Fixed before the informed run: hunger follows poverty and cash transfers, and rises with droughts.
        food_insecurity = (
            m.food_insecurity
            + 0.25 * (poverty_rate - m.poverty_rate)
            - 0.5 * d_social
            + 0.05 * s.drought
            + noise(0.02)
        )
        food_insecurity = max(0.5, food_insecurity)

        polarization = min(100.0, inputs.approval_sd * 2.5)
        risk_target = (
            0.5 * (100.0 - stability)
            + 0.3 * polarization
            + self._court_conflict
            + 15.0 * lv["institutional_conflict"]
        )
        democracy_risk = 0.7 * m.democracy_risk + 0.3 * risk_target

        self.metrics = Metrics(
            gdp_growth=growth,
            inflation=inflation,
            selic=selic,
            unemployment=unemployment,
            debt_gdp=debt_gdp,
            primary_balance=primary_balance,
            brl_usd=brl_usd,
            poverty_rate=poverty_rate,
            gini=gini,
            homicides_per_100k=homicides,
            deforestation_km2=deforestation,
            approval=max(0.0, min(100.0, inputs.approval)),
            institutional_stability=max(0.0, min(100.0, stability)),
            infant_mortality=infant_mortality,
            democracy_risk=max(0.0, min(100.0, democracy_risk)),
            food_insecurity=food_insecurity,
        )
        self._prev_levers = lv
        self.lever_history.append(lv)
        self.tick += 1
        return self.metrics


def tally(bloc_votes: dict[str, str], seats: dict[str, float], constitutional: bool) -> str:
    """Seat-weighted outcome. A bill passes if approve+amend clears the threshold; it passes in full only if approve alone does."""
    threshold = CONSTITUTIONAL_THRESHOLD if constitutional else SIMPLE_MAJORITY
    total = sum(seats.values())
    approve = sum(seats[b] for b, v in bloc_votes.items() if v == "approve") / total
    amend = sum(seats[b] for b, v in bloc_votes.items() if v == "amend") / total
    if approve > threshold:
        return "approve"
    if approve + amend > threshold:
        return "amend"
    return "reject"


def load_policies(raw: dict) -> list[PolicyState]:
    return [
        PolicyState(
            id=p["id"],
            title=p["title"],
            description=p["description"],
            needs_congress=p["needs_congress"],
            constitutional_amendment=p["constitutional_amendment"],
            stf_risk=p["stf_risk"],
            levers=dict(p["levers"]),
        )
        for p in raw["policies"]
    ]
