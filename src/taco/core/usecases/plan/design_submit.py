from __future__ import annotations

from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _find_heading_by_section_id,
    _fingerprint,
    _placeholder_markers_in_text,
    _replace_heading_block,
    _slice_text,
)
from taco.core.usecases.io import read_text, write_text

from .stage_state import set_plan_stage


def _allowed_design_path(state: RepoState, path: str) -> bool:
    docs = state.config_raw.get("docs", {})
    if not isinstance(docs, dict):
        return False
    allowed: set[str] = set()
    for key in ("architecture", "plan", "intent"):
        value = docs.get(key)
        if isinstance(value, str) and value.strip():
            allowed.add(value.strip())
    intents_glob = docs.get("intents_glob")
    if isinstance(intents_glob, str) and "/" in intents_glob:
        allowed.add(intents_glob.rsplit("/", 1)[0].strip() + "/")
    architecture_path = docs.get("architecture")
    if isinstance(architecture_path, str) and "/" in architecture_path:
        allowed.add(architecture_path.rsplit("/", 1)[0].strip() + "/")

    if path in allowed:
        return True
    return any(path.startswith(prefix) for prefix in allowed if prefix.endswith("/"))


def plan_design_submit_changes(
    state: RepoState, args: dict[str, Any]
) -> dict[str, Any]:
    changes = args.get("changes")
    if not isinstance(changes, list) or not changes:
        raise ToolError(
            "invalid_input",
            "changes must be a non-empty array",
            {"key": "changes"},
        )
    applied: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for idx, raw in enumerate(changes):
        if not isinstance(raw, dict):
            rejected.append(
                {
                    "index": idx,
                    "code": "invalid_change_item",
                    "message": "must be object",
                }
            )
            continue
        path = str(raw.get("path", "")).strip()
        section_id = str(raw.get("section_id", "")).strip()
        content = raw.get("content")
        base_fingerprint = str(raw.get("base_fingerprint", "")).strip()
        if (
            not path
            or not section_id
            or not isinstance(content, str)
            or not content.strip()
        ):
            rejected.append(
                {
                    "index": idx,
                    "code": "missing_required_fields",
                    "message": "path, section_id, content are required",
                }
            )
            continue
        if not _allowed_design_path(state, path):
            rejected.append(
                {
                    "index": idx,
                    "code": "path_not_allowed",
                    "message": "path is outside plan-mode design scope",
                    "path": path,
                }
            )
            continue
        doc = next((item for item in state.index.documents if item.path == path), None)
        if doc is None:
            rejected.append(
                {
                    "index": idx,
                    "code": "doc_not_found",
                    "message": "document was not found",
                    "path": path,
                }
            )
            continue
        heading = _find_heading_by_section_id(doc, section_id)
        if heading is None:
            rejected.append(
                {
                    "index": idx,
                    "code": "section_not_found",
                    "message": "section was not found",
                    "path": path,
                    "section_id": section_id,
                }
            )
            continue
        original = read_text(state, path)
        before = _slice_text(original, heading.start_line, heading.end_line)
        actual = _fingerprint([path, section_id, before])
        if base_fingerprint and base_fingerprint != actual:
            rejected.append(
                {
                    "index": idx,
                    "code": "fingerprint_mismatch",
                    "message": "base fingerprint mismatch",
                    "expected": base_fingerprint,
                    "actual": actual,
                }
            )
            continue
        updated = _replace_heading_block(original, heading.heading, content)
        original_markers = set(_placeholder_markers_in_text(original))
        updated_markers = set(_placeholder_markers_in_text(updated))
        if sorted(updated_markers - original_markers):
            rejected.append(
                {
                    "index": idx,
                    "code": "placeholder_detected",
                    "message": "placeholder markers are not allowed",
                }
            )
            continue
        write_text(state, path, updated)
        after = _slice_text(updated, heading.start_line, heading.end_line)
        applied.append(
            {
                "index": idx,
                "path": path,
                "section_id": section_id,
                "fingerprint": _fingerprint([path, section_id, after]),
            }
        )
    if rejected:
        raise ToolError(
            "design_submit_failed",
            "one or more design changes failed validation",
            {"applied": applied, "rejected": rejected},
        )
    set_plan_stage(state, "task_authoring")
    return {
        "applied": applied,
        "rejected": [],
        "stage_transition": "task_authoring",
        "next_action": {"tool": "plan.mode.guide", "args": {"stage": "task_authoring"}},
    }
