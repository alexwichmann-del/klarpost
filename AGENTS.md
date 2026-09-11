# AGENTS.md — maintainer contract

Working agreement for humans and coding agents maintaining klarpost. It is policy-as-code for personal mail hygiene, not a mailbox connector.

## North star

- Explain why mail was filed, archived, kept, or only suggested for deletion.
- Protect orders, invoices, receipts, tickets, travel, banking, security, government, medical, legal, and identity mail: never `delete_candidate`.
- Keep the CLI fixtures-only: no IMAP, SMTP, OAuth, tokens, credentials, or personal mail.
- Write docs, issues, PRs, CLI help, reasons, comments, and tests in English first; matcher keywords may include other languages.

ADHD and high-sensory-load framing is honest context, not a universal-accessibility claim.

## Do

- Review policy diffs as safety changes.
- Add a synthetic fixture for ambiguous matcher collisions.
- Preserve `ablegen` > `archive` > `keep` > `delete_candidate`.
- Keep explanations useful: rule id, reason, action, safety veto.

## Never

- Add live-mail or credential handling, or real personal/work data.
- Weaken `HARD_PROTECTED_CATEGORIES`.
- Set `default_action: delete_candidate` or disable human review.
- Trade away a safety test for a clever promo rule.

## Review

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
klarpost validate -p policies/packs/<pack>.yaml
klarpost evaluate -p policies/packs/<pack>.yaml -f fixtures/protected_must_keep.json --format json
```

Check schema, unique ids, non-empty matches, plain-English reasons, and zero delete candidates in protected fixtures. Each delete rule needs a clean promo fixture and a collision case. Rails are a backstop, not permission to ship sloppy rules.

Use `good first issue`, `safety`, `policy-pack`, or `docs`. Reproduce with synthetic data only; park live-connector requests. Prefer `keep` or `ablegen` when unsure: the cost of a wrong delete is the whole product.
