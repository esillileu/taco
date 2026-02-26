from __future__ import annotations

from pathlib import Path

import yaml

from taco.core.plan import _compose_front_matter


def _write_fixture_repo(root: Path) -> None:
    (root / "docs" / "dev" / "tasks").mkdir(parents=True)
    (root / "docs" / "intents").mkdir(parents=True)
    (root / "docs" / "dev").mkdir(exist_ok=True)
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
                "active_tasks: [T-008]",
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
    (root / "docs" / "dev" / "tasks" / "T-008-cli-entrypoint.md").write_text(
        "\n".join(
            [
                "---",
                "id: T-008",
                "type: task",
                "title: T-008-cli-entrypoint",
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
                "# Task: T-008-cli-entrypoint",
                "## Intent",
                "<!-- taco:pack=task.core -->",
                "intent",
                "## Goal",
                "<!-- taco:pack=task.core -->",
                "goal",
                "## Scope",
                "<!-- taco:pack=task.core,pack.next_actions -->",
                "- run cli task list",
                "scope",
                "## Implementation Approach",
                "<!-- taco:pack=task.plans,pack.next_actions -->",
                "1. wire argparse",
                "impl",
                "## Verification Approach",
                "<!-- taco:pack=task.plans,pack.acceptance_checks,"
                "pack.verification_commands -->",
                "- verify cli json output",
                "- uv run --extra dev pytest -q",
                "verify",
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
                "task_refs: [T-008]",
                "links: [PLAN-MAIN, T-008, ARCH-INDEX]",
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


def _author_task_from_blueprint(root: Path, blueprint: dict[str, object]) -> None:
    task_path = str(blueprint.get("path", "")).strip()
    assert task_path
    fm = blueprint.get("front_matter_requirements")
    assert isinstance(fm, dict)
    body = "\n".join(
        [
            f"# Task: {fm.get('title', '')}",
            "",
            "## Intent",
            "- authored from blueprint for review gate pass.",
            "",
            "## Goal",
            "- make review and apply pass with authored task content.",
            "",
            "## Scope",
            "- keep change boundary inside task blueprint constraints.",
            "",
            "## Implementation Approach",
            "1. use blueprint front matter exactly.",
            "2. author required sections with actionable lines.",
            "",
            "## Verification Approach",
            "- run review bundle and expect pass.",
            "- run apply and expect success.",
            "",
            "## Implementation Result",
            "- pending",
            "",
            "## Verification Result",
            "- pending",
        ]
    )
    text = _compose_front_matter(fm, body)
    target = root / task_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
