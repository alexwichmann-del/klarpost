# Changelog

## Unreleased

- Attention cost is a first-class, deterministic field on every evaluation
  (`ablegen`/`archive` = 1, `delete_candidate` = 2, `keep` = 3). CLI, JSON,
  demo, and `tests/test_attention.py` share one table.
- Never-delete rails cover travel, legal, and government signals; delete rules
  that *name* protected phrases fail validation; a delete/protected collision
  files the message (`ablegen`) and records a veto.
- `klarpost evaluate --fail-on-delete`, `klarpost explain` (text receipt),
  and `klarpost demo` for maintainer / Codex workflows.
- Docs and SVG diagrams rewritten English-first (`architecture.svg` plus
  evaluation / ladder / mark). `ablegen` remains the file token. Project
  URLs point at `clearmind93/klarpost`.

## 0.1.0 — 2026-09-11

First public alpha.

- Policy pack schema (`version: 1`) with validator and JSON Schema export
- Hard safety rails: protected categories cannot become `delete_candidate`
- Reference CLI: `klarpost evaluate|validate|explain|schema` (fixtures only)
- Sample packs: `protected-only`, `receipts-first`, `inbox-calm`
- Synthetic fixtures and pytest coverage, including safety vetoes
- GitHub Actions CI on Python 3.11–3.13
