import json
from pathlib import Path

from klarpost.schema import policy_json_schema

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "policies" / "policy.schema.json"


def test_committed_schema_matches_export():
    committed = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert committed == policy_json_schema()
