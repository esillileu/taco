from __future__ import annotations

import re
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _placeholder_markers_in_text,
    _split_front_matter,
)


def task_pack_readiness_missing(state: RepoState, task_id: str) -> list[str]:
    task_path = state.index.task_index.get(task_id)
    if not task_path:
        return ["task_not_found"]

    task_doc = next(
        (doc for doc in state.index.documents if doc.path == task_path), None
    )
    if task_doc is None:
        return ["task_doc_missing"]

    text = state.index.document_texts.get(task_path, "")
    meta, _ = _split_front_matter(text)

    missing: list[str] = []
    if not meta:
        missing.append("front_matter")
    else:
        scope = meta.get("scope")
        if not isinstance(scope, dict):
            missing.append("scope")
        else:
            for key in ("in", "out"):
                if not isinstance(scope.get(key), list):
                    missing.append(f"scope.{key}")

        references = meta.get("references")
        if not isinstance(references, dict):
            missing.append("references")
        else:
            for key in ("modules", "flows", "schemas"):
                value = references.get(key)
                if not isinstance(value, list):
                    missing.append(f"references.{key}")
                    continue
                values = [item.strip() for item in value if isinstance(item, str)]
                if not values:
                    missing.append(f"references.{key}")

    required = state.task_required_headings
    seen_headings = {heading.heading for heading in task_doc.headings}
    for heading in required:
        if heading not in seen_headings:
            missing.append(f"heading:{heading}")

    if "heading:Implementation Approach" not in missing and not _has_actionable_section(
        task_doc, text, "Implementation Approach"
    ):
        missing.append("implementation.approach")
    if "heading:Verification Approach" not in missing and not _has_actionable_section(
        task_doc, text, "Verification Approach"
    ):
        missing.append("verification.criteria")

    return missing


def ensure_task_readiness_for_pack(state: RepoState, task_id: str) -> None:
    task_path = state.index.task_index.get(task_id)
    if task_path:
        text = state.index.document_texts.get(task_path, "")
        markers = _placeholder_markers_in_text(text)
        if markers:
            raise ToolError(
                "placeholder_detected",
                "task contains placeholder markers",
                {"task_id": task_id, "markers": markers},
            )

    missing = task_pack_readiness_missing(state, task_id)
    if "task_not_found" in missing:
        raise ToolError(
            "task_not_found", "task id not found in index", {"task_id": task_id}
        )
    if "task_doc_missing" in missing:
        raise ToolError(
            "task_doc_missing",
            "task document missing from indexed docs",
            {"task_id": task_id, "path": task_path or ""},
        )
    if missing:
        deduped = list(dict.fromkeys(missing))
        raise ToolError(
            "task_not_ready",
            "task is not ready for pack execution",
            {"task_id": task_id, "missing_requirements": ",".join(deduped)},
        )


def _has_actionable_section(doc: Any, text: str, heading_name: str) -> bool:
    heading = next(
        (item for item in doc.headings if item.heading == heading_name), None
    )
    if heading is None:
        return False

    lines = text.splitlines()
    start = max(heading.start_line, 0)
    end = min(heading.end_line, len(lines))
    body = lines[start:end]
    for raw in body:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue
        if stripped.lower() in {"pending", "pending definition.", "tbd"}:
            continue
        if stripped.startswith("- "):
            return True
        if re.match(r"^\d+\.\s+\S", stripped):
            return True
        if "`" in stripped:
            return True
    return False
