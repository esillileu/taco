from __future__ import annotations

import re
from typing import Any

from taco.core.plan import (
    RepoState,
    _collect_string_list,
    _intent_design_impact,
    _intent_kind,
)


def _required_refactor_design_sync(
    state: RepoState, task_id: str, task_meta: dict[str, Any]
) -> list[dict[str, str]]:
    intent_ids: set[str] = set()
    for value in _collect_string_list(task_meta.get("links")):
        path = state.index.node_index.get(value, "")
        if not path:
            continue
        doc = next((item for item in state.index.documents if item.path == path), None)
        if doc is not None and doc.doc_type == "intent":
            intent_ids.add(value)

    for doc in state.index.documents:
        if doc.doc_type != "intent" or not isinstance(doc.metadata, dict):
            continue
        refs = _collect_string_list(doc.metadata.get("task_refs"))
        if task_id in refs and doc.node_id:
            intent_ids.add(doc.node_id)

    required: list[dict[str, str]] = []
    for intent_id in sorted(intent_ids):
        path = state.index.node_index.get(intent_id, "")
        doc = next((item for item in state.index.documents if item.path == path), None)
        if doc is None or doc.doc_type != "intent":
            continue
        meta = doc.metadata if isinstance(doc.metadata, dict) else {}
        kind = _intent_kind(meta)
        impact = _intent_design_impact(meta)
        if kind == "refactor" and impact in {"minor", "major"}:
            required.append({"intent_id": intent_id, "design_impact": impact})
    return required

def _has_design_sync_evidence(implementation: str, verification: str) -> bool:
    combined = f"{implementation}\n{verification}"
    lowered = combined.lower()
    if "design-sync:" not in lowered:
        return False
    has_path = bool(
        re.search(r"\.context/project/architecture/[\w./-]+\.md", combined)
    )
    has_anchor = "ARCH-INDEX" in combined or bool(
        re.search(r"FLOW-[A-Z0-9-]+", combined)
    )
    return has_path or has_anchor

