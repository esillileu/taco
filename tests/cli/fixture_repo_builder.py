from __future__ import annotations

from pathlib import Path

import yaml

from ..fixtures.repo_snippets import task_doc_t008, test_repo_config


def write_fixture_repo(root: Path) -> None:
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
        task_doc_t008(),
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
    (root / "taco.yaml").write_text(
        yaml.safe_dump(test_repo_config()),
        encoding="utf-8",
    )
