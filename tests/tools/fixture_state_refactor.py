from __future__ import annotations

from pathlib import Path

import yaml

from taco.apps.composition import RepoState
from taco.apps.composition import build_repo_state as load_repo_state


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
