import asyncio

import pytest

from sim.agents import CentralBankDecision, CitizenDecision, PresidentDecision, ask
from sim.llm import Budget, BudgetExceeded, FakeClient, Prices, ResponseCache, estimate_tokens

PRICES = Prices(input=0.09, cache_hit=0.09, output=0.18)


def test_cost_formula_uses_cache_hit_price_for_cached_tokens():
    p = Prices(input=0.10, cache_hit=0.01, output=0.20)
    assert p.cost(1_000_000, 500_000, 1_000_000) == pytest.approx(0.05 + 0.005 + 0.20)


def test_reserve_refuses_a_call_that_could_cross_the_limit():
    budget = Budget(limit_usd=0.001, prices=PRICES)
    with pytest.raises(BudgetExceeded):
        budget.reserve(est_prompt_tokens=20_000, max_tokens=10_000)


def test_reservations_count_against_the_limit_until_settled():
    budget = Budget(limit_usd=0.0002, prices=PRICES)
    r = budget.reserve(1000, 500)
    with pytest.raises(BudgetExceeded):
        budget.reserve(1000, 500)
    budget.settle(r, "citizen", 1000, 0, 100)
    assert budget.reserved == pytest.approx(0)
    assert budget.spent == pytest.approx(PRICES.cost(1000, 0, 100))


def test_estimate_is_conservative_for_portuguese_text():
    msgs = [{"role": "user", "content": "Qual é a sua opinião sobre a inflação no Brasil? " * 50}]
    assert estimate_tokens(msgs) >= len(msgs[0]["content"]) / 4


def test_response_cache_roundtrip(tmp_path):
    cache = ResponseCache(tmp_path / "c.sqlite")
    key = ResponseCache.key("m", [{"role": "user", "content": "x"}], 10, 0.7)
    assert cache.get(key) is None
    cache.put(key, '{"a": 1}')
    assert cache.get(key) == '{"a": 1}'


def test_out_of_range_values_are_clamped():
    assert CentralBankDecision.model_validate({"selic_change_pp": 9}).selic_change_pp == 1.5
    c = CitizenDecision.model_validate({"approval": 140, "econ_sentiment": -3})
    assert (c.approval, c.econ_sentiment) == (100.0, -1.0)
    assert PresidentDecision.model_validate({"priorities": ["P1", "P2", "P3", "P4"]}).priorities == ["P1", "P2", "P3"]


def test_malformed_json_falls_back_to_defaults():
    class Broken:
        budget = Budget(limit_usd=1, prices=PRICES)

        async def complete(self, *a, **k):
            return "not json"

    decision, fallback = asyncio.run(ask(Broken(), "citizen", "s", "u", CitizenDecision, 10, None))
    assert fallback is True
    assert decision.approval == 50.0


def test_fake_client_books_worst_case_cost():
    budget = Budget(limit_usd=float("inf"), prices=PRICES)
    client = FakeClient(budget, seed=1)
    msgs = [{"role": "user", "content": "x" * 3000}]
    asyncio.run(client.complete("citizen", msgs, 200, lambda r: {"ok": True}))
    assert budget.spent == pytest.approx(PRICES.cost(estimate_tokens(msgs), 0, 200))
