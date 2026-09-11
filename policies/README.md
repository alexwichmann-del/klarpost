# Policy packs

A pack is a YAML file a human can read in one sitting. The engine still applies
**hard safety rails**: protected categories can never become `delete_candidate`,
even if a rule is sloppy.

## Actions (priority)

1. `ablegen` — file the paper trail (receipts, invoices, tickets, …)
2. `archive` — leave the inbox, keep the message
3. `keep` — stay in the inbox; do not guess
4. `delete_candidate` — **suggestion only**. A human still decides. klarpost
   never deletes.

## Authoring rules

- Every rule needs a stable `id`, a non-empty `match`, a `classify`, an
  `action`, and a one-line English `reason`. Matcher keywords may include
  other locales.
- `match_mode: any_field` (default) fires when any filled matcher hits.
  Use `all_fields` when you need several signals together.
- Do not classify a protected category as `delete_candidate`. Validation fails.
- Do not put protected phrases (`invoice`, `boarding pass`, `steuerbescheid`, …)
  in a delete rule's matchers. Validation fails.
- Do not set `safety.default_action: delete_candidate`. Validation fails.
- `require_human_review_for_delete` must stay `true`.

## Test a pack

```bash
klarpost validate --policy policies/packs/inbox-calm.yaml
klarpost evaluate --policy policies/packs/inbox-calm.yaml \
  --fixtures fixtures/protected_must_keep.json --fail-on-delete
```

`fixtures/protected_must_keep.json` must produce **zero** `delete_candidate`
rows. CI enforces this.

Attention cost is part of the evaluate JSON (`attention_cost`). Protected mail
that is filed pays `1`. See [DESIGN.md](../DESIGN.md).
