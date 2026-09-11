# klarpost

**Policy-as-code for personal email hygiene.**

You can drown in newsletters and promo mail and still need the one invoice,
boarding pass, or bank notice that arrived the same hour. Spam filters guess.
klarpost makes the *rules* readable, reviewable, and biased toward **not
losing the paper trail**.

This repository is an **early-stage** open-source project (alpha `0.1.0`).
There is no hosted product, no user metrics to show, and no live mailbox
integration. The reference CLI evaluates **synthetic fixtures only**.

[![CI](https://github.com/alexwichmann-del/klarpost/actions/workflows/ci.yml/badge.svg)](https://github.com/alexwichmann-del/klarpost/actions/workflows/ci.yml)

## What it is

- Human-readable **YAML policy packs** (`policies/packs/`)
- A fixed action ladder: **Ablegen / Belege → archive → keep → delete-candidate**
- **Hard safety rails** in the engine: orders, invoices, receipts, tickets,
  banking, and security mail cannot become delete-candidates — even if a pack
  is sloppy
- Sample packs + fixture inboxes + pytest, so a change is a diff you can read
- A reference CLI: `klarpost evaluate` (fixtures only)

## What it is not

- Not a spam filter and not a replacement for your mail host
- Not an IMAP/SMTP client (and it will **refuse** credential-shaped flags)
- Not an auto-delete robot. `delete_candidate` is a suggestion. A human still
  decides.
- Not trained on anyone's real inbox. Fixtures use `example.com` and reserved
  names only.

## Why this exists

Inbox tools optimized for "less mail" quietly fail people with ADHD or high
sensory load: the cost of a wrong delete is higher than the cost of a full
inbox. klarpost starts from the opposite default — **protect Belege first**,
then offer calmer archive / delete-candidate rules you can see.

If two rules collide (order confirmation + "20% off"), Ablegen wins.

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

klarpost validate --policy policies/packs/inbox-calm.yaml
klarpost evaluate --policy policies/packs/inbox-calm.yaml --fixtures fixtures/inbox_mixed.json
klarpost explain --policy policies/packs/inbox-calm.yaml \
  --fixtures fixtures/inbox_mixed.json --message-id fx-order-promo-collision
```

`fx-order-promo-collision` is an order confirmation that also looks like a
promo. Expected result: `ablegen` + a safety veto, not `delete_candidate`.

A rule is a few lines of YAML a tired human can audit:

```yaml
- id: ablegen-invoices
  priority: 90
  match:
    subject_contains: [invoice, receipt, rechnung, beleg]
  classify: invoice
  action: ablegen
  reason: Belege first — invoices and receipts stay.
```

## Actions

| Action | Meaning |
| --- | --- |
| `ablegen` | File / keep the paper trail (Belege). Highest priority. |
| `archive` | Leave the inbox, keep the message. |
| `keep` | Stay put. Used when nothing reliable matched. |
| `delete_candidate` | Suggestion only. Never executed by this engine. |

## Safety rails (non-negotiable)

The engine **unions** every pack's `never_delete_categories` with a hard set:

`order`, `invoice`, `receipt`, `ticket`, `travel`, `banking`, `security`,
`government`, `medical`, `legal`, `identity`

Packs may add categories. They may not remove these, default to
`delete_candidate`, or set `require_human_review_for_delete: false`.
Validation fails. Keyword rails still run even when no rule matches.

CI evaluates `fixtures/protected_must_keep.json` against every sample pack and
fails if any row is `delete_candidate`.

## Sample packs

| Pack | Intent |
| --- | --- |
| [`policies/packs/protected-only.yaml`](policies/packs/protected-only.yaml) | Only Ablegen rules. Everything else stays `keep`. |
| [`policies/packs/receipts-first.yaml`](policies/packs/receipts-first.yaml) | Ablegen + archive newsletters. No delete-candidates. |
| [`policies/packs/inbox-calm.yaml`](policies/packs/inbox-calm.yaml) | Ablegen + archive + obvious promo delete-candidates. |

Write a pack: [policies/README.md](policies/README.md).

## Tests

```bash
pytest
ruff check src tests
```

Safety tests live in `tests/test_safety.py`. If you add a `delete_candidate`
rule, add a fixture that proves it does **not** collide with protected
signals.

## Deutsch (kurz)

klarpost ist **Policy-as-Code für persönliche Mail-Hygiene**: Newsletter dürfen
ruhig raus aus dem Posteingang — **Bestellungen, Rechnungen, Tickets, Bank-
und Sicherheitsmails werden nicht zum Löschkandidaten**. Die Reihenfolge ist
fest: **Ablegen / Belege → Archiv → Behalten → Löschkandidat**. Die
Referenz-CLI arbeitet nur mit synthetischen Fixtures, nie mit einem echten
Postfach oder Zugangsdaten. Das Projekt ist bewusst früh (Alpha), ohne
gehostetes Produkt.

## Good first issues

These are real, small, and useful. Open a PR; mention the number if you file
an issue first.

1. **Locale pack (DE newsletter phrases)** — add `policies/packs/inbox-calm.de.yaml`
   plus 3–5 fixtures. Must still pass `protected_must_keep.json`.
2. **Calendar-invite fixture** — a synthetic `.ics` / "invitation" message and
   a rule that *keeps* or Ablegen it (never delete-candidate).
3. **Safer promo phrases** — extend `inbox-calm` delete-candidate matchers
   with more obvious marketing copy, each backed by a fixture that has **no**
   protected keywords.
4. **Explain output** — make `klarpost explain` print a short prose paragraph
   above the JSON (still fixture-only).
5. **JSON Schema in-repo** — commit `policies/policy.schema.json` generated
   from `klarpost schema` and wire a CI drift check.

Labels we use when triaging: `good first issue`, `safety`, `policy-pack`,
`docs`. See [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md)
(maintainer / Codex workflow).

## Status

Alpha. The useful artifact today is the **policy format + safety tests**, not
a desktop mail client. Live connectors are out of scope until the rails have
more eyes on them.

## License

[MIT](LICENSE)
