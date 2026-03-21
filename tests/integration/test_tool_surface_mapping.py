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
        ("plan", "mode.guide", {}),
        ("plan", "task.template", {"intent_id": "I-001"}),
        (
            "plan",
            "task.lint",
            {"path": "docs/dev/tasks/T-006-integration-tests.md", "intent_id": "I-001"},
        ),
        ("plan", "pack", {"task_id": "T-006"}),
        ("plan", "intent.list", {}),
        ("plan", "intent.template", {}),
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
        if action == "mode.guide":
            tool = "plan.mode.guide"
        if action == "intent.list":
            tool = "plan.intent.list"
        if action == "intent.template":
            tool = "plan.intent.template"
        if action == "intent.submit-many":
            tool = "plan.intent.submit_many"
        if action == "intent.view":
            tool = "plan.intent.view"
        if action == "intent.index":
            tool = "plan.intent.index"
        if action == "intent.validate":
            tool = "plan.intent.validate"
        if action == "intent.propose":
            tool = "plan.intent.propose"
        if action == "task.template":
            tool = "plan.task.template"
        if action == "task.lint":
            tool = "plan.task.lint"
        assert call_tool(state, tool_name, mapped_payload) == call_tool(
            state, tool, payload
        )

    text_payload = {
        "intent_text": "Capture natural language planning input.",
        "title": "Natural Language Intake",
    }
    tool_name, mapped_payload = map_cli_to_tool("plan", "intent.propose", text_payload)
    left = call_tool(load_repo_state(tmp_path), tool_name, mapped_payload)
    right = call_tool(load_repo_state(tmp_path), "plan.intent.propose", text_payload)
    assert left["ok"] is True
    assert right["ok"] is True
    assert left["data"]["created_intent"] is True
    assert right["data"]["created_intent"] is True
    assert left["data"]["intent"]["title"] == right["data"]["intent"]["title"]

    create_payload = {
        "intents": [
            {
                "title": "Create Intent A",
                "intent": "Capture decomposed planning objective A.",
            },
            {
                "title": "Create Intent B",
                "intent": "Capture decomposed planning objective B.",
            },
        ]
    }
    tool_name, mapped_payload = map_cli_to_tool(
        "plan", "intent.create-many", create_payload
    )
    created = call_tool(load_repo_state(tmp_path), tool_name, mapped_payload)
    assert created["ok"] is True
    assert created["data"]["count"] == 2

    submit_payload = {
        "intents": [
            {
                "title": "Submitted intent",
                "intent": "intent text",
                "scope_in": ["scope"],
                "scope_out": ["out"],
            }
        ]
    }
    tool_name, mapped_payload = map_cli_to_tool(
        "plan",
        "intent.submit-many",
        submit_payload,
    )
    left_submit = call_tool(load_repo_state(tmp_path), tool_name, mapped_payload)
    right_submit = call_tool(
        load_repo_state(tmp_path), "plan.intent.submit_many", submit_payload
    )
    assert left_submit["ok"] is True
    assert right_submit["ok"] is True
    assert left_submit["data"]["count"] == right_submit["data"]["count"]

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
