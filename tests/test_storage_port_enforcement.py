from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_tool


def _write(root: Path, rel: str, lines: list[str]) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fixture_repo(root: Path) -> None:
    _write(
        root,
        "docs/intent.md",
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
        ],
    )
    _write(
        root,
        "docs/architecture.md",
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
        ],
    )
    _write(
        root,
        "docs/plan.md",
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
        ],
    )
    _write(
        root,
        "docs/glossary.md",
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
        ],
    )
    _write(
        root,
        "docs/dev/principles.md",
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
        ],
    )
    _write(root, "docs/dev/todo.md", ["# Todo"])
    _write(
        root,
        "docs/dev/tasks/T-001-parser-foundation.md",
        [
            "---",
            "id: T-001",
            "type: task",
            "title: T-001-parser-foundation",
            "status: active",
            "plan_ref: PLAN-MAIN",
            "scope:",
            "  in: []",
            "  out: []",
            "references:",
            "  modules: [ARCH-INDEX]",
            "  flows: [PLAN-MAIN]",
            "  schemas: [SCH-GLOSSARY]",
            "  governance: [GOV-CODE-PRINCIPLES]",
            "links: [PLAN-MAIN]",
            "---",
            "",
            "# Task: T-001-parser-foundation",
            "## Intent",
            "- intent",
            "## Goal",
            "- goal",
            "## Scope",
            "- scope",
            "## Implementation Approach",
            "- plan",
            "## Verification Approach",
            "- verify",
            "## Implementation Result",
            "- pending",
            "## Verification Result",
            "- pending",
        ],
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
            "priority_order": ["task.core", "task.plans"],
            "required_groups": ["task.core", "task.plans"],
        },
    }
    (root / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


def test_task_record_requires_storage_port(tmp_path: Path) -> None:
    _fixture_repo(tmp_path)
    state = load_repo_state(tmp_path)
    no_storage = replace(state, storage=None)

    result = call_tool(
        no_storage,
        "task.record",
        {
            "task_id": "T-001",
            "route_type": "implementation",
            "content": "applied",
            "dry_run": False,
        },
    )
    assert result["ok"] is False
    assert result["error"]["code"] == "storage_unavailable"
