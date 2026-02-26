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
from taco.core.task.design import (
    _has_design_sync_evidence,
    _required_refactor_design_sync,
)
from taco.core.task.plan_sync import _advance_plan_for_completed_task
from taco.core.usecases.io import read_text, write_text


def _task_complete(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    implementation = _required_str(args, "implementation")
    verification = _required_str(args, "verification")
    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})

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
    required_design_sync = _required_refactor_design_sync(state, task_id, task_meta)
    if isinstance(status, str) and status.strip() == "done":
        raise ToolError(
            "task_already_done",
            "task is already marked done",
            {"task_id": task_id},
        )
    if required_design_sync and not _has_design_sync_evidence(
        implementation, verification
    ):
        details: dict[str, Any] = {
            "task_id": task_id,
            "required_for_intents": required_design_sync,
            "required_marker": "design-sync:",
            "required_path_hint": ".context/project/architecture/*.md",
        }
        raise ToolError(
            "design_sync_required",
            "refactor task requires design-sync evidence before completion",
            details,
        )

    implementation_target = resolve_write_target(
        task_id, "implementation", state.index, state.router_config
    )
    verification_target = resolve_write_target(
        task_id, "verification", state.index, state.router_config
    )

    updated_task = _append_under_heading(
        task_text, implementation_target.heading, f"- {implementation}"
    )
    updated_task = _append_under_heading(
        updated_task, verification_target.heading, f"- {verification}"
    )
    updated_task = _set_front_matter_key(updated_task, "status", "done")

    plan_path = _plan_path_from_config(state.config_raw)
    plan_text = read_text(state, plan_path)
    updated_plan, promoted = _advance_plan_for_completed_task(
        plan_text,
        completed_task_id=task_id,
        task_index=state.index.task_index,
        task_documents=state.index.documents,
        plan_path=plan_path,
    )

    if dry_run:
        return {
            "task_id": task_id,
            "applied": False,
            "status_from": status if isinstance(status, str) else "unknown",
            "status_to": "done",
            "next_active_task": promoted,
            "task_target": task_path,
            "plan_target": plan_path,
            "task_preview": _preview_change(task_text, updated_task),
            "plan_preview": _preview_change(plan_text, updated_plan),
            "targets": {
                "implementation": implementation_target.to_dict(),
                "verification": verification_target.to_dict(),
            },
            "design_sync_required_for": required_design_sync,
        }

    write_text(state, task_path, updated_task)
    write_text(state, plan_path, updated_plan)
    return {
        "task_id": task_id,
        "applied": True,
        "status_from": status if isinstance(status, str) else "unknown",
        "status_to": "done",
        "next_active_task": promoted,
        "task_target": task_path,
        "plan_target": plan_path,
        "targets": {
            "implementation": implementation_target.to_dict(),
            "verification": verification_target.to_dict(),
        },
        "design_sync_required_for": required_design_sync,
    }
