from __future__ import annotations

from pathlib import Path

from taco.apps.cli import map_cli_to_tool
from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_tool

from .fixture_repo import write_fixture_repo


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

