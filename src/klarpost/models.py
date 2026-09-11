"""Public data models for policies, messages, and actions."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Action(StrEnum):
    """What to do with a message. Priority is Ablegen > archive > keep > delete-candidate."""

    ABLEGEN = "ablegen"
    ARCHIVE = "archive"
    KEEP = "keep"
    DELETE_CANDIDATE = "delete_candidate"


# Higher number wins when several rules match.
ACTION_PRIORITY: dict[Action, int] = {
    Action.ABLEGEN: 100,
    Action.ARCHIVE: 50,
    Action.KEEP: 20,
    Action.DELETE_CANDIDATE: 10,
}


class MatchSpec(BaseModel):
    """Matchers that fire on fixture metadata only (no live mailbox)."""

    model_config = ConfigDict(extra="forbid")

    subject_contains: list[str] = Field(default_factory=list)
    subject_regex: list[str] = Field(default_factory=list)
    from_contains: list[str] = Field(default_factory=list)
    from_domain_in: list[str] = Field(default_factory=list)
    body_contains: list[str] = Field(default_factory=list)
    has_list_unsubscribe: bool | None = None
    has_attachment: bool | None = None

    def is_empty(self) -> bool:
        return (
            not self.subject_contains
            and not self.subject_regex
            and not self.from_contains
            and not self.from_domain_in
            and not self.body_contains
            and self.has_list_unsubscribe is None
            and self.has_attachment is None
        )


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9][a-z0-9-]*$")
    enabled: bool = True
    priority: int = 0
    match: MatchSpec
    match_mode: Literal["any_field", "all_fields"] = "any_field"
    classify: str = Field(min_length=1, max_length=40, pattern=r"^[a-z][a-z0-9_]*$")
    action: Action
    reason: str = Field(min_length=1, max_length=400)

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("reason must not be blank")
        return cleaned


class SafetyConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    never_delete_categories: list[str] = Field(default_factory=list)
    require_human_review_for_delete: bool = True
    default_action: Action = Action.KEEP

    @field_validator("never_delete_categories")
    @classmethod
    def normalize_categories(cls, value: list[str]) -> list[str]:
        seen: list[str] = []
        for item in value:
            key = item.strip().lower()
            if key and key not in seen:
                seen.append(key)
        return seen


class PolicyPack(BaseModel):
    """A human-readable YAML pack. Version 1 is the only supported schema."""

    model_config = ConfigDict(extra="forbid")

    version: Literal[1] = 1
    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9][a-z0-9-]*$")
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    locale: str = "en"
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    rules: list[Rule] = Field(default_factory=list)

    @field_validator("rules")
    @classmethod
    def unique_rule_ids(cls, value: list[Rule]) -> list[Rule]:
        ids = [rule.id for rule in value]
        dupes = {item for item in ids if ids.count(item) > 1}
        if dupes:
            raise ValueError(f"duplicate rule ids: {sorted(dupes)}")
        return value


class Message(BaseModel):
    """Synthetic inbox fixture. Use example.com / reserved names only."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    id: str = Field(min_length=1, max_length=80)
    from_address: str = Field(alias="from")
    to: str | list[str] = "you@example.com"
    subject: str = ""
    date: str | None = None
    headers: dict[str, Any] = Field(default_factory=dict)
    body_preview: str = ""
    has_attachment: bool = False

    def header(self, name: str) -> str | None:
        wanted = name.lower()
        for key, value in self.headers.items():
            if key.lower() == wanted:
                if value is None:
                    return None
                return str(value)
        return None

    def from_domain(self) -> str:
        address = self.from_address.strip().lower()
        if address.startswith("<") and address.endswith(">"):
            address = address[1:-1]
        if "<" in address and ">" in address:
            address = address[address.index("<") + 1 : address.index(">")]
        if "@" not in address:
            return ""
        return address.split("@", 1)[1]
