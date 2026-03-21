from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

from taco.core.plan import RepoState, ToolError, _compose_front_matter, _fingerprint
from taco.core.usecases.io import write_text

from .intent_helpers import next_task_id, tasks_dir_from_config

_REQUIRED_HEADINGS = (
    "Intent",
    "Goal",
    "Scope",
    "Implementation Approach",
    "Verification Approach",
    "Implementation Result",
    "Verification Result",
)


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return normalized or "task"


def _normalize_text(value: Any) -> str:
    # CLI payloads may encode newlines as literal "\n"; normalize for validation/render.
    text = str(value)
    return text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")


def _validate_task_content(sections: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for heading in _REQUIRED_HEADINGS:
        value = sections.get(heading)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"missing_section:{heading}")
    scope = _normalize_text(sections.get("Scope", "")).lower()
    if "out of scope" not in scope:
        issues.append("scope_out_of_scope_missing")
    impl = (
        _normalize_text(sections.get("Implementation Approach", ""))
        .strip()
        .splitlines()
    )
    if len([line for line in impl if line.strip()]) < 2:
        issues.append("implementation_approach_too_thin")
    verify_raw = _normalize_text(sections.get("Verification Approach", "")).lower()
    verify_lines = [line for line in verify_raw.splitlines() if line.strip()]
    if len(verify_lines) < 2:
        issues.append("verification_approach_too_thin")
    verify_tokens = ("uv run", "assert", "check", "verify")
    if not any(token in verify_raw for token in verify_tokens):
        issues.append("verification_command_or_condition_missing")
    return issues


def _render_task_body(sections: dict[str, Any]) -> str:
    blocks: list[str] = []
    for heading in _REQUIRED_HEADINGS:
        blocks.append(f"## {heading}")
        blocks.append("")
        blocks.append(_normalize_text(sections[heading]).rstrip())
        blocks.append("")
    title = str(sections.get("title_hint", "")).strip() or "submitted-task"
    return "\n".join([f"# Task: {title}", "", *blocks]).rstrip() + "\n"


def plan_task_submit_many(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    tasks = args.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ToolError(
            "invalid_input",
            "tasks must be a non-empty array",
            {"key": "tasks"},
        )
    applied: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    task_index = dict(state.index.task_index)
    tasks_dir = tasks_dir_from_config(state)
    for idx, raw in enumerate(tasks):
        if not isinstance(raw, dict):
            rejected.append({"index": idx, "code": "invalid_task_item"})
            continue
        front_matter = raw.get("front_matter")
        sections = raw.get("sections")
        intent_id = str(raw.get("intent_id", "")).strip()
        if (
            not isinstance(front_matter, dict)
            or not isinstance(sections, dict)
            or not intent_id
        ):
            rejected.append(
                {
                    "index": idx,
                    "code": "missing_required_fields",
                    "required": ["front_matter", "sections", "intent_id"],
                }
            )
            continue
        issues = _validate_task_content(sections)
        if issues:
            rejected.append(
                {"index": idx, "code": "task_content_invalid", "issues": issues}
            )
            continue
        task_id = str(front_matter.get("id", "")).strip()
        if not task_id:
            task_id = next_task_id(task_index)
            front_matter["id"] = task_id
        title = str(front_matter.get("title", "")).strip() or (
            f"{task_id}-{_slugify(intent_id)}"
        )
        front_matter["title"] = title
        front_matter.setdefault("type", "task")
        front_matter.setdefault("status", "active")
        front_matter.setdefault("plan_ref", "PLAN-MAIN")
        links = front_matter.get("links")
        if not isinstance(links, list):
            links = []
        if intent_id not in links:
            links.append(intent_id)
        front_matter["links"] = links
        refs = front_matter.get("references")
        if not isinstance(refs, dict):
            rejected.append({"index": idx, "code": "references_missing"})
            continue
        if not all(
            isinstance(refs.get(k), list) and refs.get(k)
            for k in ("modules", "flows", "schemas")
        ):
            rejected.append({"index": idx, "code": "references_invalid"})
            continue
        path = str(raw.get("path", "")).strip()
        if not path:
            path = str(PurePosixPath(tasks_dir) / f"{task_id}-{_slugify(title)}.md")
        sections_with_hint = dict(sections)
        sections_with_hint["title_hint"] = title
        body = _render_task_body(sections_with_hint)
        text = _compose_front_matter(front_matter, body)
        write_text(state, path, text)
        task_index[task_id] = path
        applied.append(
            {
                "task_id": task_id,
                "path": path,
                "fingerprint": _fingerprint([task_id, path, title, intent_id]),
            }
        )
    if rejected:
        raise ToolError(
            "task_submit_failed",
            "one or more tasks failed validation",
            {"applied_tasks": applied, "rejected_tasks": rejected},
        )
    return {
        "applied_tasks": applied,
        "rejected_tasks": [],
        "next_action": {"tool": "plan.intent.review_bundle"},
    }
