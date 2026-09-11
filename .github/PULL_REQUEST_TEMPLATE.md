## What

<!-- Pack, fixture, CLI, or docs. One concern if you can. -->

## Safety

- [ ] I did not add IMAP/SMTP/OAuth/credential handling
- [ ] Fixtures use example.com (or other reserved names) only
- [ ] `fixtures/protected_must_keep.json` still has zero `delete_candidate` rows for every sample pack
- [ ] New `delete_candidate` rules have a clean promo fixture **and** I thought about order/invoice collisions
- [ ] I did not narrow `HARD_PROTECTED_CATEGORIES`
- [ ] User-facing copy (reasons, docs, comments) is English first

## How I checked

```bash
pytest
klarpost validate --policy policies/packs/<pack>.yaml
```

## Notes for Codex / reviewers

<!-- Anything a safety-first review should stare at. -->
