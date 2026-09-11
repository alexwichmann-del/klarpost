import json
from pathlib import Path

from klarpost.cli import main

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "packs" / "inbox-calm.yaml"
PROTECTED = ROOT / "fixtures" / "protected_must_keep.json"
MIXED = ROOT / "fixtures" / "inbox_mixed.json"


def test_evaluate_json_on_protected_has_no_deletes(capsys):
    code = main(
        [
            "evaluate",
            "--policy",
            str(POLICY),
            "--fixtures",
            str(PROTECTED),
            "--format",
            "json",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload
    assert all(row["action"] != "delete_candidate" for row in payload)


def test_evaluate_table_mentions_summary(capsys):
    code = main(["evaluate", "-p", str(POLICY), "-f", str(MIXED)])
    assert code == 0
    out = capsys.readouterr().out
    assert "summary:" in out
    assert "ablegen=" in out


def test_validate_ok(capsys):
    assert main(["validate", "-p", str(POLICY)]) == 0
    assert "ok:" in capsys.readouterr().out


def test_schema_command(capsys):
    assert main(["schema"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert "properties" in schema


def test_explain_one_message(capsys):
    code = main(
        [
            "explain",
            "-p",
            str(POLICY),
            "-f",
            str(MIXED),
            "--message-id",
            "fx-order-promo-collision",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["action"] == "ablegen"
    assert payload["safety_veto"] is True


def test_missing_message_id(capsys):
    code = main(["explain", "-p", str(POLICY), "-f", str(MIXED), "-m", "nope"])
    assert code == 1
    assert "no fixture" in capsys.readouterr().err


def test_refuses_imap_flag(capsys):
    code = main(["evaluate", "--imap", "mail.example", "-p", str(POLICY), "-f", str(MIXED)])
    assert code == 2
    err = capsys.readouterr().err
    assert "refuses live-mail" in err
    assert "--imap" in err


def test_refuses_password_flag(capsys):
    assert main(["evaluate", "--password", "secret", "-p", "x", "-f", "y"]) == 2
    assert "refuses" in capsys.readouterr().err


def test_invalid_policy_path():
    assert main(["validate", "-p", str(ROOT / "does-not-exist.yaml")]) == 1
