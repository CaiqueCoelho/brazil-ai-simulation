import json
import random
from dataclasses import dataclass
from typing import Annotated, Literal, TypeVar

from pydantic import BaseModel, BeforeValidator, Field, ValidationError, field_validator

from sim.engine import Metrics, PolicyState, World
from sim.llm import LLMClient


def clamped(lo: float, hi: float):
    return Annotated[float, BeforeValidator(lambda v: max(lo, min(hi, float(v))))]


class PresidentDecision(BaseModel):
    priorities: list[str] = Field(default_factory=list)
    statement: str = ""

    @field_validator("priorities")
    @classmethod
    def at_most_three(cls, v: list[str]) -> list[str]:
        return [str(x) for x in v][:3]


class FinanceDecision(BaseModel):
    fiscal_adjust_pct_gdp: clamped(-0.5, 0.5) = 0.0
    rationale: str = ""


class CentraoDecision(BaseModel):
    support: clamped(0.0, 1.0) = 0.5
    amendment_demand_pct_gdp: clamped(0.0, 0.3) = 0.1
    note: str = ""


class Vote(BaseModel):
    policy_id: str
    outcome: Literal["approve", "amend", "reject"]


class CongressDecision(BaseModel):
    votes: list[Vote] = Field(default_factory=list)
    note: str = ""


class Ruling(BaseModel):
    policy_id: str
    ruling: Literal["uphold", "suspend"]


class STFDecision(BaseModel):
    rulings: list[Ruling] = Field(default_factory=list)
    note: str = ""


class CentralBankDecision(BaseModel):
    selic_change_pp: clamped(-1.5, 1.5) = 0.0
    note: str = ""


class MarketsDecision(BaseModel):
    confidence: clamped(-1.0, 1.0) = 0.0
    note: str = ""


class MediaDecision(BaseModel):
    headline: str = ""
    tone: clamped(-1.0, 1.0) = 0.0


class CitizenDecision(BaseModel):
    approval: clamped(0.0, 100.0) = 50.0
    econ_sentiment: clamped(-1.0, 1.0) = 0.0
    top_concern: str = ""
    quote: str = ""


M = TypeVar("M", bound=BaseModel)


@dataclass
class Persona:
    id: int
    region: str
    income: str
    age: str
    area: str
    religion: str
    vote_2022: str
    occupation: str

    def describe(self) -> str:
        return (f"{self.occupation}; age {self.age}; {self.area}, {self.region}; income {self.income}; "
                f"{self.religion}; 2022 runoff: {self.vote_2022}.")


def sample_personas(shares: dict, n: int, seed: int) -> list[Persona]:
    rng = random.Random(f"personas-{seed}")

    def pick(table: dict) -> str:
        keys = list(table)
        return rng.choices(keys, weights=[table[k] for k in keys])[0]

    personas = []
    for i in range(n):
        income = pick(shares["income"])
        personas.append(
            Persona(
                id=i,
                region=pick(shares["region"]),
                income=income,
                age=pick(shares["age"]),
                area=pick(shares["area"]),
                religion=pick(shares["religion"]),
                vote_2022=pick(shares["vote_2022"]),
                occupation=rng.choice(shares["occupation_by_income"][income]),
            )
        )
    return personas


WORLD_RULES = """You are an agent in a realistic simulation of Brazil from January 2027 to December 2030, advancing one quarter per turn.
A new President took office on 1 January 2027 and governs according to the platform below. The President's name and party are intentionally hidden; judge the government only by its platform, actions and results.
Behave like the real Brazilian actor you represent, with its usual interests, constraints and incentives. Be realistic, not idealistic: Congress bargains, markets react to fiscal risk, the Central Bank targets 3% inflation, citizens care about prices, jobs, safety and services.
Always answer with a single JSON object exactly matching the requested schema. Write every text field in Brazilian Portuguese and keep it short."""


def platform_block(policies: list[PolicyState]) -> str:
    lines = []
    for p in policies:
        flags = []
        if p.needs_congress:
            flags.append("needs Congress")
        if p.constitutional_amendment:
            flags.append("constitutional amendment: 3/5 of both houses")
        if p.stf_risk:
            flags.append("may be challenged at the Supreme Court")
        lines.append(f"- {p.id}: {p.title}. {p.description}" + (f" [{'; '.join(flags)}]" if flags else ""))
    return "PRESIDENT'S PLATFORM:\n" + ("\n".join(lines) or "- No new policies: the government continues the policies in force at the end of 2026.")


