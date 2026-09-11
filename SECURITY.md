# Security

klarpost is a **local, fixtures-only evaluator**. It does not connect to a mailbox and must not grow credential handling without a dedicated design review.

The serious bugs here are not “it did not delete enough.” They are ways the engine could recommend deleting mail that is a record.

## Threat model (alpha)

| In scope | Out of scope |
| --- | --- |
| A pack or the engine marking protected mail as `delete_candidate` | “Please add IMAP” |
| Delete rules that name protected signals in matchers | Taste debates about archive vs keep |
| Weakening `HARD_PROTECTED_CATEGORIES` | Missing connectors |
| Path traversal or reads outside the paths you passed | Delivered-mail parsing of a live mailbox |
| Logging or committing personal mailbox data | |

Protected categories: orders, invoices, receipts, tickets, travel, banking, security, government, medical, legal, identity.

## Please report

- Policy-bypass: protected fixture → `delete_candidate`
- Validation bypass: pack sets `default_action: delete_candidate` or `require_human_review_for_delete: false` and still loads
- Unexpected file reads
- Anything that would cause real mailbox contents to land in logs, fixtures, or git

## Please do not report

- “It does not delete enough mail” — product taste, not a vulnerability
- Missing IMAP/SMTP/OAuth — intentional
- Keyword rails missing a phrase — open a `safety` issue with a **synthetic** fixture; that is a test gap, not an advisory unless a sample pack already deletes that fixture

## How to report

Use GitHub’s **private vulnerability report** on this repository (Security → Report a vulnerability) if it is available. Otherwise open an issue titled `security: …` **without** pasting real email contents.

Engine bypasses are P0: add a fixture and a test before any other change. CI’s `--fail-on-delete` gate on `fixtures/protected_must_keep.json` is the regression lock.
