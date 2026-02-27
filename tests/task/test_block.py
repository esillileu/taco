from __future__ import annotations

from pathlib import Path

from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_tool

from .fixture_repo import write_context_repo


def test_task_block_dry_run_preview_and_apply(tmp_path: Path) -> None:
    write_context_repo(tmp_path)
    state = load_repo_state(tmp_path)

    dry = call_tool(
        state,
        "task.block",
        {
            "task_id": "T-010",
            "reason_code": "architecture_change_required",
            "reason": "schema boundary changed",
            "dry_run": True,
        },
    )
    assert dry["ok"] is True
    assert dry["data"]["applied"] is False
    assert dry["data"]["status_to"] == "blocked"
    assert dry["data"]["next_active_task"] == "T-011"

    apply = call_tool(
        state,
        "task.block",
        {
            "task_id": "T-010",
            "reason_code": "architecture_change_required",
            "reason": "schema boundary changed",
            "dry_run": False,
        },
    )
    assert apply["ok"] is True
    assert apply["data"]["applied"] is True
    assert apply["data"]["next_active_task"] == "T-011"

    task_path = ".context/project/tasks/T-010-task-closeout-automation.md"
    task_text = (tmp_path / task_path).read_text(encoding="utf-8")
    assert "status: blocked" in task_text
    assert (
        "- blocked: [architecture_change_required] schema boundary changed"
        in task_text
    )

    plan_text = (tmp_path / ".context/project/plan.md").read_text(encoding="utf-8")
    assert "- T-010" in plan_text.split("blocked_tasks:", 1)[1]
    assert "## Blocked Tasks" in plan_text
    assert "- [T-010](./tasks/T-010-task-closeout-automation.md)" in plan_text


def test_task_block_rejects_invalid_reason_code_and_done_status(tmp_path: Path) -> None:
    write_context_repo(tmp_path)
    state = load_repo_state(tmp_path)

    invalid = call_tool(
        state,
        "task.block",
        {
            "task_id": "T-010",
            "reason_code": "bad_reason",
            "reason": "x",
            "dry_run": True,
        },
    )
    assert invalid["ok"] is False
    assert invalid["error"]["code"] == "invalid_reason_code"

    done = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "done",
            "verification": "done",
            "dry_run": False,
        },
    )
    assert done["ok"] is True

    blocked_after_done = call_tool(
        load_repo_state(tmp_path),
        "task.block",
        {
            "task_id": "T-010",
            "reason_code": "scope_split_required",
            "reason": "needs split",
            "dry_run": False,
        },
    )
    assert blocked_after_done["ok"] is False
    assert blocked_after_done["error"]["code"] == "task_state_conflict"