ROLE_INSTRUCTIONS = {
    "president": """ROLE: You are the President. Each quarter choose up to 3 platform items to push now (only items listed as available), considering political capital, approval and the economy.
JSON schema: {"priorities": ["P01", ...], "statement": "<=30 words public statement"}""",
    "finance": """ROLE: You are the Finance Minister appointed by this President. Decide a discretionary fiscal adjustment on top of the platform, in % of GDP (negative = extra restraint, positive = extra spending), between -0.5 and 0.5.
JSON schema: {"fiscal_adjust_pct_gdp": number, "rationale": "<=25 words"}""",
    "centrao": """ROLE: You are the Centrão, the pragmatic center-right party bloc that holds the swing votes in Congress. Decide how much you support the government (0-1) and how much budget amendment spending you demand in exchange (0-0.3 % of GDP).
JSON schema: {"support": number, "amendment_demand_pct_gdp": number, "note": "<=25 words"}""",
    "bloc": """ROLE: You are a party bloc in the National Congress, described below. Vote on each bill sent this quarter in your bloc's real interest: approve, amend (support only a watered-down version) or reject. Ordinary bills need a simple majority of seats; constitutional amendments need 3/5 of both houses, so they pass only with broad cross-bloc support.
JSON schema: {"votes": [{"policy_id": "Pxx", "outcome": "approve|amend|reject"}], "note": "<=25 words"}""",
    "stf": """ROLE: You are the Supreme Federal Court (STF). For each newly approved measure under challenge, rule whether it is constitutional (uphold) or suspend it.
JSON schema: {"rulings": [{"policy_id": "Pxx", "ruling": "uphold|suspend"}], "note": "<=25 words"}""",
    "central_bank": """ROLE: You are the independent Central Bank's monetary policy committee. Set the change in the Selic rate in percentage points (between -1.5 and 1.5) to bring inflation to the 3% target.
JSON schema: {"selic_change_pp": number, "note": "<=25 words"}""",
    "markets": """ROLE: You are financial markets (banks, asset managers, foreign investors). Give your confidence in Brazil's economic outlook from -1 (panic) to 1 (euphoria).
JSON schema: {"confidence": number, "note": "<=25 words"}""",
    "media": """ROLE: You are the mainstream Brazilian press. Write the quarter's main political-economic headline in Brazilian Portuguese and its tone toward the government from -1 (very negative) to 1 (very positive). Report events and results; do not cite approval ratings or opinion polls.
JSON schema: {"headline": "<=20 words, in Portuguese", "tone": number}""",
    "citizen": """ROLE: You are one Brazilian citizen described below. React to this quarter from your own situation: what changed for you, your family and your community. Your opinion can improve or worsen; judge this quarter on its own merits, not on what others think.
JSON schema: {"approval": 0-100 (your approval of the President), "econ_sentiment": -1 to 1 (how your household's economic life is going), "top_concern": "one or two words", "quote": "<=20 words in Brazilian Portuguese, in your own voice, or empty string when told to skip it"}""",
}


def system_prompt(policies: list[PolicyState], role: str, identity: str = "", record: str = "") -> str:
    record_block = f"\n\n{record}" if record else ""
    return f"{WORLD_RULES}\n\n{platform_block(policies)}{record_block}\n\n{ROLE_INSTRUCTIONS[role]}" + (f"\n{identity}" if identity else "")


def situation(world: World, quarter_label: str, shock_text: str, news: list[str], hide: tuple[str, ...] = ()) -> str:
    m = {k: v for k, v in world.metrics.rounded().items() if k not in hide}
    status = ", ".join(f"{p.id}={p.status}" for p in world.policies)
    recent = "\n".join(f"- {n}" for n in news[-4:]) or "- (none yet)"
    return (
        f"QUARTER: {quarter_label}\n"
        f"ECONOMY AND SOCIETY (latest): {json.dumps(m)}\n"
        f"PLATFORM STATUS: {status}\n"
        f"EXTERNAL CONTEXT THIS QUARTER: {shock_text}\n"
        f"RECENT NEWS:\n{recent}"
    )


async def ask(client: LLMClient, role: str, system: str, user: str, model: type[M], max_tokens: int, fake) -> tuple[M, bool]:
    """Returns (decision, used_fallback). A malformed answer falls back to the schema defaults instead of re-paying."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    text = await client.complete(role, messages, max_tokens, fake)
    try:
        return model.model_validate_json(text), False
    except ValidationError:
        return model(), True


def citizen_memory(c: "CitizenDecision") -> str:
    """Qualitative on purpose: feeding back the exact score makes approval drift in one direction."""
    if c.approval >= 70:
        stance = "strongly approved of"
    elif c.approval >= 55:
        stance = "approved of"
    elif c.approval > 45:
        stance = "were undecided about"
    elif c.approval > 30:
        stance = "disapproved of"
    else:
        stance = "strongly disapproved of"
    household = "improving" if c.econ_sentiment > 0.2 else "getting worse" if c.econ_sentiment < -0.2 else "about the same"
    return f"{stance} the President; household {household}; concern: {c.top_concern or 'unclear'}"


FILLER = "texto simulado com tamanho parecido ao de uma resposta real do modelo para a projecao de custo " * 2


def fake_for(role: str, world: World, pushed: list[str] | None = None, challenged: list[str] | None = None):
    available = [p.id for p in world.policies if world.can_push(p)]
    pushed = pushed or []
    challenged = challenged or []
    return {
        "president": lambda r: {"priorities": r.sample(available, min(3, len(available))), "statement": FILLER},
        "finance": lambda r: {"fiscal_adjust_pct_gdp": r.uniform(-0.3, 0.3), "rationale": FILLER},
        "centrao": lambda r: {"support": r.random(), "amendment_demand_pct_gdp": r.uniform(0, 0.2), "note": FILLER},
        "bloc": lambda r: {
            "votes": [{"policy_id": p, "outcome": r.choice(["approve", "amend", "reject"])} for p in pushed],
            "note": FILLER,
        },
        "stf": lambda r: {"rulings": [{"policy_id": p, "ruling": r.choice(["uphold", "suspend"])} for p in challenged], "note": FILLER},
        "central_bank": lambda r: {"selic_change_pp": r.choice([-0.5, -0.25, 0.0, 0.25, 0.5]), "note": FILLER},
        "markets": lambda r: {"confidence": r.uniform(-0.5, 0.5), "note": FILLER},
        "media": lambda r: {"headline": FILLER[:120], "tone": r.uniform(-0.5, 0.5)},
        "citizen": lambda r: {
            "approval": r.uniform(20, 80),
            "econ_sentiment": r.uniform(-0.6, 0.6),
            "top_concern": r.choice(["inflation", "jobs", "security", "health"]),
            "quote": FILLER[:120],
        },
    }[role]
