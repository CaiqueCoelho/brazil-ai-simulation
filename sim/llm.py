import asyncio
import hashlib
import json
import math
import random
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

CHARS_PER_TOKEN = 3.0


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class Prices:
    input: float
    cache_hit: float
    output: float

    def cost(self, prompt_tokens: int, cache_hit_tokens: int, completion_tokens: int) -> float:
        miss = max(0, prompt_tokens - cache_hit_tokens)
        return (miss * self.input + cache_hit_tokens * self.cache_hit + completion_tokens * self.output) / 1_000_000


def estimate_tokens(messages: list[dict]) -> int:
    return math.ceil(sum(len(m["content"]) for m in messages) / CHARS_PER_TOKEN) + 8 * len(messages)


@dataclass
class Budget:
    limit_usd: float
    prices: Prices
    spent: float = 0.0
    reserved: float = 0.0
    calls: int = 0
    cached_calls: int = 0
    prompt_tokens: int = 0
    cache_hit_tokens: int = 0
    completion_tokens: int = 0
    by_role: dict[str, float] = field(default_factory=dict)
    tokens_by_role: dict[str, list[int]] = field(default_factory=dict)

    def reserve(self, est_prompt_tokens: int, max_tokens: int) -> float:
        worst = self.prices.cost(est_prompt_tokens, 0, max_tokens)
        if self.spent + self.reserved + worst > self.limit_usd:
            raise BudgetExceeded(
                f"next call could reach ${self.spent + self.reserved + worst:.4f} > budget ${self.limit_usd:.2f}"
            )
        self.reserved += worst
        return worst

    def settle(self, reservation: float, role: str, prompt_tokens: int, cache_hit_tokens: int, completion_tokens: int) -> None:
        self.reserved -= reservation
        cost = self.prices.cost(prompt_tokens, cache_hit_tokens, completion_tokens)
        self.spent += cost
        self.calls += 1
        self.prompt_tokens += prompt_tokens
        self.cache_hit_tokens += cache_hit_tokens
        self.completion_tokens += completion_tokens
        self.by_role[role] = self.by_role.get(role, 0.0) + cost
        t = self.tokens_by_role.setdefault(role, [0, 0, 0, 0])
        t[0] += 1
        t[1] += prompt_tokens
        t[2] += cache_hit_tokens
        t[3] += completion_tokens

    def release(self, reservation: float) -> None:
        self.reserved -= reservation

    def summary(self) -> dict:
        return {
            "spent_usd": round(self.spent, 4),
            "limit_usd": self.limit_usd,
            "calls": self.calls,
            "cached_calls": self.cached_calls,
            "prompt_tokens": self.prompt_tokens,
            "cache_hit_tokens": self.cache_hit_tokens,
            "completion_tokens": self.completion_tokens,
            "by_role_usd": {k: round(v, 4) for k, v in sorted(self.by_role.items())},
            "tokens_by_role": {k: dict(zip(("calls", "prompt", "cache_hit", "completion"), v)) for k, v in sorted(self.tokens_by_role.items())},
        }


class ResponseCache:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        self._db.execute("CREATE TABLE IF NOT EXISTS responses (key TEXT PRIMARY KEY, content TEXT NOT NULL)")

    @staticmethod
    def key(model: str, messages: list[dict], max_tokens: int, temperature: float) -> str:
        blob = json.dumps([model, messages, max_tokens, temperature], ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def get(self, key: str) -> str | None:
        row = self._db.execute("SELECT content FROM responses WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def put(self, key: str, content: str) -> None:
        self._db.execute("INSERT OR REPLACE INTO responses VALUES (?, ?)", (key, content))
        self._db.commit()


Faker = Callable[[random.Random], dict]


class LLMClient(Protocol):
    budget: Budget

    async def complete(self, role: str, messages: list[dict], max_tokens: int, fake: Faker) -> str: ...


class FakeClient:
    """Returns random schema-valid JSON and books the worst-case cost of each call, so a dry run yields an upper-bound projection."""

    def __init__(self, budget: Budget, seed: int):
        self.budget = budget
        self._rng = random.Random(f"fake-{seed}")

    async def complete(self, role: str, messages: list[dict], max_tokens: int, fake: Faker) -> str:
        est = estimate_tokens(messages)
        self.budget.settle(0.0, role, est, 0, max_tokens)
        return json.dumps(fake(self._rng))


class DeepSeekClient:
    def __init__(
        self,
        budget: Budget,
        cache: ResponseCache,
        api_key: str,
        model: str,
        base_url: str,
        concurrency: int,
        temperature: float,
    ):
        from openai import AsyncOpenAI

        self.budget = budget
        self.model = model
        self.temperature = temperature
        self._cache = cache
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=120)
        self._sem = asyncio.Semaphore(concurrency)

    async def complete(self, role: str, messages: list[dict], max_tokens: int, fake: Faker) -> str:
        key = ResponseCache.key(self.model, messages, max_tokens, self.temperature)
        if (hit := self._cache.get(key)) is not None:
            self.budget.cached_calls += 1
            return hit

        reservation = self.budget.reserve(estimate_tokens(messages), max_tokens)
        try:
            async with self._sem:
                resp = await self._with_retries(messages, max_tokens)
        except BaseException:
            self.budget.release(reservation)
            raise

        usage = resp.usage
        self.budget.settle(
            reservation,
            role,
            usage.prompt_tokens,
            getattr(usage, "prompt_cache_hit_tokens", 0) or 0,
            usage.completion_tokens,
        )
        content = resp.choices[0].message.content or "{}"
        self._cache.put(key, content)
        return content

    async def _with_retries(self, messages: list[dict], max_tokens: int, attempts: int = 5):
        delay = 2.0
        for attempt in range(attempts):
            try:
                return await self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=self.temperature,
                    response_format={"type": "json_object"},
                    extra_body={"thinking": {"type": "disabled"}},
                )
            except Exception as exc:
                if getattr(exc, "status_code", None) == 402:
                    raise BudgetExceeded("DeepSeek account balance exhausted") from exc
                if attempt == attempts - 1:
                    raise
                await asyncio.sleep(delay)
                delay *= 2
