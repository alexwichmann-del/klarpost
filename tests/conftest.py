from pathlib import Path

import pytest

from klarpost.fixtures import load_fixtures
from klarpost.policy import load_policy

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "policies" / "packs"
FIXTURES = ROOT / "fixtures"


@pytest.fixture
def inbox_calm():
    return load_policy(PACKS / "inbox-calm.yaml")


@pytest.fixture
def receipts_first():
    return load_policy(PACKS / "receipts-first.yaml")


@pytest.fixture
def protected_only():
    return load_policy(PACKS / "protected-only.yaml")


@pytest.fixture
def mixed_messages():
    return load_fixtures(FIXTURES / "inbox_mixed.json")


@pytest.fixture
def protected_messages():
    return load_fixtures(FIXTURES / "protected_must_keep.json")


@pytest.fixture
def promo_messages():
    return load_fixtures(FIXTURES / "promo_noise.json")
