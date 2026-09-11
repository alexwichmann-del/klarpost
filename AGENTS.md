# AGENTS.md — maintainer workflows (Codex and humans)

This file is the contract for coding agents that help maintain klarpost
(OpenAI Codex, similar review bots, or a tired human on a Sunday).

klarpost is **policy-as-code for personal email hygiene**. The interesting
work is reviewing YAML packs and safety tests — not connecting a mailbox.

## North star

1. People with ADHD / high sensory load should be able to *read* why a
   message would be filed, archived, or only *suggested* for deletion.
2. Orders, invoices, receipts, tickets, banking, and security mail are
   never `delete_candidate`.
3. The reference CLI stays **fixtures-only**. No IMAP, SMTP, OAuth, tokens,
   or personal mail samples.
4. **English first.** README, CONTRIBUTING, issues, PR text, CLI help,
   rule `reason` strings, and code comments are written in English.
   Matcher keywords may include other locales (e.g. `rechnung`). A short
   optional German section at the end of the README is fine.

## What you may do

- Review policy-pack PRs against the checklist below
- Add fixtures and pytest coverage when a rule is ambiguous
- Improve `evaluate` / `explain` output (still local files)
- Triage issues (`good first issue`, `safety`, `policy-pack`, `docs`)
- Propose copy that stays honest: this is alpha, not a popular product

## What you must never do

- Add a live mail client, credential flag, or `.env` mail password
- Commit real From/To addresses, phone numbers, or account identifiers
- Delete or narrow `HARD_PROTECTED_CATEGORIES` in `src/klarpost/safety.py`
- Set `require_human_review_for_delete: false` or default `delete_candidate`
- Trade a red safety test for a "smarter" promo rule
- Mention or import anything from private personal/work tooling

## Policy PR review checklist

Run from the repo root after `pip install -e ".[dev]"`:

```bash
pytest
ruff check src tests
klarpost validate --policy policies/packs/<pack>.yaml
klarpost evaluate --policy policies/packs/<pack>.yaml \
  --fixtures fixtures/protected_must_keep.json --format json
```

Then read the diff as a safety review:

1. **Schema** — `version: 1`, unique rule ids, non-empty `match`, human
   `reason` strings.
2. **Ladder** — file (`ablegen`) beats archive beats keep beats
   delete-candidate. A colliding order+promo rule must still file.
3. **Protected fixture** — zero `delete_candidate` rows on
   `fixtures/protected_must_keep.json`.
4. **New delete rules** — each one has a *clean* promo fixture (no invoice /
   order / ticket / bank / 2FA language) *and* you thought about a collision
   case.
5. **Locale** — DE/EN phrases are fine; do not assume one language covers
   safety. Keyword rails in `safety.py` already cover both for the hard set.
6. **Honesty** — PR description does not claim auto-delete or production
   IMAP support.

If the pack is sloppy but the engine vetoes the delete, **do not merge**
until the pack itself is corrected. Rails are a backstop, not a style guide.

## Issue triage (Codex)

- `safety` / "this would have deleted my invoice" → reproduce with a
  **synthetic** fixture, add a test, keep the rail. Never ask the reporter
  to paste a real email.
- Feature requests for IMAP → politely close or park as out of scope;
  point at fixtures. Do not scaffold a connector "just for local use".
- `good first issue` → keep the task smaller than one evening: a pack, a
  handful of fixtures, or a CLI output tweak.
- Duplicate pack ideas → ask for a fixture that today's packs get wrong.

## CI contract

`.github/workflows/ci.yml` must stay red when:

- pytest fails (especially `tests/test_safety.py`)
- ruff fails
- a sample pack fails `klarpost validate`
- protected fixtures emit `delete_candidate`

Do not skip CI with `continue-on-error` on those jobs.

## Review comments that help

Good: "This subject matcher also hits `Your order #… 30% off`. Add that
fixture; expected action is `ablegen`."

Bad: "Make delete the default so the inbox is emptier."

## When you are unsure

Prefer `keep` or `ablegen` over `delete_candidate`. File a follow-up issue
instead of guessing. The cost of a wrong delete is the whole product.
