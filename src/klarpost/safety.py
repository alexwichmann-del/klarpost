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
    (
        r"\b(hotel (booking|reservation|confirmation)|check[- ]in is open|"
        r"visa (appointment|application)|reisebest[aä]tigung)\b",
        "travel",
    ),
    (
        r"\b(court (summons|order)|legal notice|subpoena|cease and desist|"
        r"power of attorney|vollmacht|gerichtliche ladung)\b",
        "legal",
    ),
)

# "receipt" keywords live in the invoice pattern; both categories are protected.
ALIASED_PROTECTED_CATEGORIES: dict[str, str] = {"receipt": "invoice"}

_COMPILED: tuple[tuple[re.Pattern[str], str], ...] = tuple(
    (re.compile(pattern, re.IGNORECASE), category) for pattern, category in _SIGNAL_PATTERNS
)

SCANNED_PROTECTED_CATEGORIES: frozenset[str] = frozenset(
    category for _, category in _SIGNAL_PATTERNS
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
    """After a veto, file any hard-protected mail. Uncertainty stays `keep`."""
    if categories & set(HARD_PROTECTED_CATEGORIES):
        return Action.ABLEGEN
    return Action.KEEP


def enforce_protected_action(
    proposed: Action,
    categories: set[str],
    protected: frozenset[str],
) -> Action:
    """Never return delete_candidate when a protected category matched.

    Archive and keep are left alone: a newsletter that *mentions* an invoice
    is not an invoice. The rail exists to stop irreversible suggestions.
    """
    if proposed is Action.DELETE_CANDIDATE and categories & set(protected):
        return downgrade_after_veto(categories)
    return proposed


def matcher_names_protected(blob: str) -> tuple[str, str] | None:
    """If matcher text names a hard-protected signal, return (category, evidence)."""
    if not blob.strip():
        return None
    for pattern, category in _COMPILED:
        match = pattern.search(blob)
        if match:
            return category, match.group(0)
    return None
