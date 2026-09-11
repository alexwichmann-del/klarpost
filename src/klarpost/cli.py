"""Reference CLI. Fixtures only — no IMAP, no credentials, no personal mail."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from klarpost import __version__
from klarpost.evaluate import Evaluation, evaluate_messages
from klarpost.fixtures import FixtureError, load_fixtures
from klarpost.policy import PolicyError, load_policy
from klarpost.schema import policy_json_schema

# Refuse even the *shape* of a live-mail / credential workflow.
FORBIDDEN_FLAGS = (
    "--imap",
    "--imaps",
    "--smtp",
    "--host",
    "--password",
    "--passwd",
    "--oauth",
    "--token",
    "--secret",
    "--credentials",
    "--login",
    "--user",
    "--username",
    "--mailbox",
    "--inbox",
)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    blocked = _forbidden(args)
    if blocked:
        print(
            "klarpost refuses live-mail and credential flags "
            f"({', '.join(blocked)}). Evaluate synthetic fixtures only.",
            file=sys.stderr,
        )
        return 2

    parser = _build_parser()
    parsed = parser.parse_args(args)
    try:
        return parsed.func(parsed)
    except (PolicyError, FixtureError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _forbidden(args: list[str]) -> list[str]:
    found: list[str] = []
    for item in args:
        key = item.split("=", 1)[0].lower()
        if key in FORBIDDEN_FLAGS:
            found.append(key)
    return found


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="klarpost",
        description=(
            "Policy-as-code for personal email hygiene. "
            "This reference CLI evaluates fixture files only."
        ),
    )
    parser.add_argument("--version", action="version", version=f"klarpost {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    evaluate = sub.add_parser("evaluate", help="classify fixture messages with a policy pack")
    evaluate.add_argument("--policy", "-p", required=True, help="path to a YAML policy pack")
    evaluate.add_argument("--fixtures", "-f", required=True, help="path to a JSON fixture file")
    evaluate.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        help="output format (default: table)",
    )
    evaluate.set_defaults(func=_cmd_evaluate)

    validate = sub.add_parser(
        "validate",
        help="validate a policy pack against schema + safety rails",
    )
    validate.add_argument("--policy", "-p", required=True, help="path to a YAML policy pack")
    validate.set_defaults(func=_cmd_validate)

    schema = sub.add_parser("schema", help="print the policy JSON Schema")
    schema.set_defaults(func=_cmd_schema)

    explain = sub.add_parser("explain", help="show why one fixture message received its action")
    explain.add_argument("--policy", "-p", required=True)
    explain.add_argument("--fixtures", "-f", required=True)
    explain.add_argument("--message-id", "-m", required=True)
    explain.set_defaults(func=_cmd_explain)

    return parser


def _cmd_evaluate(args: argparse.Namespace) -> int:
    pack = load_policy(args.policy)
    messages = load_fixtures(args.fixtures)
    results = evaluate_messages(messages, pack)
    if args.format == "json":
        print(json.dumps([item.as_dict() for item in results], indent=2, ensure_ascii=True))
    else:
        _print_table(results)
        _print_summary(results)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    pack = load_policy(args.policy)
    print(
        f"ok: {pack.id} ({len(pack.rules)} rules, "
        f"{len(pack.safety.never_delete_categories) or 'hard-default'} extra protected categories)"
    )
    return 0


def _cmd_schema(_args: argparse.Namespace) -> int:
    print(json.dumps(policy_json_schema(), indent=2, ensure_ascii=True))
    return 0


def _cmd_explain(args: argparse.Namespace) -> int:
    pack = load_policy(args.policy)
    messages = load_fixtures(args.fixtures)
    match = next((item for item in messages if item.id == args.message_id), None)
    if match is None:
        print(f"error: no fixture with id {args.message_id!r}", file=sys.stderr)
        return 1
    result = evaluate_messages([match], pack)[0]
    print(_explain_prose(result))
    print(json.dumps(result.as_dict(), indent=2, ensure_ascii=True))
    return 0


def _explain_prose(result: Evaluation) -> str:
    """One English paragraph so a human can read the decision without JSON."""
    category = result.category.replace("_", " ")
    if result.action.value == "ablegen":
        action_bit = "File (ablegen) wins"
    elif result.action.value == "keep":
        action_bit = "Keep it"
    elif result.action.value == "archive":
        action_bit = "Archive it"
    else:
        action_bit = "Delete is a candidate only"

    if result.safety_veto:
        veto_bit = "delete is vetoed by a safety rail"
    else:
        veto_bit = "no safety veto applied"

    return (
        f"This looks like {category} mail that also matched other policy rules. "
        f"{action_bit}; {veto_bit}."
    )


def _print_table(results: list[Evaluation]) -> None:
    if not results:
        print("no messages")
        return
    rows = [
        (
            item.message_id,
            item.action.value,
            item.category,
            "veto" if item.safety_veto else "-",
            ",".join(item.matched_rules) or "-",
        )
        for item in results
    ]
    headers = ("id", "action", "category", "safety", "rules")
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    fmt = "  ".join(f"{{:{width}}}" for width in widths)
    print(fmt.format(*headers))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print(fmt.format(*row))


def _print_summary(results: list[Evaluation]) -> None:
    counts = Counter(item.action.value for item in results)
    vetoes = sum(1 for item in results if item.safety_veto)
    print()
    print(
        "summary: "
        + ", ".join(f"{name}={counts.get(name, 0)}" for name in (
            "ablegen",
            "archive",
            "keep",
            "delete_candidate",
        ))
        + f", safety_vetoes={vetoes}"
    )
    print(f"evaluated {len(results)} fixture message(s) from {Path.cwd()}")
