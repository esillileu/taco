from __future__ import annotations

from pathlib import Path

from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_tool

from .fixture_repo import write_context_repo, write_file


def test_task_complete_dry_run_preview_and_apply(tmp_path: Path) -> None:
    write_context_repo(tmp_path)
    state = load_repo_state(tmp_path)

    dry = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "implemented closeout flow",
            "verification": "all checks passed",
            "dry_run": True,
        },
    )
    assert dry["ok"] is True
    assert dry["data"]["applied"] is False
    assert dry["data"]["status_to"] == "done"
    assert dry["data"]["next_active_task"] == "T-011"

    apply = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "implemented closeout flow",
            "verification": "all checks passed",
            "dry_run": False,
        },
    )
    assert apply["ok"] is True
    assert apply["data"]["applied"] is True
    assert apply["data"]["next_active_task"] == "T-011"

    task_path = ".context/project/tasks/T-010-task-closeout-automation.md"
    task_text = (tmp_path / task_path).read_text(encoding="utf-8")
    assert "status: done" in task_text
    assert "- implemented closeout flow" in task_text
    assert "- all checks passed" in task_text

    plan_text = (tmp_path / ".context/project/plan.md").read_text(encoding="utf-8")
    assert "active_tasks:" in plan_text
    assert "- T-011" in plan_text
    assert "- T-010" not in plan_text.split("next_tasks:", 1)[1]
    assert "## Active Tasks" in plan_text
    assert "## Blocked Tasks" in plan_text
    assert "## Next Tasks" in plan_text
    assert "- [T-011](./tasks/T-011-feature-precision.md)" in plan_text
    assert "- [T-010](./tasks/T-010-task-closeout-automation.md)" not in plan_text


def test_task_complete_rejects_already_done_task(tmp_path: Path) -> None:
    write_context_repo(tmp_path)
    state = load_repo_state(tmp_path)

    first = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "done",
            "verification": "done",
            "dry_run": False,
        },
    )
    assert first["ok"] is True

    second = call_tool(
        load_repo_state(tmp_path),
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "again",
            "verification": "again",
            "dry_run": False,
        },
    )
    assert second["ok"] is False
    assert second["error"]["code"] == "task_already_done"


def test_task_complete_removes_task_from_blocked_queue(tmp_path: Path) -> None:
    write_context_repo(tmp_path)
    plan_path = tmp_path / ".context/project/plan.md"
    current = plan_path.read_text(encoding="utf-8")
    plan_path.write_text(
        current.replace("blocked_tasks: []", "blocked_tasks:\n  - T-010"),
        encoding="utf-8",
    )

    applied = call_tool(
        load_repo_state(tmp_path),
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "design-sync: updated ARCH-INDEX",
            "verification": (
                "design-sync: updated "
                ".context/project/architecture/index.md"
            ),
            "dry_run": False,
        },
    )
    assert applied["ok"] is True

    updated_plan = plan_path.read_text(encoding="utf-8")
    assert "- T-010" not in updated_plan.split("blocked_tasks:", 1)[1]


def test_task_complete_requires_design_sync_for_refactor_major(tmp_path: Path) -> None:
    write_context_repo(tmp_path)
    write_file(
        tmp_path,
        ".context/project/intents/I-020-refactor.md",
        "\n".join(
            [
                "---",
                "id: I-020",
                "type: intent",
                "title: refactor lane",
                "status: active",
                "kind: refactor",
                "design_impact: major",
                "plan_ref: PLAN-MAIN",
                "task_refs: [T-010]",
                "links: [PLAN-MAIN, ARCH-INDEX, T-010]",
                "---",
                "",
                "# Intent: I-020-refactor",
                "",
            ]
        ),
    )
    state = load_repo_state(tmp_path)

    missing = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "split modules",
            "verification": "unit tests passed",
            "dry_run": True,
        },
    )
    assert missing["ok"] is False
    assert missing["error"]["code"] == "design_sync_required"

    ok = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "design-sync: updated FLOW-MODE-TRANSITION",
            "verification": (
                "design-sync: updated "
                ".context/project/architecture/index.md"
            ),
            "dry_run": True,
        },
    )
    assert ok["ok"] is True
    assert ok["data"]["design_sync_required_for"] == [
        {"intent_id": "I-020", "design_impact": "major"}
    ]

