from __future__ import annotations

from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _append_under_heading,
    _doc_patch_constraints,
    _enforce_doc_patch_scope,
    _find_heading_by_section_id,
    _fingerprint,
    _placeholder_markers_in_text,
    _replace_heading_block,
    _required_str,
    _set_front_matter_key,
    _slice_text,
)
from taco.core.usecases.io import read_text, write_text


def _doc_snippet(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    path = _required_str(args, "path")
    anchor_id = _required_str(args, "anchor_id")
    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None:
        raise ToolError("doc_not_found", "document was not found", {"path": path})

    heading = next((item for item in doc.headings if item.anchor_id == anchor_id), None)
    if heading is None:
        raise ToolError(
            "anchor_not_found",
            "anchor was not found in document",
            {"path": path, "anchor_id": anchor_id},
        )

    text = state.index.document_texts[path]
    snippet = _slice_text(text, heading.start_line, heading.end_line)
    return {
        "path": path,
        "anchor_id": anchor_id,
        "heading": heading.heading,
        "snippet": snippet,
    }

def _doc_section_get(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    path = _required_str(args, "path")
    section_id = _required_str(args, "section_id")
    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None:
        raise ToolError("doc_not_found", "document was not found", {"path": path})
    heading = _find_heading_by_section_id(doc, section_id)
    if heading is None:
        raise ToolError(
            "section_not_found",
            "section was not found in document",
            {"path": path, "section_id": section_id},
        )
    text = state.index.document_texts.get(path, "")
    snippet = _slice_text(text, heading.start_line, heading.end_line)
    return {
        "path": path,
        "section_id": section_id,
        "heading": heading.heading,
        "content": snippet,
        "fingerprint": _fingerprint([path, section_id, snippet]),
        "constraints": _doc_patch_constraints(path),
    }

def _doc_section_patch(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    path = _required_str(args, "path")
    section_id = _required_str(args, "section_id")
    base_fingerprint = _required_str(args, "base_fingerprint")
    ops = args.get("ops")
    mode = str(args.get("mode", "plan")).strip().lower() or "plan"
    dry_run = args.get("dry_run", True)
    if mode not in {"plan", "build"}:
        raise ToolError("invalid_input", "mode must be plan or build", {"key": "mode"})
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})
    if not isinstance(ops, list) or not ops:
        raise ToolError("invalid_input", "ops must be non-empty list", {"key": "ops"})

    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None:
        raise ToolError("doc_not_found", "document was not found", {"path": path})

    heading = _find_heading_by_section_id(doc, section_id)
    if heading is None:
        raise ToolError(
            "section_not_found",
            "section was not found in document",
            {"path": path, "section_id": section_id},
        )

    _enforce_doc_patch_scope(mode, path, heading.heading)

    original = read_text(state, path)
    current_section = _slice_text(original, heading.start_line, heading.end_line)
    actual_fingerprint = _fingerprint([path, section_id, current_section])
    if actual_fingerprint != base_fingerprint:
        raise ToolError(
            "fingerprint_mismatch",
            "section fingerprint mismatch",
            {
                "path": path,
                "section_id": section_id,
                "expected": base_fingerprint,
                "actual": actual_fingerprint,
            },
        )

    updated = original
    for op in ops:
        if not isinstance(op, dict):
            raise ToolError("invalid_patch_op", "patch op must be object", {"op": op})
        kind = str(op.get("op", "")).strip()
        if kind == "append_list_item":
            text = str(op.get("text", "")).strip()
            if not text:
                raise ToolError(
                    "invalid_patch_op",
                    "append_list_item requires non-empty text",
                    {"op": kind},
                )
            updated = _append_under_heading(updated, heading.heading, f"- {text}")
        elif kind == "replace_block":
            content = op.get("content")
            if not isinstance(content, str):
                raise ToolError(
                    "invalid_patch_op",
                    "replace_block requires string content",
                    {"op": kind},
                )
            updated = _replace_heading_block(updated, heading.heading, content)
        elif kind == "set_front_matter_key":
            key = str(op.get("key", "")).strip()
            if not key:
                raise ToolError(
                    "invalid_patch_op",
                    "set_front_matter_key requires key",
                    {"op": kind},
                )
            updated = _set_front_matter_key(updated, key, op.get("value"))
        else:
            raise ToolError(
                "invalid_patch_op",
                "unsupported patch op",
                {"op": kind},
            )

    original_markers = set(_placeholder_markers_in_text(original))
    updated_markers = set(_placeholder_markers_in_text(updated))
    if sorted(updated_markers - original_markers):
        raise ToolError(
            "placeholder_detected",
            "placeholder markers are not allowed",
            {"path": path, "markers": sorted(updated_markers - original_markers)},
        )

    if not dry_run:
        write_text(state, path, updated)

    refreshed = _slice_text(updated, heading.start_line, heading.end_line)
    return {
        "path": path,
        "section_id": section_id,
        "applied": not dry_run,
        "fingerprint": _fingerprint([path, section_id, refreshed]),
    }
