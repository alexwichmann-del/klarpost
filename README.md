# klarpost

**Policy-as-code for inbox attention and deletion safety.**

Spam filters guess. **klarpost makes attention and deletion policy explicit and testable.** Reviewable YAML names matchers, precedence, actions, and reasons. The runner uses synthetic fixtures only: no mailbox, credentials, or deletion.

## Architecture

![klarpost architecture](docs/assets/architecture.svg)

The deterministic evaluator returns `keep`, `archive`, or `delete-candidate`; the last is only a human-review suggestion. Consequential mail is protected by a hard safety rail.

## Thesis

A newsletter and an invoice are both messages, but losing the invoice costs more than reading one extra newsletter. ML filters hide that trade-off in a score; klarpost puts it in versioned text. Attention is a budget; deletion is asymmetric.

## Sacred receipts manifesto

Receipts are evidence, not clutter. **Preserve the paper trail before optimizing for quiet.** Prefer a visible false negative to an irreversible mistake. See `fixtures/protected_must_keep.json`.

| Concern | ML | klarpost |
|---|---|---|
| Decision | Score | YAML rule |
| Deletion | May follow | Never |
| Audit | Opaque | Diffable |

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -e '.[dev]'
klarpost demo
klarpost validate --policy policies/packs/inbox-calm.yaml
klarpost evaluate --policy policies/packs/inbox-calm.yaml --fixtures fixtures/inbox_mixed.json
```

## Codex maintainer workflow

Read [`AGENTS.md`](AGENTS.md). Policy changes ship with positive, near-miss, and protected-collision fixtures. Keep reasons English-first; run `pytest`, `ruff check src tests`, and validation. CI enforces the protected-fixture invariant. Review precedence, action, reason, and rail. See [`DESIGN.md`](DESIGN.md).

Fixture-only software; preserve the no-live-mail boundary.

*DE: „klar“ heißt clear; der Name bleibt bewusst `klarpost`.*
