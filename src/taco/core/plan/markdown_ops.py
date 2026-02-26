from __future__ import annotations

from typing import Any

from taco.core.plan.types import ToolError


def _slice_text(text: str, start_line: int, end_line: int) -> str:
    lines = text.splitlines()
    start = max(start_line - 1, 0)
    end = min(end_line, len(lines))
    return "\n".join(lines[start:end]).strip()

def _append_under_heading(markdown_text: str, heading: str, line: str) -> str:
    lines = markdown_text.splitlines()
    marker = f"## {heading}"
    heading_idx = -1
    for idx, raw in enumerate(lines):
        if raw.strip() == marker:
            heading_idx = idx
            break
    if heading_idx < 0:
        raise ToolError(
            "target_heading_not_found",
            "target heading missing",
            {"heading": heading},
        )

    insert_idx = len(lines)
    for idx in range(heading_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            insert_idx = idx
            break
    next_lines = lines[:insert_idx] + [line] + lines[insert_idx:]
    return "\n".join(next_lines) + "\n"

def _replace_heading_block(markdown_text: str, heading: str, content: str) -> str:
    lines = markdown_text.splitlines()
    marker = f"## {heading}"
    heading_idx = -1
    for idx, raw in enumerate(lines):
        if raw.strip() == marker:
            heading_idx = idx
            break
    if heading_idx < 0:
        raise ToolError(
            "target_heading_not_found",
            "target heading missing",
            {"heading": heading},
        )
    end_idx = len(lines)
    for idx in range(heading_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            end_idx = idx
            break
    body = content.rstrip("\n")
    replacement = [marker]
    if body:
        replacement.extend(body.splitlines())
    result = lines[:heading_idx] + replacement + lines[end_idx:]
    return "\n".join(result) + "\n"

def _find_heading_by_section_id(doc: Any, section_id: str) -> Any | None:
    sid = section_id.strip().lower()
    for heading in getattr(doc, "headings", []):
        anchor = str(getattr(heading, "anchor_id", "")).strip().lower()
        title = str(getattr(heading, "heading", "")).strip().lower()
        if sid in {anchor, title, title.replace(" ", "-")}:
            return heading
    return None

def _doc_patch_constraints(path: str) -> dict[str, Any]:
    if "/tasks/" in path:
        return {
            "allowed_in_build_mode": ["Implementation Result", "Verification Result"],
            "forbidden_ops": [],
        }
    if path.startswith(".context/project/architecture/"):
        return {
            "allowed_in_build_mode": [],
            "forbidden_ops": [],
        }
    if path.startswith(".context/project/intents/"):
        return {
            "allowed_in_build_mode": [],
            "forbidden_ops": [],
        }
    if path.startswith(".context/project/plan.md"):
        return {
            "allowed_in_build_mode": [],
            "forbidden_ops": [],
        }
    return {
        "allowed_in_build_mode": [],
        "forbidden_ops": [],
    }

def _enforce_doc_patch_scope(mode: str, path: str, heading: str) -> None:
    if mode != "build":
        return
    constraints = _doc_patch_constraints(path)
    allowed = constraints.get("allowed_in_build_mode", [])
    if not isinstance(allowed, list):
        allowed = []
    if heading not in allowed:
        raise ToolError(
            "design_change_requires_plan",
            "build mode cannot edit this section",
            {"path": path, "heading": heading, "mode": mode},
        )

def _preview_change(before: str, after: str) -> str:
    if before == after:
        return "(no change)"
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    if len(after_lines) >= len(before_lines):
        tail = after_lines[max(0, len(before_lines) - 1) :]
    else:
        tail = after_lines[-8:]
    return "\n".join(tail[-12:])

