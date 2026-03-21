from __future__ import annotations

from typing import Any


def plan_intent_template(_args: dict[str, Any]) -> dict[str, Any]:
    return {
        "template_version": "v1",
        "front_matter_required": [
            "id",
            "type",
            "title",
            "status",
            "plan_ref",
            "task_refs",
            "links",
        ],
        "body_sections_required": ["Intent", "Scope"],
        "decomposition_guide": [
            "Split by independent objective with separate validation outcomes.",
            "Keep each intent boundary narrow enough to produce executable tasks.",
            "Avoid mixing unrelated architecture domains in one intent.",
        ],
        "mapping_rules": {
            "type": "intent",
            "status": "active",
            "task_refs_default": [],
            "links_defaults": [
                "PROJ-INTENT-INDEX",
                "PLAN-MAIN",
                "ARCH-INDEX",
            ],
        },
        "example_intent_payload": {
            "title": "Intent title",
            "intent": "Why this change is needed and expected outcome.",
            "scope_in": ["in-scope item"],
            "scope_out": ["out-of-scope item"],
            "links": ["PLAN-MAIN", "ARCH-INDEX"],
            "kind": "general",
            "design_impact": "unspecified",
        },
    }
