"""Pure matchers against fixture metadata."""

from __future__ import annotations

import re

from klarpost.models import MatchSpec, Message


def message_matches(message: Message, spec: MatchSpec, *, mode: str) -> bool:
    checks: list[bool] = []

    if spec.subject_contains:
        subject = message.subject.lower()
        checks.append(any(needle.lower() in subject for needle in spec.subject_contains))
    if spec.subject_regex:
        checks.append(
            any(_safe_search(pattern, message.subject) for pattern in spec.subject_regex)
        )
    if spec.from_contains:
        sender = message.from_address.lower()
        checks.append(any(needle.lower() in sender for needle in spec.from_contains))
    if spec.from_domain_in:
        domain = message.from_domain()
        checks.append(any(_domain_suffix(domain, item) for item in spec.from_domain_in))
    if spec.body_contains:
        body = message.body_preview.lower()
        checks.append(any(needle.lower() in body for needle in spec.body_contains))
    if spec.has_list_unsubscribe is not None:
        present = _has_list_unsubscribe(message)
        checks.append(present is spec.has_list_unsubscribe)
    if spec.has_attachment is not None:
        checks.append(message.has_attachment is spec.has_attachment)

    if not checks:
        return False
    if mode == "all_fields":
        return all(checks)
    return any(checks)


def _safe_search(pattern: str, text: str) -> bool:
    try:
        return re.search(pattern, text, flags=re.IGNORECASE) is not None
    except re.error:
        return False


def _domain_suffix(domain: str, candidate: str) -> bool:
    left = domain.lower().rstrip(".")
    right = candidate.lower().rstrip(".")
    return left == right or left.endswith("." + right)


def _has_list_unsubscribe(message: Message) -> bool:
    value = message.header("list-unsubscribe")
    if value is None:
        return False
    return bool(str(value).strip())
