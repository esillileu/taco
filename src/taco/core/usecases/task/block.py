from __future__ import annotations

from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _append_under_heading,
    _plan_path_from_config,
    _preview_change,
    _required_str,
    _set_front_matter_key,
    _split_front_matter,
)
from taco.core.routing.router import resolve_write_target
from taco.core.task.plan_sync import _advance_plan_for_blocked_task
from taco.core.usecases.io import read_text, write_text

BLOCK_REASON_CODES = (
    "architecture_change_required",
    "scope_split_required",
    "verification_ambiguous",
    "dependency_out_of_scope",
)

def _task_block(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    reason_code = _required_str(args, "reason_code")
    reason = _required_str(args, "reason")
    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})
    if reason_code not in BLOCK_REASON_CODES:
        raise ToolError(
            "invalid_reason_code",
            "reason_code is not supported",
            {"reason_code": reason_code},
        )

    task_path = state.index.task_index.get(task_id)
    if not task_path:
        raise ToolError(
            "task_not_found",
            "task id not found in index",
            {"task_id": task_id},
        )

    task_text = read_text(state, task_path)
    task_meta, _ = _split_front_matter(task_text)
    status = task_meta.get("status")
    if isinstance(status, str) and status.strip() == "done":
        raise ToolError(
            "task_state_conflict",
            "done task cannot be blocked",
            {"task_id": task_id, "status": "done"},
        )
    if isinstance(status, str) and status.strip() == "blocked":
        raise ToolError(
            "task_already_blocked",
            "task is already marked blocked",
            {"task_id": task_id},
        )

    implementation_target = resolve_write_target(
        task_id, "implementation", state.index, state.router_config
    )
    updated_task = _append_under_heading(
        task_text,
        implementation_target.heading,
        f"- blocked: [{reason_code}] {reason}",
    )
    updated_task = _set_front_matter_key(updated_task, "status", "blocked")

    plan_path = _plan_path_from_config(state.config_raw)
    plan_text = read_text(state, plan_path)
    updated_plan, promoted = _advance_plan_for_blocked_task(
        plan_text,
        blocked_task_id=task_id,
        task_index=state.index.task_index,
        task_documents=state.index.documents,
        plan_path=plan_path,
    )

    if dry_run:
        return {
            "task_id": task_id,
            "applied": False,
            "reason_code": reason_code,
            "reason": reason,
            "status_from": status if isinstance(status, str) else "unknown",
            "status_to": "blocked",
            "next_active_task": promoted,
            "task_target": task_path,
            "plan_target": plan_path,
            "task_preview": _preview_change(task_text, updated_task),
            "plan_preview": _preview_change(plan_text, updated_plan),
        }

    write_text(state, task_path, updated_task)
    write_text(state, plan_path, updated_plan)
    return {
        "task_id": task_id,
        "applied": True,
        "reason_code": reason_code,
        "reason": reason,
        "status_from": status if isinstance(status, str) else "unknown",
        "status_to": "blocked",
        "next_active_task": promoted,
        "task_target": task_path,
        "plan_target": plan_path,
    }
