"""Reference CLI. Fixtures only — no IMAP, no credentials, no personal mail."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from klarpost import __version__
from klarpost.attention import MAX_COST, budget
from klarpost.demo import run_demo
from klarpost.evaluate import Evaluation, evaluate_messages
from klarpost.fixtures import FixtureError, load_fixtures
from klarpost.models import Action
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
            "Policy-as-code for inbox attention. "
            "This reference CLI evaluates fixture files only — never a mailbox."
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
    evaluate.add_argument(
        "--fail-on-delete",
        action="store_true",
        help="exit 1 if any message is a delete_candidate (use on protected fixtures)",
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
    explain.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="text is the human receipt; json is the machine record",
    )
    explain.set_defaults(func=_cmd_explain)

    demo = sub.add_parser("demo", help="narrate policy decisions for synthetic fixtures")
    demo.add_argument("--policy", "-p", required=True, help="path to a YAML policy pack")
    demo.add_argument("--fixtures", "-f", required=True, help="path to a JSON fixture file")
    demo.set_defaults(func=_cmd_demo)

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
    if args.fail_on_delete:
        bad = [item.message_id for item in results if item.action is Action.DELETE_CANDIDATE]
        if bad:
            print(
                "fail-on-delete: delete_candidate on " + ", ".join(bad),
                file=sys.stderr,
            )
            return 1
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


def _cmd_demo(args: argparse.Namespace) -> int:
    return run_demo(args.policy, args.fixtures)


def _cmd_explain(args: argparse.Namespace) -> int:
    pack = load_policy(args.policy)
    messages = load_fixtures(args.fixtures)
    match = next((item for item in messages if item.id == args.message_id), None)
    if match is None:
        print(f"error: no fixture with id {args.message_id!r}", file=sys.stderr)
        return 1
    result = evaluate_messages([match], pack)[0]
    if args.format == "json":
        print(json.dumps(result.as_dict(), indent=2, ensure_ascii=True))
        return 0
    _print_explain(result)
    return 0


def _print_explain(result: Evaluation) -> None:
    verb = {
        "ablegen": "file",
        "archive": "archive",
        "keep": "keep in inbox",
        "delete_candidate": "suggest delete (human still decides)",
    }[result.action.value]
    print(f"message   {result.message_id}")
    print(f"action    {result.action.value}  ({verb})")
    print(f"category  {result.category}")
    print(f"cost      {result.attention_cost}/{MAX_COST}  (lower is quieter)")
    if result.safety_veto:
        print("guard     SAFETY RAIL — protected mail is filed, never a delete candidate")
    print("why")
    for reason in result.reasons:
        print(f"  {reason}")


def _print_table(results: list[Evaluation]) -> None:
    if not results:
        print("no messages")
        return
    rows = [
        (
            item.message_id,
            item.action.value,
            item.category,
            str(item.attention_cost),
            "veto" if item.safety_veto else "-",
            ",".join(item.matched_rules) or "-",
        )
        for item in results
    ]
    headers = ("id", "action", "category", "cost", "safety", "rules")
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
    spent, ceiling = budget([item.action for item in results])
    print()
    print(
        "summary: "
        + ", ".join(
            f"{name}={counts.get(name, 0)}"
            for name in (
                "ablegen",
                "archive",
                "keep",
                "delete_candidate",
            )
        )
        + f", safety_vetoes={vetoes}"
    )
    print(f"attention: {spent}/{ceiling}  (lower is quieter; keep costs {MAX_COST})")
    print(f"evaluated {len(results)} fixture message(s) from {Path.cwd()}")
