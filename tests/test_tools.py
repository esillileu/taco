from __future__ import annotations

from pathlib import Path

import yaml

from taco.indexer import DocumentInput, IndexConfig, build_index
from taco.pack import BudgetConfig
from taco.router import RouterConfig
from taco.tools import RepoState, call_tool, load_repo_state


def _state(tmp_path: Path) -> RepoState:
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text(
            "docs/architecture.md",
            "\n".join(["# Architecture", "## System", "system detail"]),
        ),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text(
            "docs/glossary.md",
            "\n".join(["# Glossary", "## Term", "term detail"]),
        ),
        DocumentInput.from_text(
            "docs/dev/principles.md",
            "\n".join(["# Principles", "## Rules", "rules detail"]),
        ),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
        DocumentInput.from_text(
            "docs/dev/tasks/T-005-mcp-tools.md",
            "\n".join(
                [
                    "# Task: T-005-mcp-tools",
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
        ),
    ]

    index_cfg = IndexConfig(
        intent_path="docs/intent.md",
        architecture_path="docs/architecture.md",
        plan_path="docs/plan.md",
        glossary_path="docs/glossary.md",
        principles_paths=("docs/dev/principles.md",),
        todo_paths=("docs/dev/todo.md",),
        tasks_glob="docs/dev/tasks/T-*.md",
        git_module_path="docs/dev/git.md",
    )
    index = build_index(docs, index_cfg)
    return RepoState(
        root=tmp_path,
        config_raw={"modules": {"git": {"path": "docs/dev/git.md"}}},
        index=index,
        budget_config=BudgetConfig(
            default_tokens=200,
            priority_order=(
                "task.core",
                "task.plans",
                "arch.snippets",
                "principles.snippets",
                "glossary.terms",
            ),
        ),
        router_config=RouterConfig.default(),
    )


def test_call_tool_unknown_returns_error(tmp_path: Path) -> None:
    state = _state(tmp_path)
    response = call_tool(state, "unknown.tool", {})
    assert response["ok"] is False
    assert response["error"]["code"] == "unknown_tool"


def test_task_list_and_pack_and_targets(tmp_path: Path) -> None:
    state = _state(tmp_path)
    listed = call_tool(state, "task.list", {})
    assert listed["ok"] is True
    assert listed["data"]["tasks"][0]["task_id"] == "T-005"

    packed = call_tool(state, "task.pack", {"task_id": "T-005"})
    assert packed["ok"] is True
    assert packed["data"]["task_id"] == "T-005"

    target = call_tool(
        state,
        "task.targets",
        {"task_id": "T-005", "route_type": "implementation_result"},
    )
    assert target["ok"] is True
    assert target["data"]["heading"] == "Implementation Result"


def test_doc_snippet_issue_triage_and_convention(tmp_path: Path) -> None:
    state = _state(tmp_path)
    snippet = call_tool(
        state,
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
    )
    assert snippet["ok"] is True
    assert "System" in snippet["data"]["snippet"]

    triage = call_tool(state, "issue.triage", {"title": "fix broken parser"})
    assert triage["ok"] is True
    assert triage["data"]["type"] == "Fix"

    convention = call_tool(state, "convention.get", {"topic": "git"})
    assert convention["ok"] is True
    assert convention["data"]["path"] == "docs/dev/git.md"


def test_task_record_dry_run_preview(tmp_path: Path) -> None:
    state = _state(tmp_path)
    result = call_tool(
        state,
        "task.record",
        {
            "task_id": "T-005",
            "route_type": "verification_result",
            "content": "validated behavior",
            "dry_run": True,
        },
    )
    assert result["ok"] is True
    assert result["data"]["applied"] is False
    assert result["data"]["preview"] == "- validated behavior"


def test_load_repo_state_from_config(tmp_path: Path) -> None:
    (tmp_path / "docs" / "dev" / "tasks").mkdir(parents=True)
    (tmp_path / "docs" / "dev").mkdir(exist_ok=True)
    (tmp_path / "docs" / "intent.md").write_text("# Intent\n", encoding="utf-8")
    (tmp_path / "docs" / "architecture.md").write_text(
        "# Architecture\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (tmp_path / "docs" / "glossary.md").write_text("# Glossary\n", encoding="utf-8")
    (tmp_path / "docs" / "dev" / "principles.md").write_text(
        "# Principles\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (tmp_path / "docs" / "dev" / "tasks" / "T-001-sample.md").write_text(
        "# Task: T-001-sample\n", encoding="utf-8"
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
            "default_tokens": 50,
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
    (tmp_path / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    state = load_repo_state(tmp_path)
    assert state.budget_config.default_tokens == 50
