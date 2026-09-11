# Design notes

klarpost is a small, inspectable boundary between an inbox and an irreversible decision. It is not a smarter spam filter, not a mailbox product, and not a promise that one policy fits everyone.

## Attention is the scarce resource

Email is not only storage. It is attentional load: every message can demand noticing, interpretation, a decision, and later recall. A quiet inbox is not necessarily a safe inbox. The cost of a wrong deletion is higher than one extra review.

ADHD and high-sensory-load workflows are useful constraints because they expose that cost. They are not a diagnosis and not a claim of universal accessibility.

## Make the boundary explicit

Spam filters optimize a broad probability of unwanted mail. klarpost makes the local trade-off inspectable. A policy pack names the signal, category, action, precedence, and reason. The evaluator is deterministic: the same fixture and pack produce the same receipt.

```
fixture → match YAML rules → match keyword rails → choose by action priority
        → if delete_candidate ∩ protected: file (ablegen) + veto
        → emit receipt {action, category, rules, reasons, veto, attention_cost}
```

YAML is the part a human can review in a diff. The runner is the part a pack author cannot waive. Hard rails live in `klarpost.safety`, not in comments.

The ladder is conservative: file the paper trail, archive low-urgency mail, keep uncertainty visible, then maybe suggest a candidate. A suggestion is not an instruction. The engine never connects to a mailbox and never deletes.

`ablegen` stays as the file token because packs and tests already depend on it. English docs say “file”. Matcher keywords may include other languages; user-facing reasons, CLI help, and docs do not switch language mid-sentence.

## Four layers, one invariant

Protected categories (orders, invoices, receipts, tickets, travel, banking, security, government, medical, legal, identity) must never emerge as `delete_candidate`.

1. **Validate the pack.** No empty matchers, no duplicate ids, no `default_action: delete_candidate`, no `require_human_review_for_delete: false`, no delete rule that *classifies* or *names* a protected signal.
2. **Scan the message.** Conservative EN/DE phrases, fixtures-only — not a spam model.
3. **Veto at runtime.** A sloppy “flash sale” rule that also hits `Steuerbescheid 2024 — flash sale` files the tax notice and records a veto. A newsletter that merely *mentions* “no invoice” is not an invoice; archive/keep are left alone.
4. **CI the invariant.** `--fail-on-delete` on `fixtures/protected_must_keep.json` for every sample pack.

Rails are a backstop, not permission to ship sloppy rules. Each delete rule still needs a clean promo fixture and a collision case.

## Attention cost is a test, not a vibe

`klarpost.attention` maps the final action to `{1, 2, 3}`. File and archive are cheap because they are decided. `keep` is expensive because it still occupies the inbox. `delete_candidate` sits in the middle because a human still has to look.

The number is deterministic. Tests freeze it (`15/30` on the mixed demo inbox). It is not telemetry, not a ranking model, and not a reason to auto-delete.

## What Codex is for

Codex can propose matchers, enumerate edge cases, write fixture coverage, and clarify reasons. It should act like a careful maintainer: read `AGENTS.md`, keep the diff narrow, and show policy plus fixtures together. It is not the authority that decides what a person may lose.

A good PR pairs a policy change with a positive fixture, a near miss, and a protected collision where relevant. CI checks the invariant; human review checks whether the rule expresses the intended attention policy.

## Small surface area is a feature

Synthetic fixtures keep review safe and reproducible. Packs keep behavior legible. Tests are executable promises about what klarpost will never do.

What we refuse to grow without a dedicated design review: IMAP, SMTP, OAuth, tokens, credential flags, personal mailbox samples, silent deletion, and a default-delete pack.

Treat inbox hygiene as a safety-critical attention interface, then keep the implementation humble enough to audit on a tired Sunday.
