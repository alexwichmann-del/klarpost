"""A vivid, fixture-only tour of klarpost decisions."""

from __future__ import annotations

import argparse

from klarpost.evaluate import evaluate_messages
from klarpost.fixtures import load_fixtures
from klarpost.policy import load_policy


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

    for result in results:
        print(f"MAIL  {result.message_id}")
        print(f"  route: {result.action.value}  |  category: {result.category}")
        if result.safety_veto:
            print("  guard: SAFETY VETO — the paper trail wins")
        for reason in result.reasons:
            print(f"  why:   {reason}")
        if not result.reasons:
            print("  why:   no rule matched; uncertainty stays visible")
        print()

    print("No mailbox was opened. No message was deleted. Every choice is reviewable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
