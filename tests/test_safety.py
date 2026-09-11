"""Hard rails: protected mail must never become a delete-candidate."""

from __future__ import annotations

import pytest

from klarpost.evaluate import evaluate_message, evaluate_messages
from klarpost.models import Action, Message, PolicyPack, Rule, SafetyConfig
from klarpost.policy import PolicyError, parse_policy, validate_policy
from klarpost.safety import (
    ALIASED_PROTECTED_CATEGORIES,
    HARD_PROTECTED_CATEGORIES,
    SCANNED_PROTECTED_CATEGORIES,
    enforce_protected_action,
    scan_message,
)


def _msg(**kwargs) -> Message:
    data = {
        "id": kwargs.pop("id", "m1"),
        "from": kwargs.pop("from_address", kwargs.pop("from", "noreply@shop.example")),
        "to": "you@example.com",
        "subject": "",
        "body_preview": "",
        "has_attachment": False,
    }
    data.update(kwargs)
    return Message.model_validate(data)


def test_hard_set_covers_paper_trail_and_security():
    required = {"order", "invoice", "receipt", "ticket", "banking", "security"}
    assert required <= HARD_PROTECTED_CATEGORIES


def test_every_hard_category_is_scanned_or_aliased():
    covered = SCANNED_PROTECTED_CATEGORIES | set(ALIASED_PROTECTED_CATEGORIES)
    missing = sorted(HARD_PROTECTED_CATEGORIES - covered)
    assert missing == []


@pytest.mark.parametrize(
    "subject,expected",
    [
        ("Invoice 12", "invoice"),
        ("Rechnung 9 / Beleg", "invoice"),
        ("Your order #99 has shipped", "order"),
        ("Boarding pass ready", "ticket"),
        ("Kontoauszug Januar", "banking"),
        ("Security alert: new sign-in", "security"),
        ("Password reset requested", "security"),
        ("Terminbestätigung + Befund", "medical"),
        ("Personalausweis copy", "identity"),
        ("Steuerbescheid 2025", "government"),
        ("Legal notice and court summons", "legal"),
        ("Hotel confirmation for Friday", "travel"),
    ],
)
def test_safety_scan_detects_protected_phrases(subject: str, expected: str):
    hits = scan_message(_msg(subject=subject))
    assert expected in {hit.category for hit in hits}


def test_invoice_plus_promo_language_is_ablegen(inbox_calm):
    message = _msg(
        id="collision",
        subject="Invoice 55 — 40% off your next order",
        body_preview="Flash sale language must not hide a receipt.",
    )
    result = evaluate_message(message, inbox_calm)
    assert result.action is Action.ABLEGEN
    assert result.category == "invoice"
    assert result.safety_veto is False or result.action is not Action.DELETE_CANDIDATE


def test_order_with_list_unsubscribe_is_not_deleted(inbox_calm):
    message = _msg(
        id="order-unsub",
        subject="Your order #4821 — 20% off next time",
        headers={"list-unsubscribe": "<mailto:unsub@shop.example>"},
        body_preview="Tracking number and a flash sale.",
    )
    result = evaluate_message(message, inbox_calm)
    assert result.action is not Action.DELETE_CANDIDATE
    assert result.action is Action.ABLEGEN
    assert result.safety_veto is True or result.category == "order"


def test_banking_otp_never_deleted(inbox_calm):
    message = _msg(
        id="otp",
        from_address="security@bank.example",
        subject="Verification code for your account",
        body_preview="One-time password. Ignore flash sale banners.",
    )
    result = evaluate_message(message, inbox_calm)
    assert result.action is Action.ABLEGEN
    assert "security" in result.safety_categories or result.category == "security"


def test_ticket_with_newsletter_header_stays(inbox_calm):
    message = _msg(
        id="ticket",
        subject="Your e-ticket and itinerary",
        headers={"list-unsubscribe": "<mailto:unsub@rail.example>"},
        body_preview="Boarding pass attached.",
    )
    result = evaluate_message(message, inbox_calm)
    assert result.action is Action.ABLEGEN
    assert result.category == "ticket"


def test_empty_unknown_mail_defaults_to_keep(inbox_calm):
    result = evaluate_message(_msg(id="empty", subject="", body_preview=""), inbox_calm)
    assert result.action is Action.KEEP
    assert result.safety_veto is False


def test_protected_fixture_file_has_zero_delete_candidates(inbox_calm, protected_messages):
    results = evaluate_messages(protected_messages, inbox_calm)
    deleted = [item.message_id for item in results if item.action is Action.DELETE_CANDIDATE]
    assert deleted == []
    assert all(item.action in {Action.ABLEGEN, Action.KEEP, Action.ARCHIVE} for item in results)
    ablegen = {item.message_id for item in results if item.action is Action.ABLEGEN}
    assert "keep-invoice" in ablegen
    assert "keep-order-with-sale-language" in ablegen
    assert "keep-government" in ablegen
    assert "keep-legal" in ablegen
    assert "keep-travel" in ablegen
    assert all(item.attention_cost == 1 for item in results)


