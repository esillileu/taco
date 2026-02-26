from __future__ import annotations

from pathlib import Path

import yaml


def write_fixture_repo(root: Path) -> None:
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
