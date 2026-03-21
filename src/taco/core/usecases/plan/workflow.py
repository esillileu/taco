from __future__ import annotations

from taco.core.plan import RepoState, ToolError

from .design_submit import plan_design_submit_changes
from .mode_guide import plan_mode_guide
from .task_frontmatter_sync import plan_task_frontmatter_sync
from .task_lint import plan_task_lint
from .task_submit import plan_task_submit_many
from .task_template import plan_task_template


def _plan_mode_guide(state: RepoState, args: dict[str, object]) -> dict[str, object]:
    return plan_mode_guide(state, args)


def _plan_design_submit_changes(
    state: RepoState, args: dict[str, object]
) -> dict[str, object]:
    changes = args.get("changes")
    if not isinstance(changes, list):
        raise ToolError("invalid_input", "changes must be an array", {"key": "changes"})
    return plan_design_submit_changes(state, {"changes": changes})


def _plan_task_submit_many(
    state: RepoState, args: dict[str, object]
) -> dict[str, object]:
    tasks = args.get("tasks")
    if not isinstance(tasks, list):
        raise ToolError("invalid_input", "tasks must be an array", {"key": "tasks"})
    return plan_task_submit_many(state, {"tasks": tasks})


def _plan_task_template(
    state: RepoState, args: dict[str, object]
) -> dict[str, object]:
    intent_id = args.get("intent_id")
    if not isinstance(intent_id, str) or not intent_id.strip():
        raise ToolError("invalid_input", "intent_id is required", {"key": "intent_id"})
    payload: dict[str, object] = {"intent_id": intent_id.strip()}
    task_id = args.get("task_id")
    if task_id is not None:
        if not isinstance(task_id, str):
            raise ToolError(
                "invalid_input", "task_id must be string", {"key": "task_id"}
            )
        payload["task_id"] = task_id.strip()
    return plan_task_template(state, payload)


def _plan_task_frontmatter_sync(
    state: RepoState, args: dict[str, object]
) -> dict[str, object]:
    intent_id = args.get("intent_id")
    path = args.get("path")
    if not isinstance(intent_id, str) or not intent_id.strip():
        raise ToolError("invalid_input", "intent_id is required", {"key": "intent_id"})
    if not isinstance(path, str) or not path.strip():
        raise ToolError("invalid_input", "path is required", {"key": "path"})
    payload: dict[str, object] = {"intent_id": intent_id.strip(), "path": path.strip()}
    front_matter = args.get("front_matter")
    if front_matter is not None:
        if not isinstance(front_matter, dict):
            raise ToolError(
                "invalid_input",
                "front_matter must be object",
                {"key": "front_matter"},
            )
        payload["front_matter"] = front_matter
    return plan_task_frontmatter_sync(state, payload)


def _plan_task_lint(state: RepoState, args: dict[str, object]) -> dict[str, object]:
    path = args.get("path")
    if not isinstance(path, str) or not path.strip():
        raise ToolError("invalid_input", "path is required", {"key": "path"})
    payload: dict[str, object] = {"path": path.strip()}
    intent_id = args.get("intent_id")
    if intent_id is not None:
        if not isinstance(intent_id, str):
            raise ToolError(
                "invalid_input", "intent_id must be string", {"key": "intent_id"}
            )
        payload["intent_id"] = intent_id.strip()
    return plan_task_lint(state, payload)
