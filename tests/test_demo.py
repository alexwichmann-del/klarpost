from pathlib import Path

from klarpost.cli import main
from klarpost.demo import main as demo_main

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies" / "packs" / "inbox-calm.yaml"
MIXED = ROOT / "fixtures" / "inbox_mixed.json"


def test_demo_prints_attention_budget(capsys):
    assert demo_main(["-p", str(POLICY), "-f", str(MIXED)]) == 0
    out = capsys.readouterr().out
    assert "attention budget: 15/30" in out
    assert "No mailbox was opened" in out
    assert "SAFETY RAIL" in out


def test_cli_demo_subcommand(capsys):
    assert main(["demo", "-p", str(POLICY), "-f", str(MIXED)]) == 0
    out = capsys.readouterr().out
    assert "attention budget: 15/30" in out
    assert "klarpost demo" in out
