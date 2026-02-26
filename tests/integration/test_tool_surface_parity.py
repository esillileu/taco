from __future__ import annotations

from pathlib import Path

from taco.apps.cli import map_cli_to_tool
from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_tool

from .fixture_repo import write_fixture_repo


def test_integration_happy_path_for_all_tools(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)

    assert call_tool(state, "task.list", {})["ok"] is True
    assert call_tool(state, "task.pack", {"task_id": "T-006"})["ok"] is True
    assert call_tool(state, "plan.pack", {"task_id": "T-006"})["ok"] is True
    assert call_tool(state, "plan.intent.list", {})["ok"] is True
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


def test_cli_mapping_parity_with_mcp_calls(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)

    tool_name, payload = map_cli_to_tool("task", "pack", {"task_id": "T-006"})
    assert call_tool(state, tool_name, payload) == call_tool(
        state, "task.pack", {"task_id": "T-006"}
    )

    tool_name, payload = map_cli_to_tool(
        "doc", "snippet", {"path": "docs/architecture.md", "anchor_id": "system"}
    )
    assert call_tool(state, tool_name, payload) == call_tool(
        state,
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
    )

    tool_name, payload = map_cli_to_tool(
        "task",
        "block",
        {
            "task_id": "T-006",
            "reason_code": "verification_ambiguous",
            "reason": "checklist unclear",
            "dry_run": True,
        },
    )
    assert call_tool(state, tool_name, payload) == call_tool(
        state,
        "task.block",
        {
            "task_id": "T-006",
            "reason_code": "verification_ambiguous",
            "reason": "checklist unclear",
            "dry_run": True,
        },
    )

    for domain, action, payload in [
        ("plan", "view", {}),
        ("plan", "pack", {"task_id": "T-006"}),
        ("plan", "intent.list", {}),
        ("plan", "intent.view", {"intent_id": "I-001"}),
        ("plan", "intent.index", {"intent_id": "I-001"}),
        ("plan", "intent.validate", {"intent_id": "I-001"}),
        ("plan", "intent.propose", {"intent_id": "I-001"}),
    ]:
        tool_name, mapped_payload = map_cli_to_tool(domain, action, payload)
        tool_action = action.replace("-", "_")
        if domain == "plan" and action.startswith("intent."):
            tool = f"plan.{tool_action}"
        else:
            tool = f"{domain}.{tool_action}" if action != "view" else "plan.view"
        if action == "pack":
            tool = "plan.pack"
        if action == "intent.list":
            tool = "plan.intent.list"
        if action == "intent.view":
            tool = "plan.intent.view"
        if action == "intent.index":
            tool = "plan.intent.index"
        if action == "intent.validate":
            tool = "plan.intent.validate"
        if action == "intent.propose":
            tool = "plan.intent.propose"
        assert call_tool(state, tool_name, mapped_payload) == call_tool(
            state, tool, payload
        )

    cli_result = call_tool(state, "plan.intent.propose", {"intent_id": "I-001"})
    proposal_fingerprint = cli_result["data"]["proposal_fingerprint"]
    tool_name, payload = map_cli_to_tool(
        "plan",
        "intent.autodesign",
        {"intent_id": "I-001", "proposal_fingerprint": proposal_fingerprint},
    )
    assert call_tool(state, tool_name, payload) == call_tool(
        state,
        "plan.intent.autodesign",
        {"intent_id": "I-001", "proposal_fingerprint": proposal_fingerprint},
    )


def test_cli_mapping_supports_init_bootstrap_command() -> None:
    tool_name, payload = map_cli_to_tool("init", "", {})
    assert tool_name == "project.init"
    assert payload == {}
