"""JSON Schema export for policy packs (editor / CI use)."""

from __future__ import annotations

from klarpost.models import PolicyPack


def policy_json_schema() -> dict:
    schema = PolicyPack.model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["title"] = "klarpost policy pack"
    schema["description"] = (
        "Human-readable inbox policy. Hard safety rails in the engine still "
        "block delete-candidates on orders, invoices, receipts, tickets, "
        "travel, banking, security, government, medical, legal, and identity "
        "mail even if a pack is incomplete."
    )
    return schema
