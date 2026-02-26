from __future__ import annotations

from pathlib import Path

import yaml

from taco.cli import map_cli_to_tool
from taco.tools import call_tool, load_repo_state


def _write_fixture_repo(root: Path) -> None:
    (root / "docs" / "dev" / "tasks").mkdir(parents=True)
    (root / "docs" / "dev" / "git").mkdir(parents=True)
    (root / "docs" / "intents").mkdir(parents=True)

    (root / "docs" / "intent.md").write_text(
        "\n".join(
            [
                "---",
                "id: PROJ-INTENT",
                "type: anchor",
                "title: Intent",
                "status: active",
                "links: []",
                "---",
                "",
                "# Intent",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "architecture.md").write_text(
        "\n".join(
            [
                "---",
                "id: ARCH-INDEX",
                "type: anchor",
                "title: Architecture",
                "status: active",
                "links: []",
                "---",
                "",
                "# Architecture",
                "## System",
                "<!-- taco:pack=arch.snippets -->",
                "system detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "plan.md").write_text(
        "\n".join(
            [
                "---",
                "id: PLAN-MAIN",
                "type: plan",
                "title: Plan",
                "status: active",
                "active_tasks: []",
                "blocked_tasks: []",
                "next_tasks: []",
                "links: []",
                "---",
                "",
                "# Plan",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "glossary.md").write_text(
        "\n".join(
            [
                "---",
                "id: SCH-GLOSSARY",
                "type: schema",
                "title: Glossary",
                "status: active",
                "links: []",
                "---",
                "",
                "# Glossary",
                "## Terms",
                "<!-- taco:pack=glossary.terms -->",
                "term detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "principles.md").write_text(
        "\n".join(
            [
                "---",
                "id: GOV-CODE-PRINCIPLES",
                "type: governance",
                "title: Principles",
                "status: active",
                "links: []",
                "---",
                "",
                "# Principles",
                "## Rules",
                "<!-- taco:pack=principles.snippets -->",
                "rules detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "doc-index.md").write_text(
        "\n".join(
            [
                "---",
                "id: GOV-DOC-INDEX",
                "type: governance",
                "title: Doc Guide",
                "status: active",
                "links: []",
                "---",
                "",
                "# Doc Guide",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (root / "docs" / "dev" / "git.md").write_text("# Git Rules\n", encoding="utf-8")
    (root / "docs" / "dev" / "tasks" / "T-006-integration-tests.md").write_text(
        "\n".join(
            [
                "---",
                "id: T-006",
                "type: task",
                "title: T-006-integration-tests",
                "status: active",
                "plan_ref: PLAN-MAIN",
                "scope:",
                "  in: []",
                "  out: []",
                "references:",
                "  modules: [ARCH-INDEX]",
                "  flows: [PLAN-MAIN]",
                "  schemas: [GOV-CODE-PRINCIPLES]",
                "  governance: [GOV-CODE-PRINCIPLES]",
                "links: [PLAN-MAIN]",
                "---",
                "",
                "# Task: T-006-integration-tests",
                "## Intent",
                "<!-- taco:pack=task.core -->",
                "intent detail",
                "## Goal",
                "<!-- taco:pack=task.core -->",
                "goal detail",
                "## Scope",
                "<!-- taco:pack=task.core,pack.next_actions -->",
                "- start integration checks",
                "scope detail",
                "## Implementation Approach",
                "<!-- taco:pack=task.plans,pack.next_actions -->",
                "1. run tool integration",
                "impl detail",
                "## Verification Approach",
                "<!-- taco:pack=task.plans,pack.acceptance_checks,"
                "pack.verification_commands -->",
                "- ensure pack deterministic",
                "- uv run --extra dev pytest -q",
                "verify detail",
                "## Implementation Result",
                "Pending",
                "## Verification Result",
                "Pending",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "intents" / "I-001-plan-mode.md").write_text(
        "\n".join(
            [
                "---",
                "id: I-001",
                "type: intent",
                "title: plan mode intent",
                "status: active",
                "plan_ref: PLAN-MAIN",
                "task_refs: [T-006]",
                "links: [PLAN-MAIN, T-006, ARCH-INDEX]",
                "---",
                "",
                "# Intent: I-001-plan-mode",
            ]
        ),
        encoding="utf-8",
    )

    config = {
        "docs": {
            "intent": "docs/intent.md",
            "architecture": "docs/architecture.md",
            "plan": "docs/plan.md",
            "doc_map": "docs/dev/doc-index.md",
            "glossary": "docs/glossary.md",
            "principles": ["docs/dev/principles.md"],
            "todo": ["docs/dev/todo.md"],
            "tasks_glob": "docs/dev/tasks/T-*.md",
        },
        "budget": {
            "default_tokens": 100,
            "priority_order": [
                "task.core",
                "task.plans",
                "arch.snippets",
                "principles.snippets",
                "glossary.terms",
            ],
            "required_groups": [
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ],
        },
        "modules": {"git": {"path": "docs/dev/git.md"}},
    }
    (root / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


def test_integration_happy_path_for_all_tools(tmp_path: Path) -> None:
    _write_fixture_repo(tmp_path)
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
    assert call_tool(
        state,
        "task.targets",
        {"task_id": "T-006", "route_type": "implementation_result"},
    )["ok"] is True
    assert call_tool(
        state,
        "task.record",
        {
            "task_id": "T-006",
            "route_type": "verification_result",
            "content": "verified",
            "dry_run": True,
        },
    )["ok"] is True
    assert call_tool(
        state,
        "task.block",
        {
            "task_id": "T-006",
            "reason_code": "scope_split_required",
            "reason": "needs split before continue",
            "dry_run": True,
        },
    )["ok"] is True
    assert call_tool(state, "plan.view", {})["ok"] is True
    assert call_tool(
        state,
        "plan.locate",
        {"change_type": "task", "target": "T-006"},
    )["ok"] is True
    assert call_tool(
        state,
        "plan.locate",
        {"change_type": "intent", "target": "I-001"},
    )["ok"] is True
    assert call_tool(state, "plan.validate", {})["ok"] is True
    assert call_tool(
        state,
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
    )["ok"] is True
    section = call_tool(
        state,
        "doc.section.get",
        {"path": "docs/dev/tasks/T-006-integration-tests.md", "section_id": "goal"},
    )
    assert section["ok"] is True
    assert call_tool(
        state,
        "build.precheck",
        {"pack": call_tool(state, "task.pack", {"task_id": "T-006"})["data"]},
    )["ok"] is True
    assert call_tool(
        state, "issue.triage", {"title": "fix broken target"}
    )["ok"] is True
    assert call_tool(state, "convention.get", {"topic": "git"})["ok"] is True


def test_integration_invalid_input_and_missing_cases(tmp_path: Path) -> None:
    _write_fixture_repo(tmp_path)
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
    _write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)
    first = call_tool(state, "task.pack", {"task_id": "T-006"})
    second = call_tool(state, "task.pack", {"task_id": "T-006"})
    assert first == second


def test_cli_mapping_parity_with_mcp_calls(tmp_path: Path) -> None:
    _write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)

    tool_name, payload = map_cli_to_tool("task", "pack", {"task_id": "T-006"})
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "task.pack", {"task_id": "T-006"})
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool(
        "doc",
        "snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
    )
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(
        state,
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
    )
    assert cli_result == mcp_result

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
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(
        state,
        "task.block",
        {
            "task_id": "T-006",
            "reason_code": "verification_ambiguous",
            "reason": "checklist unclear",
            "dry_run": True,
        },
    )
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool("plan", "view", {})
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "plan.view", {})
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool("plan", "pack", {"task_id": "T-006"})
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "plan.pack", {"task_id": "T-006"})
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool("plan", "intent.list", {})
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "plan.intent.list", {})
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool(
        "plan", "intent.view", {"intent_id": "I-001"}
    )
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "plan.intent.view", {"intent_id": "I-001"})
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool(
        "plan", "intent.index", {"intent_id": "I-001"}
    )
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "plan.intent.index", {"intent_id": "I-001"})
    assert cli_result == mcp_result

    tool_name, payload = map_cli_to_tool(
        "plan", "intent.validate", {"intent_id": "I-001"}
    )
    cli_result = call_tool(state, tool_name, payload)
    mcp_result = call_tool(state, "plan.intent.validate", {"intent_id": "I-001"})
    assert cli_result == mcp_result


def test_cli_mapping_supports_init_bootstrap_command() -> None:
    tool_name, payload = map_cli_to_tool("init", "", {})
    assert tool_name == "project.init"
    assert payload == {}
