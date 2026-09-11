"""Hard safety rails. Policy packs cannot turn these off."""

from __future__ import annotations

import re
from dataclasses import dataclass

from klarpost.models import Action, Message

# Categories that must never become delete-candidates, even if a pack is sloppy.
HARD_PROTECTED_CATEGORIES: frozenset[str] = frozenset(
    {
        "order",
        "invoice",
        "receipt",
        "ticket",
        "travel",
        "banking",
        "security",
        "government",
        "medical",
        "legal",
        "identity",
    }
)

# Conservative keyword signals. These are fixtures-only heuristics, not a spam model.
# Keep phrases generic and language-aware (EN + DE) without personal data.
_SIGNAL_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        r"\b(invoice|tax invoice|receipt|rechnung|beleg|quittung|zahlungsbeleg)\b",
        "invoice",
    ),
    (
        r"\b(order confirmation|your order\s*#|bestellbest[aä]tigung|bestellung\s*#|"
        r"shipping confirmation|versandbest[aä]tigung|tracking number)\b",
        "order",
    ),
    (
        r"\b(boarding pass|boardingpass|e-?ticket|eticket|itinerary|reservation|"
        r"buchungsbest[aä]tigung|fahrkarte|zugticket)\b",
        "ticket",
    ),
    (
        r"\b(one[-\s]?time (code|password)|verification code|security (alert|code)|"
        r"2fa|mfa|password reset|passwort zur[uü]cksetzen|anmeldeversuch|"
        r"new sign[- ]in|suspicious (login|activity))\b",
        "security",
    ),
    (
        r"\b(iban|sepa|account statement|kontoauszug|wire transfer|[uü]berweisung|"
        r"overdraft|payment received|zahlungseingang|direct debit|lastschrift)\b",
        "banking",
    ),
    (
        r"\b(tax (notice|assessment)|steuerbescheid|amtliche mitteilung|"
        r"residence permit|social security)\b",
        "government",
    ),
    (
        r"\b(lab result|befund|prescription|rezept|appointment confirmation|"
        r"terminbest[aä]tigung)\b",
        "medical",
    ),
    (
        r"\b(passport|reisepass|national id|personalausweis|driver'?s license|"
        r"f[uü]hrerschein)\b",
        "identity",
    ),
)

_COMPILED: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern, re.IGNORECASE), category) for pattern, category in _SIGNAL_PATTERNS
)


@dataclass(frozen=True)
class SafetyHit:
    category: str
    evidence: str


def merge_protected_categories(pack_categories: list[str]) -> frozenset[str]:
    """Packs may add categories. They may not remove the hard set."""
    extra = {item.strip().lower() for item in pack_categories if item.strip()}
    return HARD_PROTECTED_CATEGORIES | extra


def scan_message(message: Message) -> list[SafetyHit]:
    """Detect protected paper-trail / security mail from fixture text."""
    blob = " ".join(
        part
        for part in (
            message.subject,
            message.from_address,
            message.body_preview,
        )
        if part
    )
    hits: list[SafetyHit] = []
    seen: set[str] = set()
    for pattern, category in _COMPILED:
        match = pattern.search(blob)
        if match and category not in seen:
            seen.add(category)
            hits.append(SafetyHit(category=category, evidence=match.group(0)))
    return hits


def veto_delete(
    proposed: Action,
    categories: set[str],
    protected: frozenset[str],
) -> bool:
    """True when a delete-candidate would violate a hard rail."""
    if proposed is not Action.DELETE_CANDIDATE:
        return False
    return bool(categories & set(protected))


def downgrade_after_veto(categories: set[str]) -> Action:
    """After a veto, prefer Ablegen for paper-trail mail, else keep."""
    paper = {"order", "invoice", "receipt", "ticket", "travel", "legal", "identity"}
    if categories & paper:
        return Action.ABLEGEN
    return Action.KEEP
