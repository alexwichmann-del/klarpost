from pathlib import Path

import pytest

from klarpost.policy import PolicyError, load_policy, parse_policy
from klarpost.schema import policy_json_schema

PACK_DIR = Path(__file__).resolve().parents[1] / "policies" / "packs"


@pytest.mark.parametrize("name", ["inbox-calm.yaml", "receipts-first.yaml", "protected-only.yaml"])
def test_sample_packs_validate(name: str):
    pack = load_policy(PACK_DIR / name)
    assert pack.version == 1
    assert pack.rules
    assert pack.safety.require_human_review_for_delete is True


def test_duplicate_rule_ids_rejected():
    with pytest.raises(PolicyError, match="duplicate"):
        parse_policy(
            {
                "version": 1,
                "id": "dupes",
                "name": "Dupes",
                "description": "Two rules share an id.",
                "safety": {"require_human_review_for_delete": True},
                "rules": [
                    {
                        "id": "same",
                        "match": {"subject_contains": ["a"]},
                        "classify": "promo",
                        "action": "archive",
                        "reason": "one",
                    },
                    {
                        "id": "same",
                        "match": {"subject_contains": ["b"]},
                        "classify": "promo",
                        "action": "archive",
                        "reason": "two",
                    },
                ],
            }
        )


def test_empty_match_rejected():
    with pytest.raises(PolicyError, match="empty match"):
        parse_policy(
            {
                "version": 1,
                "id": "empty",
                "name": "Empty",
                "description": "Rule with no matchers.",
                "safety": {"require_human_review_for_delete": True},
                "rules": [
                    {
                        "id": "blank",
                        "match": {},
                        "classify": "promo",
                        "action": "archive",
                        "reason": "no matchers",
                    }
                ],
            }
        )


def test_unknown_version_rejected():
    with pytest.raises(PolicyError):
        parse_policy(
            {
                "version": 2,
                "id": "future",
                "name": "Future",
                "description": "Unsupported version.",
                "rules": [],
            }
        )


def test_json_schema_export_has_title_and_actions():
    schema = policy_json_schema()
    assert schema["title"] == "klarpost policy pack"
    dumped = str(schema)
    assert "ablegen" in dumped
    assert "delete_candidate" in dumped
