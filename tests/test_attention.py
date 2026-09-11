"""Attention cost is a deterministic function of the final action."""

from klarpost.attention import COST, MAX_COST, attention_cost, budget
from klarpost.evaluate import evaluate_messages
from klarpost.models import Action


def test_cost_table_is_strictly_ordered_for_inbox_load():
    assert COST[Action.ABLEGEN] == COST[Action.ARCHIVE] == 1
    assert COST[Action.DELETE_CANDIDATE] == 2
    assert COST[Action.KEEP] == MAX_COST == 3
    assert attention_cost(Action.ABLEGEN) < attention_cost(Action.KEEP)


def test_budget_is_spent_over_ceiling():
    spent, ceiling = budget([Action.ABLEGEN, Action.KEEP, Action.DELETE_CANDIDATE])
    assert spent == 1 + 3 + 2
    assert ceiling == 9


def test_protected_fixtures_are_filed_at_cost_one(inbox_calm, protected_messages):
    results = evaluate_messages(protected_messages, inbox_calm)
    assert results
    assert all(item.action is Action.ABLEGEN for item in results)
    assert all(item.attention_cost == 1 for item in results)
    assert all(item.action is not Action.DELETE_CANDIDATE for item in results)


def test_mixed_inbox_attention_budget_is_stable(inbox_calm, mixed_messages):
    results = evaluate_messages(mixed_messages, inbox_calm)
    spent, ceiling = budget([item.action for item in results])
    assert ceiling == MAX_COST * len(results)
    # 7 filed/archived (1) + 1 promo candidate (2) + 2 keep (3) = 15 / 30
    assert spent == 15
    assert ceiling == 30
    by_id = {item.message_id: item for item in results}
    assert by_id["fx-promo-01"].attention_cost == 2
    assert by_id["fx-unknown-01"].attention_cost == 3
    assert by_id["fx-invoice-01"].attention_cost == 1


def test_json_record_includes_attention_cost(inbox_calm, mixed_messages):
    row = evaluate_messages(mixed_messages, inbox_calm)[0].as_dict()
    assert row["attention_cost"] == attention_cost(Action(row["action"]))
    assert 1 <= int(row["attention_cost"]) <= MAX_COST
