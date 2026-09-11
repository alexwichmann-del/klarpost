# Contributing

Small, testable changes beat large rewrites. Policy diffs are safety reviews.

The maintainer contract — including the Codex/agent checklist — is [AGENTS.md](AGENTS.md). Read that first.

## Ground rules

1. **No live mail.** Do not add IMAP, SMTP, OAuth, or credential flags. The CLI must keep refusing them (exit 2).
2. **No personal data.** Fixtures use `example.com` / `example.org` / `example.net` and reserved names.
3. **Safety rails are not optional.** Do not weaken `HARD_PROTECTED_CATEGORIES` or skip `tests/test_safety.py`.
4. **`delete_candidate` is not delete.** Copy and tests should say so.
5. **English first.** Docs, issue/PR text, CLI help, rule `reason` strings, and comments are English. Matcher keywords may include other locales. `ablegen` stays as the file token.
6. **README diagrams are PNG.** SVGs in `docs/assets/` are the source. GitHub mobile dropped some SVGs (invalid Latin-1 `·` bytes / sanitizer). After editing an SVG, run `docs/assets/render-png.sh` and keep the README pointing at the `.png`.

## Dev setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

Python 3.11+ is required.

## Pull requests

- One concern per PR (pack, fixture set, CLI, docs).
- Every `delete_candidate` rule needs a fixture that does **not** match protected keyword rails, plus a protected collision fixture if the phrases could overlap.
- Run:

  ```bash
  klarpost validate -p policies/packs/<your-pack>.yaml
  klarpost evaluate -p policies/packs/<your-pack>.yaml \
    -f fixtures/protected_must_keep.json --fail-on-delete
  ```

- Fill in the PR template. If CI is red, fix it before asking for review.

## Issues

Use the issue templates. Security / policy-bypass reports: [SECURITY.md](SECURITY.md). Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
