"""Load and validate YAML policy packs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from klarpost.models import Action, PolicyPack
from klarpost.safety import HARD_PROTECTED_CATEGORIES, merge_protected_categories


class PolicyError(ValueError):
    """Invalid pack: schema error or a safety-rail violation."""


def load_yaml(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"cannot read policy file {path}: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise PolicyError(f"invalid YAML in {path}: {exc}") from exc
    if data is None:
        raise PolicyError(f"empty policy file: {path}")
    return data


def parse_policy(data: Any, *, source: str = "<memory>") -> PolicyPack:
    if not isinstance(data, dict):
        raise PolicyError(f"{source}: policy root must be a mapping")
    try:
        pack = PolicyPack.model_validate(data)
    except ValidationError as exc:
        raise PolicyError(_format_validation(source, exc)) from exc
    validate_policy(pack, source=source)
    return pack


def load_policy(path: str | Path) -> PolicyPack:
    policy_path = Path(path)
    return parse_policy(load_yaml(policy_path), source=str(policy_path))


def validate_policy(pack: PolicyPack, *, source: str = "<memory>") -> None:
    """Schema is already valid here; enforce hard rails the YAML author cannot waive."""
    if pack.safety.default_action is Action.DELETE_CANDIDATE:
        raise PolicyError(
            f"{source}: safety.default_action cannot be delete_candidate "
            "(klarpost refuses silent mass-delete defaults)"
        )
    if not pack.safety.require_human_review_for_delete:
        raise PolicyError(
            f"{source}: require_human_review_for_delete must stay true "
            "(this engine never auto-deletes)"
        )

    protected = merge_protected_categories(pack.safety.never_delete_categories)
    missing_hard = sorted(HARD_PROTECTED_CATEGORIES - protected)
    if missing_hard:
        # merge_protected_categories always unions the hard set; this is a belt.
        raise PolicyError(f"{source}: missing hard protected categories: {missing_hard}")

    for rule in pack.rules:
        if rule.match.is_empty():
            raise PolicyError(f"{source}: rule {rule.id!r} has an empty match block")
        if rule.action is Action.DELETE_CANDIDATE and rule.classify in protected:
            raise PolicyError(
                f"{source}: rule {rule.id!r} classifies {rule.classify!r} as "
                "delete_candidate — protected categories may only file, archive, or keep"
            )


def _format_validation(source: str, exc: ValidationError) -> str:
    parts = [f"{source}: policy schema error"]
    for err in exc.errors():
        loc = ".".join(str(item) for item in err.get("loc", ()))
        parts.append(f"  - {loc}: {err.get('msg')}")
    return "\n".join(parts)
