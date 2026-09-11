# Design notes: a calmer boundary

`klarpost` is not a smarter spam filter. It is a small, inspectable boundary between an inbox and an irreversible decision.

## Start with attention, not volume

An inbox consumes attention before storage. A message can be harmless and still be expensive to notice, interpret, and remember. We optimize for recoverability: fewer decisions, clearer reasons, and no surprise deletion.

ADHD and high-sensory-load workflows are useful constraints because they expose hidden costs. They are not a diagnosis, a promise of universal accessibility, or a claim that one inbox fits everyone.

## Make the nervous system explicit

A policy pack is a deliberately boring nervous system: notice a signal, name a category, choose an action, explain the choice, then apply a veto. YAML lets a human review the diff; the runner tests that diff against fixtures.

The ladder is conservative: file the paper trail, archive low-urgency mail, keep uncertainty visible, then suggest a candidate. A suggestion is not an instruction. The engine never connects to a mailbox or executes deletion.

## Receipts over cleverness

A receipt is the rule id, action, reason, and any safety veto. Someone can understand it later, challenge it, and improve the pack without guessing. Protected categories are a hard floor: marketing language must not erase an order confirmation. When signals collide, the paper trail wins; when they are ambiguous, keep the message.

## Small surface area is a feature

Synthetic fixtures keep review safe and reproducible. Packs keep behavior legible. Tests are executable promises about what klarpost will never do. New cleverness should arrive as a small rule, a fixture, and an explanation.

Treat inbox hygiene as a safety-critical attention interface, then keep the implementation humble enough to audit on a tired Sunday.
