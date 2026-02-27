from __future__ import annotations

from typing import Any

from taco.core.plan import (
    ToolError,
    _compose_front_matter,
    _is_promotable_task,
    _split_front_matter,
    _sync_plan_task_sections,
)


def _advance_plan_for_completed_task(
    plan_text: str,
    completed_task_id: str,
    task_index: dict[str, str],
    task_documents: tuple[Any, ...],
    plan_path: str,
) -> tuple[str, str | None]:
    meta, body = _split_front_matter(plan_text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"document": "plan"},
        )
    active = meta.get("active_tasks", [])
    blocked = meta.get("blocked_tasks", [])
    next_tasks = meta.get("next_tasks", [])
    if not isinstance(active, list) or not isinstance(blocked, list) or not isinstance(
        next_tasks, list
    ):
        raise ToolError(
            "invalid_plan_meta",
            "active_tasks, blocked_tasks, and next_tasks must be arrays",
            {"document": "plan"},
        )

    active_clean = [item for item in active if isinstance(item, str)]
    blocked_clean = [item for item in blocked if isinstance(item, str)]
    next_clean = [item for item in next_tasks if isinstance(item, str)]
    active_clean = [
        item for item in active_clean if _is_promotable_task(item, task_documents)
    ]
    next_clean = [
        item for item in next_clean if _is_promotable_task(item, task_documents)
    ]

    active_clean = [item for item in active_clean if item != completed_task_id]
    blocked_clean = [item for item in blocked_clean if item != completed_task_id]
    next_clean = [item for item in next_clean if item != completed_task_id]
    promoted: str | None = None
    remaining_next: list[str] = []
    for item in next_clean:
        if (
            promoted is None
            and item in task_index
            and item not in active_clean
            and _is_promotable_task(item, task_documents)
        ):
            promoted = item
            continue
        remaining_next.append(item)
    if promoted and promoted not in active_clean:
        active_clean.append(promoted)

    meta["active_tasks"] = active_clean
    meta["blocked_tasks"] = blocked_clean
    meta["next_tasks"] = remaining_next
    next_body = _sync_plan_task_sections(
        body=body,
        plan_path=plan_path,
        task_index=task_index,
        active_tasks=active_clean,
        blocked_tasks=blocked_clean,
        next_tasks=remaining_next,
    )
    return _compose_front_matter(meta, next_body), promoted

def _advance_plan_for_blocked_task(
    plan_text: str,
    blocked_task_id: str,
    task_index: dict[str, str],
    task_documents: tuple[Any, ...],
    plan_path: str,
) -> tuple[str, str | None]:
    meta, body = _split_front_matter(plan_text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"document": "plan"},
        )

    active = meta.get("active_tasks", [])
    blocked = meta.get("blocked_tasks", [])
    next_tasks = meta.get("next_tasks", [])
    if not isinstance(active, list) or not isinstance(blocked, list) or not isinstance(
        next_tasks, list
    ):
        raise ToolError(
            "invalid_plan_meta",
            "active_tasks, blocked_tasks, and next_tasks must be arrays",
            {"document": "plan"},
        )

    active_clean = [item for item in active if isinstance(item, str)]
    blocked_clean = [item for item in blocked if isinstance(item, str)]
    next_clean = [item for item in next_tasks if isinstance(item, str)]
    active_clean = [
        item for item in active_clean if _is_promotable_task(item, task_documents)
    ]
    next_clean = [
        item for item in next_clean if _is_promotable_task(item, task_documents)
    ]

    active_clean = [item for item in active_clean if item != blocked_task_id]
    next_clean = [item for item in next_clean if item != blocked_task_id]
    if blocked_task_id not in blocked_clean:
        blocked_clean.append(blocked_task_id)

    promoted: str | None = None
    remaining_next: list[str] = []
    for item in next_clean:
        if (
            promoted is None
            and item in task_index
            and item not in blocked_clean
            and _is_promotable_task(item, task_documents)
        ):
            promoted = item
            continue
        remaining_next.append(item)
    if promoted and promoted not in active_clean:
        active_clean.append(promoted)

    meta["active_tasks"] = active_clean
    meta["blocked_tasks"] = blocked_clean
    meta["next_tasks"] = remaining_next
    next_body = _sync_plan_task_sections(
        body=body,
        plan_path=plan_path,
        task_index=task_index,
        active_tasks=active_clean,
        blocked_tasks=blocked_clean,
        next_tasks=remaining_next,
    )
    return _compose_front_matter(meta, next_body), promoted