@pytest.mark.parametrize("pack_fixture", ["inbox_calm", "receipts_first", "protected_only"])
def test_all_sample_packs_protect_the_must_keep_set(pack_fixture, protected_messages, request):
    pack = request.getfixturevalue(pack_fixture)
    results = evaluate_messages(protected_messages, pack)
    assert not any(item.action is Action.DELETE_CANDIDATE for item in results)


def test_policy_cannot_mark_invoice_as_delete_candidate():
    pack = PolicyPack(
        version=1,
        id="bad-pack",
        name="Bad",
        description="Must fail validation.",
        safety=SafetyConfig(require_human_review_for_delete=True),
        rules=[
            Rule.model_validate(
                {
                    "id": "oops-invoices",
                    "match": {"subject_contains": ["invoice"]},
                    "classify": "invoice",
                    "action": "delete_candidate",
                    "reason": "this must be rejected",
                }
            )
        ],
    )
    with pytest.raises(PolicyError, match="protected"):
        validate_policy(pack)


def test_policy_cannot_default_to_delete():
    with pytest.raises(PolicyError, match="default_action"):
        parse_policy(
            {
                "version": 1,
                "id": "mass-delete",
                "name": "No",
                "description": "Refuse mass-delete defaults.",
                "safety": {
                    "require_human_review_for_delete": True,
                    "default_action": "delete_candidate",
                },
                "rules": [
                    {
                        "id": "promo",
                        "match": {"subject_contains": ["sale"]},
                        "classify": "promo",
                        "action": "delete_candidate",
                        "reason": "noise",
                    }
                ],
            }
        )


def test_policy_cannot_disable_human_review():
    with pytest.raises(PolicyError, match="human_review"):
        parse_policy(
            {
                "version": 1,
                "id": "auto-delete",
                "name": "No",
                "description": "Refuse auto-delete.",
                "safety": {"require_human_review_for_delete": False},
                "rules": [
                    {
                        "id": "promo",
                        "match": {"subject_contains": ["sale"]},
                        "classify": "promo",
                        "action": "archive",
                        "reason": "noise",
                    }
                ],
            }
        )


def test_delete_rule_cannot_name_protected_keywords_in_matchers():
    with pytest.raises(PolicyError, match="protected"):
        parse_policy(
            {
                "version": 1,
                "id": "named-invoice",
                "name": "No",
                "description": "A delete rule that names an invoice in its matchers.",
                "safety": {"require_human_review_for_delete": True},
                "rules": [
                    {
                        "id": "too-broad-sale",
                        "match": {"subject_contains": ["sale", "invoice"]},
                        "classify": "promo",
                        "action": "delete_candidate",
                        "reason": "too broad on purpose",
                    }
                ],
            }
        )


def test_sloppy_promo_rule_is_vetoed_by_engine_rails():
    pack = parse_policy(
        {
            "version": 1,
            "id": "sloppy",
            "name": "Sloppy",
            "description": "A promo rule that collides with invoices only at evaluation.",
            "safety": {"require_human_review_for_delete": True},
            "rules": [
                {
                    "id": "too-broad-sale",
                    "match": {"subject_contains": ["sale"]},
                    "classify": "promo",
                    "action": "delete_candidate",
                    "reason": "too broad on purpose",
                }
            ],
        }
    )
    result = evaluate_message(_msg(subject="Invoice 3 for last sale"), pack)
    assert result.action is not Action.DELETE_CANDIDATE
    assert result.safety_veto is True
    assert result.action is Action.ABLEGEN
    assert result.attention_cost == 1


def test_engine_files_protected_mail_when_a_delete_rule_collides():
    pack = parse_policy(
        {
            "version": 1,
            "id": "empty-ish",
            "name": "Empty-ish",
            "description": "No file rules. A colliding delete must still file a tax notice.",
            "safety": {"require_human_review_for_delete": True},
            "rules": [
                {
                    "id": "only-sale",
                    "match": {"subject_contains": ["flash sale"]},
                    "classify": "promo",
                    "action": "delete_candidate",
                    "reason": "noise",
                }
            ],
        }
    )
    result = evaluate_message(_msg(subject="Steuerbescheid 2024 — flash sale"), pack)
    assert result.action is Action.ABLEGEN
    assert result.safety_veto is True
    assert "government" in result.safety_categories


def test_enforce_protected_action_blocks_delete_only():
    assert (
        enforce_protected_action(
            Action.DELETE_CANDIDATE, {"invoice"}, HARD_PROTECTED_CATEGORIES
        )
        is Action.ABLEGEN
    )
    assert (
        enforce_protected_action(Action.KEEP, {"invoice"}, HARD_PROTECTED_CATEGORIES)
        is Action.KEEP
    )
    assert (
        enforce_protected_action(Action.ARCHIVE, {"invoice"}, HARD_PROTECTED_CATEGORIES)
        is Action.ARCHIVE
    )


def test_enforce_protected_action_leaves_unprotected_delete():
    assert (
        enforce_protected_action(
            Action.DELETE_CANDIDATE, {"promo"}, HARD_PROTECTED_CATEGORIES
        )
        is Action.DELETE_CANDIDATE
    )
