# Contributing to klarpost

Thanks for wanting to help. This project is early. Small, testable changes
beat large rewrites.

## Ground rules

1. **No live mail.** Do not add IMAP, SMTP, OAuth, or credential flags.
   The CLI must keep refusing them.
2. **No personal data.** Fixtures use `example.com`, `example.org`,
   `example.net`, and reserved names. No real addresses, phones, or account
   numbers.
3. **Safety rails are not optional.** Do not weaken `HARD_PROTECTED_CATEGORIES`
   or skip `tests/test_safety.py` to make a pack "more aggressive".
4. **`delete_candidate` is not delete.** Copy and tests should say so.

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
- Every `delete_candidate` rule needs a fixture that does **not** match
  protected keyword rails, plus a protected collision fixture if the phrases
  could overlap.
- Run:

  ```bash
  klarpost validate --policy policies/packs/<your-pack>.yaml
  klarpost evaluate --policy policies/packs/<your-pack>.yaml \
    --fixtures fixtures/protected_must_keep.json --format json
  ```

  The protected fixture file must contain **zero** `delete_candidate` actions.
- Fill in the PR template. If CI is red, fix it before asking for review.

## Policy pack review (humans and Codex)

Maintainers treat pack PRs as **safety reviews**, not style bikesheds. The
checklist is in [AGENTS.md](AGENTS.md). Short version:

- Schema valid
- Hard rails still on
- Protected fixtures stay non-delete
- Reasons are sentences a tired human can read

## Issues

Use the issue templates. Security / policy-bypass reports: see
[SECURITY.md](SECURITY.md). Code of conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
