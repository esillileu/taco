from __future__ import annotations

from pathlib import Path

import yaml

from taco.cli import map_cli_to_tool
from taco.tools import call_tool, load_repo_state


def _write_fixture_repo(root: Path) -> None:
    (root / "docs" / "dev" / "tasks").mkdir(parents=True)
    (root / "docs" / "dev" / "git").mkdir(parents=True)

    (root / "docs" / "intent.md").write_text("# Intent\n", encoding="utf-8")
    (root / "docs" / "architecture.md").write_text(
        "\n".join(["# Architecture", "## System", "system detail"]),
        encoding="utf-8",
    )
    (root / "docs" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (root / "docs" / "glossary.md").write_text(
        "\n".join(["# Glossary", "## Terms", "term detail"]),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "principles.md").write_text(
        "\n".join(["# Principles", "## Rules", "rules detail"]),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (root / "docs" / "dev" / "git.md").write_text("# Git Rules\n", encoding="utf-8")
    (root / "docs" / "dev" / "tasks" / "T-006-integration-tests.md").write_text(
        "\n".join(
            [
                "# Task: T-006-integration-tests",
                "## Intent",
                "intent detail",
                "## Goal",
                "goal detail",
                "## Scope",
                "scope detail",
                "## Implementation Approach",
                "impl detail",
                "## Verification Approach",
                "verify detail",
                "## Implementation Result",
                "Pending",
                "## Verification Result",
                "Pending",
            ]
        ),
        encoding="utf-8",
    )

    config = {
        "docs": {
            "intent": "docs/intent.md",
            "architecture": "docs/architecture.md",
            "plan": "docs/plan.md",
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
        },
        "modules": {"git": {"path": "docs/dev/git.md"}},
    }
    (root / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


def test_integration_happy_path_for_all_tools(tmp_path: Path) -> None:
    _write_fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)

    assert call_tool(state, "task.list", {})["ok"] is True
    assert call_tool(state, "task.pack", {"task_id": "T-006"})["ok"] is True
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
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
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
