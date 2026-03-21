from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError

from .intent_creation import create_many_intents
from .intent_state import rebuild_state_index


def ingest_natural_language_intent(
    state: RepoState, *, intent_text: str, title: str | None
) -> dict[str, Any]:
    payload = {
        "intents": [
            {
                "title": title or "Captured Intent",
                "intent": intent_text,
                "scope_in": ["planning context"],
                "scope_out": ["implementation detail"],
            }
        ]
    }
    created = create_many_intents(state, payload)
    rows = created.get("created", [])
    if not isinstance(rows, list) or not rows:
        raise ToolError(
            "intent_create_failed",
            "failed to create intent from natural language input",
            {},
        )
    first = rows[0]
    return {
        "intent_id": str(first.get("intent_id", "")),
        "path": str(first.get("path", "")),
        "title": str(first.get("title", "")),
    }


__all__ = [
    "ingest_natural_language_intent",
    "rebuild_state_index",
    "create_many_intents",
]
