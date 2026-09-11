"""Evaluate fixture messages against a policy pack with hard safety rails."""

from __future__ import annotations

from dataclasses import dataclass, field

from klarpost.match import message_matches
from klarpost.models import ACTION_PRIORITY, Action, Message, PolicyPack
from klarpost.safety import (
    SafetyHit,
    downgrade_after_veto,
    merge_protected_categories,
    scan_message,
    veto_delete,
)


@dataclass
class RuleHit:
    rule_id: str
    classify: str
    action: Action
    priority: int
    reason: str


@dataclass
class Evaluation:
    message_id: str
    action: Action
    category: str
    matched_rules: list[str]
    safety_categories: list[str]
    safety_veto: bool
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "message_id": self.message_id,
            "action": self.action.value,
            "category": self.category,
            "matched_rules": list(self.matched_rules),
            "safety_categories": list(self.safety_categories),
            "safety_veto": self.safety_veto,
            "reasons": list(self.reasons),
        }


def evaluate_message(message: Message, pack: PolicyPack) -> Evaluation:
    protected = merge_protected_categories(pack.safety.never_delete_categories)
    safety_hits = scan_message(message)
    rule_hits = [
        RuleHit(
            rule_id=rule.id,
            classify=rule.classify,
            action=rule.action,
            priority=rule.priority,
            reason=rule.reason,
        )
        for rule in pack.rules
        if rule.enabled and message_matches(message, rule.match, mode=rule.match_mode)
    ]

    categories = {hit.classify for hit in rule_hits} | {hit.category for hit in safety_hits}
    proposed = _choose_action(rule_hits, pack.safety.default_action)
    blocked = veto_delete(proposed, categories, protected)
    delete_matched = any(hit.action is Action.DELETE_CANDIDATE for hit in rule_hits)
    protected_hit = bool(categories & set(protected))
    overridden = delete_matched and protected_hit
    final = downgrade_after_veto(categories) if blocked else proposed

    reasons = _reasons(rule_hits, safety_hits, blocked, overridden, final)
    category = _primary_category(final, rule_hits, safety_hits, categories)

    return Evaluation(
        message_id=message.id,
        action=final,
        category=category,
        matched_rules=[hit.rule_id for hit in _sorted_hits(rule_hits)],
        safety_categories=sorted({hit.category for hit in safety_hits}),
        safety_veto=blocked or overridden,
        reasons=reasons,
    )


def evaluate_messages(messages: list[Message], pack: PolicyPack) -> list[Evaluation]:
    return [evaluate_message(message, pack) for message in messages]


def _choose_action(hits: list[RuleHit], default: Action) -> Action:
    if not hits:
        return default
    return max(
        hits,
        key=lambda hit: (ACTION_PRIORITY[hit.action], hit.priority, hit.rule_id),
    ).action


def _sorted_hits(hits: list[RuleHit]) -> list[RuleHit]:
    return sorted(
        hits,
        key=lambda hit: (ACTION_PRIORITY[hit.action], hit.priority, hit.rule_id),
        reverse=True,
    )


def _primary_category(
    action: Action,
    rule_hits: list[RuleHit],
    safety_hits: list[SafetyHit],
    categories: set[str],
) -> str:
    if action is Action.ABLEGEN:
        paper = [
            "invoice",
            "receipt",
            "order",
            "ticket",
            "travel",
            "banking",
            "security",
            "legal",
            "identity",
            "government",
            "medical",
        ]
        for name in paper:
            if name in categories:
                return name
    if rule_hits:
        winner = max(rule_hits, key=lambda hit: (ACTION_PRIORITY[hit.action], hit.priority))
        return winner.classify
    if safety_hits:
        return safety_hits[0].category
    return "unclassified"


def _reasons(
    rule_hits: list[RuleHit],
    safety_hits: list[SafetyHit],
    blocked: bool,
    overridden: bool,
    final: Action,
) -> list[str]:
    reasons: list[str] = []
    for hit in _sorted_hits(rule_hits):
        reasons.append(f"rule {hit.rule_id}: {hit.reason}")
    for hit in safety_hits:
        reasons.append(f"safety rail matched {hit.category} ({hit.evidence!r})")
    if blocked:
        reasons.append(
            "HARD SAFETY VETO: delete_candidate blocked because a protected category matched"
        )
    elif overridden:
        reasons.append(
            "HARD SAFETY VETO: a delete_candidate rule matched protected mail; Ablegen/keep wins"
        )
    if not rule_hits and not safety_hits:
        reasons.append("no rule matched; default keep (do not guess-delete)")
    reasons.append(f"final action: {final.value}")
    return reasons
