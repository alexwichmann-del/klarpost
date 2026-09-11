"""Load synthetic inbox fixtures. No live mail, no personal data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from klarpost.models import Message


class FixtureError(ValueError):
    pass


def load_fixtures(path: str | Path) -> list[Message]:
    fixture_path = Path(path)
    try:
        raw = fixture_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FixtureError(f"cannot read fixtures {fixture_path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FixtureError(f"invalid JSON in {fixture_path}: {exc}") from exc
    return parse_fixtures(data, source=str(fixture_path))


def parse_fixtures(data: Any, *, source: str = "<memory>") -> list[Message]:
    if isinstance(data, dict) and "messages" in data:
        items = data["messages"]
    else:
        items = data
    if not isinstance(items, list):
        raise FixtureError(f"{source}: fixtures must be a list or {{'messages': [...]}}")
    messages: list[Message] = []
    for index, item in enumerate(items):
        try:
            messages.append(Message.model_validate(item))
        except ValidationError as exc:
            raise FixtureError(f"{source}: message[{index}] invalid: {exc}") from exc
    return messages
