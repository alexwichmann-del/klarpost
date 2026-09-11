"""A vivid, fixture-only tour of klarpost decisions."""

from __future__ import annotations

import argparse

from klarpost.evaluate import evaluate_messages
from klarpost.fixtures import load_fixtures
from klarpost.policy import load_policy

ATTENTION_COST = {"ablegen": 1, "archive": 1, "keep": 3, "delete_candidate": 2}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m klarpost.demo",
        description="Narrate policy decisions for synthetic fixtures only.",
    )
    parser.add_argument("--policy", "-p", required=True)
    parser.add_argument("--fixtures", "-f", required=True)
    args = parser.parse_args()

    pack = load_policy(args.policy)
    results = evaluate_messages(load_fixtures(args.fixtures), pack)
    print(f"klarpost demo // {pack.name}")
    print("A calm inbox is not an empty inbox. Here is what the policy protects:\n")

    total_cost = 0
    for result in results:
        cost = ATTENTION_COST[result.action.value]
        total_cost += cost
        print(f"MAIL  {result.message_id}")
        print(f"  route: {result.action.value}  |  category: {result.category}")
        print(f"  attention cost: {cost}/3  (lower is quieter)")
        if result.safety_veto:
            print("  guard: SAFETY VETO — the paper trail wins")
        for reason in result.reasons:
            print(f"  why:   {reason}")
        if not result.reasons:
            print("  why:   no rule matched; uncertainty stays visible")
        print()

    print(f"attention budget: {total_cost} point(s) for {len(results)} message(s)")
    print("No mailbox was opened. No message was deleted. Every choice is reviewable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
