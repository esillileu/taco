from __future__ import annotations

import hashlib
from posixpath import dirname, relpath
from typing import Any

from taco.core.plan.types import ToolError


def _fingerprint(parts: list[str]) -> str:
    normalized = "|".join(part.strip() for part in parts if part.strip())
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return digest[:16]

def _intent_kind(meta: dict[str, Any]) -> str:
    value = meta.get("kind", "")
    if isinstance(value, str) and value.strip():
        return value.strip().lower()
    return "general"

def _intent_design_impact(meta: dict[str, Any]) -> str:
    value = meta.get("design_impact", "")
    if isinstance(value, str) and value.strip():
        return value.strip().lower()
    return "unspecified"

def _is_promotable_task(task_id: str, task_documents: tuple[Any, ...]) -> bool:
    for doc in task_documents:
        if getattr(doc, "task_id", None) != task_id:
            continue
        meta = getattr(doc, "metadata", {})
        if not isinstance(meta, dict):
            return True
        status = meta.get("status")
        if isinstance(status, str) and status.strip() in {"done", "blocked"}:
            return False
        return True
    return True

def _replace_plan_task_section(
    lines: list[str], section_heading: str, entries: list[str]
) -> list[str]:
    marker = f"## {section_heading}"
    heading_idx = -1
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            heading_idx = idx
            break
    if heading_idx < 0:
        return lines

    start = heading_idx + 1
    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break

    replacement: list[str] = [""]
    replacement.extend(entries)
    replacement.append("")
    return lines[:start] + replacement + lines[end:]

def _format_plan_task_entries(
    task_ids: list[str], plan_path: str, task_index: dict[str, str]
) -> list[str]:
    return [
        _format_plan_task_entry(task_id, plan_path=plan_path, task_index=task_index)
        for task_id in task_ids
    ]

def _format_plan_task_entry(
    task_id: str, plan_path: str, task_index: dict[str, str]
) -> str:
    task_path = task_index.get(task_id)
    if not task_path:
        return f"- `{task_id}`"
    relative = relpath(task_path, start=dirname(plan_path))
    if not relative.startswith("."):
        relative = f"./{relative}"
    return f"- [{task_id}]({relative})"

def _sync_plan_task_sections(
    body: str,
    plan_path: str,
    task_index: dict[str, str],
    active_tasks: list[str],
    blocked_tasks: list[str],
    next_tasks: list[str],
) -> str:
    lines = body.splitlines()
    lines = _replace_plan_task_section(
        lines,
        section_heading="Active Tasks",
        entries=_format_plan_task_entries(active_tasks, plan_path, task_index),
    )
    lines = _replace_plan_task_section(
        lines,
        section_heading="Blocked Tasks",
        entries=_format_plan_task_entries(blocked_tasks, plan_path, task_index),
    )
    lines = _replace_plan_task_section(
        lines,
        section_heading="Next Tasks",
        entries=_format_plan_task_entries(next_tasks, plan_path, task_index),
    )
    return "\n".join(lines).rstrip()

def _validate_pack_v3(pack: dict[str, Any]) -> None:
    version = str(pack.get("pack_version", "")).strip()
    if version != "3":
        raise ToolError(
            "pack_required",
            "build tools require pack version 3",
            {"pack_version": version or "(missing)"},
        )

