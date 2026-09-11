"""A fixture-only tour of klarpost decisions and attention cost."""

from __future__ import annotations

import argparse

from klarpost.attention import MAX_COST, budget
from klarpost.evaluate import Evaluation, evaluate_messages
from klarpost.fixtures import load_fixtures
from klarpost.policy import load_policy


def run_demo(policy: str, fixtures: str) -> int:
    pack = load_policy(policy)
    results = evaluate_messages(load_fixtures(fixtures), pack)
    _print_demo(pack.name, results)
    return 0


def _print_demo(pack_name: str, results: list[Evaluation]) -> None:
    print(f"klarpost demo // {pack_name}")
    print("A calm inbox is not an empty inbox. Here is what the policy protects:\n")

    for result in results:
        print(f"MAIL  {result.message_id}")
        print(f"  route: {result.action.value}  |  category: {result.category}")
        print(f"  attention cost: {result.attention_cost}/{MAX_COST}  (lower is quieter)")
        if result.safety_veto:
            print("  guard: SAFETY RAIL — protected mail is filed")
        for reason in result.reasons:
            print(f"  why:   {reason}")
        if not result.reasons:
            print("  why:   no rule matched; uncertainty stays visible")
        print()

    spent, ceiling = budget([item.action for item in results])
    print(f"attention budget: {spent}/{ceiling} for {len(results)} message(s)")
    print("No mailbox was opened. No message was deleted. Every choice is reviewable.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m klarpost.demo",
        description="Narrate policy decisions for synthetic fixtures only.",
    )
    parser.add_argument("--policy", "-p", required=True)
    parser.add_argument("--fixtures", "-f", required=True)
    args = parser.parse_args(argv)
    return run_demo(args.policy, args.fixtures)


if __name__ == "__main__":
    raise SystemExit(main())
