from klarpost.evaluate import evaluate_message, evaluate_messages
from klarpost.models import Action, Message


def test_mixed_inbox_priority_ablegen_over_archive_over_delete(inbox_calm, mixed_messages):
    by_id = {item.message_id: item for item in evaluate_messages(mixed_messages, inbox_calm)}

    assert by_id["fx-invoice-01"].action is Action.ABLEGEN
    assert by_id["fx-rechnung-de"].action is Action.ABLEGEN
    assert by_id["fx-ticket-01"].action is Action.ABLEGEN
    assert by_id["fx-bank-01"].action is Action.ABLEGEN
    assert by_id["fx-security-01"].action is Action.ABLEGEN
    assert by_id["fx-order-promo-collision"].action is Action.ABLEGEN
    assert by_id["fx-order-promo-collision"].safety_veto is True

    assert by_id["fx-newsletter-01"].action is Action.ARCHIVE
    assert by_id["fx-unknown-01"].action is Action.KEEP
    assert by_id["fx-empty-subject"].action is Action.KEEP
    assert by_id["fx-promo-01"].action is Action.DELETE_CANDIDATE


def test_receipts_first_never_emits_delete_candidates(
    receipts_first, mixed_messages, promo_messages
):
    results = evaluate_messages(mixed_messages + promo_messages, receipts_first)
    assert all(item.action is not Action.DELETE_CANDIDATE for item in results)


def test_list_unsubscribe_archives_even_with_sale_language(inbox_calm):
    message = Message.model_validate(
        {
            "id": "sale-list",
            "from": "hello@boutique.example",
            "subject": "Flash sale — 30% off",
            "headers": {"list-unsubscribe": "<mailto:unsub@boutique.example>"},
            "body_preview": "Last chance marketing, but you can leave the list.",
        }
    )
    result = evaluate_message(message, inbox_calm)
    assert result.action is Action.ARCHIVE
    assert result.safety_veto is False


def test_promo_noise_can_be_delete_candidate_on_calm_pack(inbox_calm, promo_messages):
    results = {item.message_id: item for item in evaluate_messages(promo_messages, inbox_calm)}
    assert results["promo-flash"].action is Action.DELETE_CANDIDATE
    assert results["promo-rabatt"].action is Action.DELETE_CANDIDATE
    assert results["promo-digest"].action is Action.ARCHIVE
    assert all(not item.safety_veto for item in results.values())


def test_protected_only_keeps_unknowns(protected_only):
    message = Message.model_validate(
        {
            "id": "note",
            "from": "friend@example.com",
            "subject": "notes from lunch",
            "body_preview": "no commerce here",
        }
    )
    result = evaluate_message(message, protected_only)
    assert result.action is Action.KEEP
    assert result.category == "unclassified"


def test_explain_reasons_include_safety_when_vetoed(inbox_calm):
    message = Message.model_validate(
        {
            "id": "mix",
            "from": "deals@shop.example",
            "subject": "Your order #1 — last chance 40% off",
            "body_preview": "Shipping confirmation",
            "headers": {"list-unsubscribe": "<mailto:x@shop.example>"},
        }
    )
    result = evaluate_message(message, inbox_calm)
    assert any("HARD SAFETY VETO" in line for line in result.reasons)
    assert result.as_dict()["action"] == "ablegen"
