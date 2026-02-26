from __future__ import annotations

from pathlib import Path

import yaml

from taco.indexer import DocumentInput, IndexConfig, build_index
from taco.pack import BudgetConfig
from taco.router import RouterConfig
from taco.tools import RepoState, call_bootstrap_tool, call_tool, load_repo_state


def _state(tmp_path: Path) -> RepoState:
    docs = [
        DocumentInput.from_text(
            "docs/intent.md",
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
        ),
        DocumentInput.from_text(
            "docs/architecture.md",
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
        ),
        DocumentInput.from_text(
            "docs/plan.md",
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
        ),
        DocumentInput.from_text(
            "docs/glossary.md",
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
                    "## Term",
                    "<!-- taco:pack=glossary.terms -->",
                    "term detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/dev/principles.md",
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
        ),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
        DocumentInput.from_text(
            "docs/dev/tasks/T-005-mcp-tools.md",
            "\n".join(
                [
                    "---",
                    "id: T-005",
                    "type: task",
                    "title: T-005-mcp-tools",
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
                    "# Task: T-005-mcp-tools",
                    "## Intent",
                    "<!-- taco:pack=task.core -->",
                    "intent detail",
                    "## Goal",
                    "<!-- taco:pack=task.core -->",
                    "goal detail",
                    "## Scope",
                    "<!-- taco:pack=task.core,pack.next_actions -->",
                    "- prepare tool map",
                    "scope detail",
                    "## Implementation Approach",
                    "<!-- taco:pack=task.plans,pack.next_actions -->",
                    "1. implement dispatcher",
                    "impl detail",
                    "## Verification Approach",
                    "<!-- taco:pack=task.plans,pack.acceptance_checks,"
                    "pack.verification_commands -->",
                    "- assert tool envelope",
                    "- uv run --extra dev pytest -q",
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
        config_raw={
            "docs": {"plan": "docs/plan.md"},
            "modules": {"git": {"path": "docs/dev/git.md"}},
        },
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
            required_groups=(
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ),
        ),
        router_config=RouterConfig.default(),
        common_required_refs=(),
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

    plan_view = call_tool(state, "plan.view", {})
    assert plan_view["ok"] is True
    assert "plan" in plan_view["data"]

    plan_locate = call_tool(
        state,
        "plan.locate",
        {"change_type": "task", "target": "T-005"},
    )
    assert plan_locate["ok"] is True
    assert plan_locate["data"]["count"] >= 1

    plan_validate = call_tool(state, "plan.validate", {})
    assert plan_validate["ok"] is True
    assert "valid" in plan_validate["data"]


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


def test_task_pack_fails_when_readiness_requirements_missing(tmp_path: Path) -> None:
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
    (tmp_path / "docs" / "dev" / "tasks" / "T-099-not-ready.md").write_text(
        "\n".join(
            [
                "---",
                "id: T-099",
                "type: task",
                "title: T-099-not-ready",
                "status: todo",
                "plan_ref: PLAN-MAIN",
                "scope:",
                "  in: []",
                "references:",
                "  modules: []",
                "  flows: []",
                "  schemas: []",
                "---",
                "",
                "# Task: T-099-not-ready",
                "## Intent",
                "intent",
                "## Goal",
                "goal",
                "## Scope",
                "scope",
                "## Implementation Approach",
                "plan",
                "## Verification Approach",
                "Pending definition.",
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
            "default_tokens": 50,
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
    (tmp_path / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    state = load_repo_state(tmp_path)
    packed = call_tool(state, "task.pack", {"task_id": "T-099"})
    assert packed["ok"] is False
    assert packed["error"]["code"] == "task_not_ready"
    missing = packed["error"]["details"]["missing_requirements"]
    assert "scope.out" in missing
    assert "references.modules" in missing
    assert "verification.criteria" in missing


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
    (tmp_path / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    state = load_repo_state(tmp_path)
    assert state.budget_config.default_tokens == 50


def test_project_init_bootstrap_generates_minimal_context(tmp_path: Path) -> None:
    response = call_bootstrap_tool(tmp_path, "project.init", {})
    assert response["ok"] is True
    data = response["data"]
    assert data["policy"] == "fail_on_existing"
    assert ".context/project/overview.md" in data["created_files"]
    assert ".context/project/plan.md" in data["created_files"]
    assert ".context/project/architecture/index.md" in data["created_files"]
    assert ".context/governance/code-principles.md" in data["created_files"]
    assert ".context/governance/git/index.md" in data["created_files"]
    assert ".context/governance/doc/index.md" in data["created_files"]
    assert (tmp_path / "taco.yaml").exists()

    state = load_repo_state(tmp_path)
    validated = call_tool(state, "plan.validate", {})
    assert validated["ok"] is True
    assert validated["data"]["valid"] is True

    second = call_bootstrap_tool(tmp_path, "project.init", {})
    assert second["ok"] is False
    assert second["error"]["code"] == "init_target_exists"
