# AGENTS.md — maintainer contract

Working agreement for humans and coding agents maintaining klarpost. It is policy-as-code for personal mail hygiene, not a mailbox connector.

## Non-negotiables

- Protect the paper trail. Orders, invoices, receipts, tickets, travel, banking, security, government, medical, legal, and identity mail never become `delete-candidate`.
- `delete-candidate` is a human-review suggestion, never an executed delete.
- Keep the CLI fixture-only: no IMAP, SMTP, OAuth, tokens, credentials, or personal mail.
- Write docs, reasons, comments, tests, and PR text in English first. Keep the name `klarpost`.

## Review every policy-pack PR

1. **State intent.** Say what attention cost changes and why the action is safer.
2. **Inspect precedence.** Read the full pack; confirm safety matches cannot be shadowed and ties are deterministic.
3. **Require fixtures.** Add a positive case, near miss, and protected collision where relevant. Use synthetic, reserved example data.
4. **Check the receipt.** Results expose rule, category, action, safety decision, and a plain-English reason.
5. **Run gates.** Run `pytest`, `ruff check src tests`, and policy validation. Confirm `fixtures/protected_must_keep.json` never becomes delete-candidate.

## Codex workflow

Codex may propose rules, edge cases, fixtures, and clearer reasons. It must read this file and `DESIGN.md`, keep the diff narrow, and show policy plus fixtures together. It must not invent mailbox behavior, credentials, or deletion workflows. If intent is ambiguous, keep the message visible and document uncertainty.

Maintainers review policy, precedence, fixture output, safety rail, and docs—not only green CI. Changes that weaken a rail, hide a reason, or use live-mail data are out of scope.
