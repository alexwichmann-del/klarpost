# Changelog

## 0.1.0 — 2026-09-11

First public alpha.

- Policy pack schema (`version: 1`) with validator and JSON Schema export
- Hard safety rails: protected categories cannot become `delete_candidate`
- Reference CLI: `klarpost evaluate|validate|explain|schema` (fixtures only)
- Sample packs: `protected-only`, `receipts-first`, `inbox-calm`
- Synthetic fixtures and pytest coverage, including safety vetoes
- GitHub Actions CI on Python 3.11–3.13
