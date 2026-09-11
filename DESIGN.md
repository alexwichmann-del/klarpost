# Design: attention is the scarce resource

Email is not only storage or classification. It is attentional load: every message can demand noticing, interpretation, a decision, and later recall. A quiet inbox is not necessarily a safe inbox. The cost of wrong deletion is often higher than one extra review.

## Make the boundary explicit

Spam filters optimize a broad probability of unwanted mail. klarpost makes the local trade-off inspectable. A policy pack names the signal, category, action, precedence, and reason. The evaluator is deterministic, so the same fixture and policy produce the same receipt. When no rule earns confidence, uncertainty remains visible and the message stays available.

The safety rail is stronger than a matcher. Orders, invoices, receipts, tickets, travel, banking, security, government, medical, legal, and identity mail are consequential evidence. They must not become `delete-candidate` because a broad low-value rule matched. That action is a review queue, never an erase instruction.

## Why deterministic rails

Determinism is a social feature. A maintainer can diff a policy, add a fixture, reproduce a result, and explain the reason without reconstructing a model's hidden state. Conservative precedence makes irreversible mistakes hard to express. Synthetic fixtures keep the runner outside live-mail and credential workflows.

## What Codex is for

Codex can propose matchers, enumerate edge cases, write fixture coverage, and clarify reasons. It should act like a careful maintainer: read `AGENTS.md`, preserve the sacred rail, and show its work in a small diff. It is not the authority that decides what a person may lose.

A good PR pairs a policy change with a positive fixture, a near miss, and a protected collision where relevant. CI checks the invariant; human review checks whether the rule expresses the intended attention policy. This keeps the system useful, legible, and reversible.
