from __future__ import annotations

from pathlib import Path

import yaml

from ..fixtures.repo_snippets import task_doc_t010, task_doc_t011, test_repo_config


def write_context_repo(root: Path) -> None:
    _write_doc(
        root,
        ".context/project/intents/index.md",
        "PROJ-INTENT-INDEX",
        "Intent Index",
    )
    _write_doc(
        root,
        ".context/project/architecture/index.md",
        "ARCH-INDEX",
        "Architecture",
    )
    _write_doc(
        root,
        ".context/project/architecture/schemas/glossary.md",
        "SCH-GLOSSARY",
        "Glossary",
        doc_type="schema",
    )
    _write_doc(
        root,
        ".context/governance/code-principles.md",
        "GOV-CODE-PRINCIPLES",
        "Code Principles",
        doc_type="governance",
    )
    _write_doc(
        root,
        ".context/governance/git/index.md",
        "GOV-GIT-INDEX",
        "Git",
        doc_type="governance",
    )
    _write_doc(
        root,
        ".context/governance/doc/index.md",
        "GOV-DOC-INDEX",
        "Doc",
        doc_type="governance",
    )

    _write(
        root,
        ".context/project/plan.md",
        "\n".join(
            [
                "---",
                "id: PLAN-MAIN",
                "type: plan",
                "title: Plan",
                "status: active",
                "phase: test",
                "focus: test closeout",
                "active_tasks:",
                "  - T-010",
                "blocked_tasks: []",
                "next_tasks:",
                "  - T-011",
                "milestones: []",
                "links: [ARCH-INDEX]",
                "---",
                "",
                "# Plan",
                "",
                "## Active Tasks",
                "",
                "- [T-010](./tasks/T-010-task-closeout-automation.md)",
                "",
                "## Blocked Tasks",
                "",
                "",
                "## Next Tasks",
                "",
                "- [T-011](./tasks/T-011-feature-precision.md)",
                "",
            ]
        ),
    )

    _write(
        root,
        ".context/project/tasks/T-010-task-closeout-automation.md",
        task_doc_t010(),
    )
    _write(root, ".context/project/tasks/T-011-feature-precision.md", task_doc_t011())

    config = test_repo_config()
    docs = config["docs"]
    assert isinstance(docs, dict)
    docs.update(
        {
            "intent": ".context/project/intents/index.md",
            "architecture": ".context/project/architecture/index.md",
            "plan": ".context/project/plan.md",
            "glossary": ".context/project/architecture/schemas/glossary.md",
            "principles": [".context/governance/code-principles.md"],
            "todo": [".context/project/plan.md"],
            "doc_map": ".context/governance/doc/index.md",
            "tasks_glob": ".context/project/tasks/T-*.md",
        }
    )
    modules = config["modules"]
    assert isinstance(modules, dict)
    modules["git"] = {"path": ".context/governance/git/index.md"}
    (root / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


def write_file(root: Path, rel: str, text: str) -> None:
    _write(root, rel, text)


def _write_doc(
    root: Path, rel: str, doc_id: str, title: str, *, doc_type: str = "anchor"
) -> None:
    _write(
        root,
        rel,
        "\n".join(
            [
                "---",
                f"id: {doc_id}",
                f"type: {doc_type}",
                f"title: {title}",
                "status: active",
                "links: []",
                "---",
                "",
                f"# {title}",
                "",
            ]
        ),
    )


def _write(root: Path, rel: str, text: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
