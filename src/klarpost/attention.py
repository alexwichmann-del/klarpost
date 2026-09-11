"""Deterministic attention cost.

Lower is quieter. The number is a function of the *final* action only — not
telemetry, not a learned score, not a UI animation. Tests and CI can freeze
it the same way they freeze `delete_candidate` counts.

    file (ablegen)  1  decided; paper trail is parked
    archive         1  decided; out of the inbox
    delete_candidate 2  still needs a human to accept or reject
    keep            3  still occupies the inbox — the expensive default

Protected mail must never land on `delete_candidate`, so it never pays cost 2.
When the rails file it, it pays cost 1.
"""

from __future__ import annotations

from klarpost.models import Action

COST: dict[Action, int] = {
    Action.ABLEGEN: 1,
    Action.ARCHIVE: 1,
    Action.DELETE_CANDIDATE: 2,
    Action.KEEP: 3,
}

MAX_COST = 3


def attention_cost(action: Action) -> int:
    """Return the stable attention cost for an action (1..MAX_COST)."""
    return COST[action]


def budget(actions: list[Action]) -> tuple[int, int]:
    """Return (spent, ceiling) for a list of actions. Ceiling is MAX_COST * n."""
    spent = sum(attention_cost(action) for action in actions)
    ceiling = MAX_COST * len(actions)
    return spent, ceiling
