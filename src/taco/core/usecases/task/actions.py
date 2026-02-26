from __future__ import annotations

from pathlib import Path
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _append_under_heading,
    _required_str,
)
from taco.core.routing.router import resolve_write_target
from taco.core.usecases.io import read_text, write_text
from taco.core.usecases.task.block import _task_block
from taco.core.usecases.task.complete import _task_complete


def _task_targets(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    route_type = _required_str(args, "route_type")
    target = resolve_write_target(task_id, route_type, state.index, state.router_config)
    return target.to_dict()

def _task_record(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    route_type = _required_str(args, "route_type")
    content = _required_str(args, "content")
    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})

    target = resolve_write_target(task_id, route_type, state.index, state.router_config)
    if dry_run:
        return {
            "target": target.to_dict(),
            "applied": False,
            "preview": f"- {content}",
        }

    path = Path(target.path)
    original = read_text(state, path.as_posix())
    updated = _append_under_heading(original, target.heading, f"- {content}")
    write_text(state, path.as_posix(), updated)
    return {
        "target": target.to_dict(),
        "applied": True,
        "path": target.path,
    }

__all__ = [
    "_task_targets",
    "_task_record",
    "_task_complete",
    "_task_block",
]
