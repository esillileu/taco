from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState

from .pack_builder import pack_with_refs, plan_pack
from .pack_readiness import ensure_task_readiness_for_pack, task_pack_readiness_missing
from .pack_selector import select_task_id_for_pack


def _task_list(state: RepoState, _: dict[str, Any]) -> dict[str, Any]:
    items = [
        {"task_id": task_id, "path": path}
        for task_id, path in sorted(state.index.task_index.items())
    ]
    return {"tasks": items}


def _task_pack(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = select_task_id_for_pack(state, args)
    ensure_task_readiness_for_pack(state, task_id)
    return pack_with_refs(state, args, task_id, "task.pack")


def _plan_pack(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    return plan_pack(state, args)


def _task_pack_readiness_missing(state: RepoState, task_id: str) -> list[str]:
    return task_pack_readiness_missing(state, task_id)
