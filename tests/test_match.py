from klarpost.match import message_matches
from klarpost.models import MatchSpec, Message


def _msg(**kwargs) -> Message:
    payload = {"id": "m", "from": "Store <billing@invoices.shop.example>", "subject": "Hi"}
    payload.update(kwargs)
    return Message.model_validate(payload)


def test_domain_suffix_match():
    spec = MatchSpec(from_domain_in=["shop.example"])
    assert message_matches(_msg(), spec, mode="any_field")


def test_from_display_name_contains():
    spec = MatchSpec(from_contains=["billing@"])
    assert message_matches(_msg(), spec, mode="any_field")


def test_all_fields_requires_every_populated_matcher():
    spec = MatchSpec(subject_contains=["invoice"], has_attachment=True)
    message = _msg(subject="Invoice 1", has_attachment=False)
    assert not message_matches(message, spec, mode="all_fields")
    message = _msg(subject="Invoice 1", has_attachment=True)
    assert message_matches(message, spec, mode="all_fields")


def test_list_unsubscribe_present():
    spec = MatchSpec(has_list_unsubscribe=True)
    bare = _msg()
    listed = _msg(headers={"List-Unsubscribe": "<mailto:x@example.com>"})
    assert not message_matches(bare, spec, mode="any_field")
    assert message_matches(listed, spec, mode="any_field")
