from __future__ import annotations

from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _plan_path_from_config,
    _split_front_matter,
)
from taco.core.usecases.io import read_text


def select_task_id_for_pack(state: RepoState, args: dict[str, Any]) -> str:
    provided = args.get("task_id")
    if provided is not None:
        if not isinstance(provided, str) or not provided.strip():
            raise ToolError(
                "invalid_input",
                "task_id must be a non-empty string",
                {"key": "task_id"},
            )
        return provided.strip()

    plan_path = _plan_path_from_config(state.config_raw)
    text = state.index.document_texts.get(plan_path)
    if text is None:
        text = read_text(state, plan_path)
    meta, _ = _split_front_matter(text)
    if not meta:
        raise ToolError(
            "no_task_available",
            "no task available for automatic pack selection",
            {"reason": "plan_front_matter_missing", "plan_path": plan_path},
        )

    active_all = [
        item for item in meta.get("active_tasks", []) if isinstance(item, str)
    ]
    active = [item for item in active_all if item in state.index.task_index]
    if len(active_all) > 1:
        raise ToolError(
            "ambiguous_active_tasks",
            "multiple active tasks found; specify task_id explicitly",
            {"active_tasks": active_all},
        )
    if active:
        return active[0]

    next_tasks = [item for item in meta.get("next_tasks", []) if isinstance(item, str)]
    for task_id in next_tasks:
        if task_id in state.index.task_index:
            return task_id

    raise ToolError(
        "no_task_available",
        "no task available for automatic pack selection",
        {
            "active_tasks": active_all,
            "next_tasks": next_tasks,
            "plan_path": plan_path,
        },
    )
