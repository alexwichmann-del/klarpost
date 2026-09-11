# AGENTS.md — maintainer contract

Working agreement for humans and coding agents (including Codex) maintaining klarpost.

klarpost is **policy-as-code for inbox attention**, not a mailbox connector. The CLI evaluates synthetic fixtures. It must keep refusing live mail.

## Non-negotiables

- Explain why mail was filed, archived, kept, or only *suggested* for deletion.
- Protect the paper trail. Orders, invoices, receipts, tickets, travel, banking, security, government, medical, legal, and identity mail never become `delete_candidate`.
- `delete_candidate` is a human-review suggestion, never an executed delete.
- Keep the CLI fixtures-only: no IMAP, SMTP, OAuth, tokens, credentials, or personal mail.
- Write docs, issues, PRs, CLI help, reasons, comments, and tests in English first. Matcher keywords may include other languages.
- Keep the name `klarpost`. `ablegen` is the file action (schema token). Do not rename it. Do not scatter other German UI terms.

ADHD and high-sensory-load framing is honest context, not a universal-accessibility claim.

## Layout

| Path | Change when |
| --- | --- |
| `src/klarpost/safety.py` | Keyword rails, protected set, veto |
| `src/klarpost/evaluate.py` | Action choice, receipts, reasons |
| `src/klarpost/attention.py` | Cost table (`1/2/3`) |
| `src/klarpost/policy.py` | Pack validation |
| `src/klarpost/cli.py` | Commands; keep `FORBIDDEN_FLAGS` |
| `policies/packs/*.yaml` | Sample packs (safety review) |
| `fixtures/*.json` | Synthetic mail only |
| `tests/test_safety.py` | Never-delete proofs |
| `tests/test_attention.py` | Cost proofs |

## Review every policy-pack PR

1. **State intent.** Say what attention cost changes and why the action is safer.
2. **Inspect precedence.** Read the full pack; confirm safety matches cannot be shadowed and ties are deterministic (`ablegen` > `archive` > `keep` > `delete_candidate`).
3. **Require fixtures.** Add a positive case, a near miss, and a protected collision where relevant. Synthetic `example.com` data only.
4. **Check the receipt.** Results expose rule id, category, action, safety veto, attention cost, and a plain-English reason.
5. **Run gates.** Commands below. `fixtures/protected_must_keep.json` must never become `delete_candidate`.

Prefer `keep` or `ablegen` when unsure. The cost of a wrong delete is the whole product.

## Never

- Add live-mail or credential handling, or real personal/work data.
- Weaken `HARD_PROTECTED_CATEGORIES`.
- Set `default_action: delete_candidate` or disable human review.
- Trade away a safety test for a clever promo rule.
- Auto-promote archive/keep to `ablegen` just because a body mentions “invoice”. Veto is for *delete* collisions.

## Commands

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
klarpost validate -p policies/packs/<pack>.yaml
klarpost evaluate -p policies/packs/<pack>.yaml -f fixtures/protected_must_keep.json --fail-on-delete
klarpost evaluate -p policies/packs/<pack>.yaml -f fixtures/inbox_mixed.json
klarpost explain -p policies/packs/inbox-calm.yaml -f fixtures/inbox_mixed.json -m fx-order-promo-collision
klarpost demo -p policies/packs/inbox-calm.yaml -f fixtures/inbox_mixed.json
```

## Codex workflow

Codex may propose rules, edge cases, fixtures, and clearer reasons. It must read this file and `DESIGN.md`, keep the diff narrow, and show policy plus fixtures together. It must not invent mailbox behavior, credentials, or deletion workflows. If intent is ambiguous, keep the message visible and document uncertainty.

Maintainers review policy, precedence, fixture output, safety rail, attention cost, and docs — not only green CI.

## Adding a delete rule

1. Write the YAML rule as `delete_candidate` with a one-line English `reason`.
2. Add a promo fixture that does **not** contain protected phrases.
3. Add a collision fixture (`Your order #… 20% off`, invoice + sale, tax notice + flash sale).
4. Run `pytest` and `--fail-on-delete` on the protected set.
5. If CI is red, the rule is wrong — do not skip `tests/test_safety.py`.

## Labels

Use `good first issue`, `safety`, `policy-pack`, or `docs`. Reproduce with synthetic data only. Park live-connector requests.
