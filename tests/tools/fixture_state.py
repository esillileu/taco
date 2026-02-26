from __future__ import annotations

from pathlib import Path

import yaml

from taco.apps.composition import RepoState
from taco.apps.composition import build_repo_state as load_repo_state
from taco.core.indexing import DocumentInput, IndexConfig, build_index
from taco.core.packing import BudgetConfig
from taco.core.routing import RouterConfig


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
            "docs/intents/I-001-plan-mode.md",
            "\n".join(
                [
                    "---",
                    "id: I-001",
                    "type: intent",
                    "title: plan mode intent",
                    "status: active",
                    "plan_ref: PLAN-MAIN",
                    "task_refs: [T-005]",
                    "links: [PLAN-MAIN, T-005, ARCH-INDEX]",
                    "---",
                    "",
                    "# Intent: I-001-plan-mode",
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
        DocumentInput.from_text(
            "docs/dev/doc-index.md",
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
            "docs": {"plan": "docs/plan.md", "doc_map": "docs/dev/doc-index.md"},
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
        required_refs_by_tool={
            "plan.pack": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
            "plan.intent.index": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
            "task.pack": ("GOV-CODE-PRINCIPLES",),
        },
    )


def _state_with_refactor_intent(tmp_path: Path) -> RepoState:
    (tmp_path / "docs" / "dev" / "tasks").mkdir(parents=True)
    (tmp_path / "docs" / "dev").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "intents").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)

    oversized = "\n".join(["x = 1"] * 260) + "\n"
    (tmp_path / "src" / "oversized.py").write_text(oversized, encoding="utf-8")
    (tmp_path / "docs" / "intent.md").write_text(
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
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "architecture.md").write_text(
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
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "plan.md").write_text(
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
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "glossary.md").write_text(
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
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "dev" / "principles.md").write_text(
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
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "dev" / "doc-index.md").write_text(
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
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (tmp_path / "docs" / "dev" / "git.md").write_text("# Git\n", encoding="utf-8")
    (tmp_path / "docs" / "intents" / "I-020-refactor.md").write_text(
        "\n".join(
            [
                "---",
                "id: I-020",
                "type: intent",
                "title: file-size-and-srp-refactor",
                "status: active",
                "kind: refactor",
                "design_impact: tentative",
                "plan_ref: PLAN-MAIN",
                "task_refs: []",
                "links: [PLAN-MAIN, ARCH-INDEX]",
                "---",
                "",
                "# Intent: I-020-refactor",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "taco.yaml").write_text(
        yaml.safe_dump(
            {
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
                    "priority_order": ["task.core", "task.plans"],
                    "required_groups": ["task.core", "task.plans"],
                },
                "pack": {
                    "required_refs_by_tool": {
                        "plan_intent_index": [
                            "ARCH-INDEX",
                            "PLAN-MAIN",
                            "GOV-DOC-INDEX",
                        ]
                    }
                },
                "modules": {"git": {"path": "docs/dev/git.md"}},
            }
        ),
        encoding="utf-8",
    )
    return load_repo_state(tmp_path)
