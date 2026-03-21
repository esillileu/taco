from __future__ import annotations

from pathlib import Path

from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_tool

from .fixture_repo import write_fixture_repo


def test_integration_happy_path_for_all_tools(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)

    assert call_tool(state, "task.list", {})["ok"] is True
    assert call_tool(state, "task.pack", {"task_id": "T-006"})["ok"] is True
    assert call_tool(state, "plan.pack", {"task_id": "T-006"})["ok"] is True
    assert call_tool(state, "plan.mode.guide", {})["ok"] is True
    assert call_tool(state, "plan.task.template", {"intent_id": "I-001"})["ok"] is True
    assert (
        call_tool(
            state,
            "plan.task.lint",
            {"path": "docs/dev/tasks/T-006-integration-tests.md", "intent_id": "I-001"},
        )["ok"]
        is True
    )
    assert call_tool(state, "plan.intent.list", {})["ok"] is True
    assert call_tool(state, "plan.intent.template", {})["ok"] is True
    assert call_tool(state, "plan.intent.view", {"intent_id": "I-001"})["ok"] is True
    assert call_tool(state, "plan.intent.index", {"intent_id": "I-001"})["ok"] is True
    assert (
        call_tool(state, "plan.intent.validate", {"intent_id": "I-001"})["ok"] is True
    )
    assert (
        call_tool(
            state,
            "task.targets",
            {"task_id": "T-006", "route_type": "implementation_result"},
        )["ok"]
        is True
    )
    assert (
        call_tool(
            state,
            "task.record",
            {
                "task_id": "T-006",
                "route_type": "verification_result",
                "content": "verified",
                "dry_run": True,
            },
        )["ok"]
        is True
    )
    assert (
        call_tool(
            state,
            "task.block",
            {
                "task_id": "T-006",
                "reason_code": "scope_split_required",
                "reason": "needs split before continue",
                "dry_run": True,
            },
        )["ok"]
        is True
    )
    assert call_tool(state, "plan.view", {})["ok"] is True
    assert (
        call_tool(
            state,
            "plan.locate",
            {"change_type": "task", "target": "T-006"},
        )["ok"]
        is True
    )
    assert (
        call_tool(
            state,
            "plan.locate",
            {"change_type": "intent", "target": "I-001"},
        )["ok"]
        is True
    )
    created = call_tool(
        load_repo_state(tmp_path),
        "plan.intent.create_many",
        {
            "intents": [
                {
                    "title": "Intent from decomposition",
                    "intent": "Capture user design as first-class planning intent.",
                }
            ]
        },
    )
    assert created["ok"] is True
    assert created["data"]["count"] == 1
    submitted = call_tool(
        load_repo_state(tmp_path),
        "plan.intent.submit_many",
        {
            "intents": [
                {
                    "title": "Intent from submit_many",
                    "intent": "Capture decomposition through submit path.",
                    "scope_in": ["plan mode"],
                    "scope_out": ["runtime coding"],
                }
            ]
        },
    )
    assert submitted["ok"] is True
    assert submitted["data"]["count"] == 1
    assert call_tool(state, "plan.validate", {})["ok"] is True
    assert (
        call_tool(
            state,
            "doc.snippet",
            {"path": "docs/architecture.md", "anchor_id": "system"},
        )["ok"]
        is True
    )
    assert (
        call_tool(
            state,
            "doc.section.get",
            {"path": "docs/dev/tasks/T-006-integration-tests.md", "section_id": "goal"},
        )["ok"]
        is True
    )
    assert (
        call_tool(
            state,
            "build.precheck",
            {"pack": call_tool(state, "task.pack", {"task_id": "T-006"})["data"]},
        )["ok"]
        is True
    )
    assert (
        call_tool(state, "issue.triage", {"title": "fix broken target"})["ok"] is True
    )
    assert call_tool(state, "convention.get", {"topic": "git"})["ok"] is True


def test_integration_invalid_input_and_missing_cases(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)

    invalid_pack = call_tool(state, "task.pack", {"task_id": ""})
    assert invalid_pack["ok"] is False
    assert invalid_pack["error"]["code"] == "invalid_input"

    missing_task = call_tool(state, "task.pack", {"task_id": "T-999"})
    assert missing_task["ok"] is False
    assert missing_task["error"]["code"] == "task_not_found"

    missing_anchor = call_tool(
        state,
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "missing-anchor"},
    )
    assert missing_anchor["ok"] is False
    assert missing_anchor["error"]["code"] == "anchor_not_found"


def test_integration_is_deterministic_for_repeated_calls(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)
    first = call_tool(state, "task.pack", {"task_id": "T-006"})
    second = call_tool(state, "task.pack", {"task_id": "T-006"})
    assert first == second
