from __future__ import annotations

from pathlib import Path

import yaml

from taco.tools import call_tool, load_repo_state


def _write(root: Path, rel: str, text: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _write_context_repo(root: Path) -> None:
    _write(
        root,
        ".context/project/overview.md",
        "\n".join(
            [
                "---",
                "id: PROJ-OVERVIEW",
                "type: anchor",
                "title: Overview",
                "status: active",
                "links: []",
                "---",
                "",
                "# Overview",
                "",
            ]
        ),
    )
    _write(
        root,
        ".context/project/architecture/index.md",
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
                "# Architecture Index",
                "",
            ]
        ),
    )
    _write(
        root,
        ".context/project/architecture/schemas/glossary.md",
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
    )
    _write(
        root,
        ".context/governance/code-principles.md",
        "\n".join(
            [
                "---",
                "id: GOV-CODE-PRINCIPLES",
                "type: governance",
                "title: Code Principles",
                "status: active",
                "links: []",
                "---",
                "",
                "# Code Principles",
                "",
            ]
        ),
    )
    _write(
        root,
        ".context/governance/git/index.md",
        "\n".join(
            [
                "---",
                "id: GOV-GIT-INDEX",
                "type: governance",
                "title: Git",
                "status: active",
                "links: []",
                "---",
                "",
                "# Git",
                "",
            ]
        ),
    )
    _write(
        root,
        ".context/governance/doc/index.md",
        "\n".join(
            [
                "---",
                "id: GOV-DOC-INDEX",
                "type: governance",
                "title: Doc",
                "status: active",
                "links: []",
                "---",
                "",
                "# Doc",
                "",
            ]
        ),
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
            ]
        ),
    )

    _write(
        root,
        ".context/project/tasks/T-010-task-closeout-automation.md",
        "\n".join(
            [
                "---",
                "id: T-010",
                "type: task",
                "title: T-010-task-closeout-automation",
                "status: active",
                "plan_ref: PLAN-MAIN",
                "priority: p0",
                "estimate: m",
                "scope:",
                "  in: []",
                "  out: []",
                "references:",
                "  modules: []",
                "  flows: []",
                "  schemas: []",
                "  governance: []",
                "deliverables: []",
                "verification: []",
                "links: [PLAN-MAIN]",
                "---",
                "",
                "# Task: T-010-task-closeout-automation",
                "## Intent",
                "- intent",
                "## Goal",
                "- goal",
                "## Scope",
                "- scope",
                "## Implementation Approach",
                "- impl plan",
                "## Verification Approach",
                "- verify plan",
                "## Implementation Result",
                "- Pending",
                "## Verification Result",
                "- Pending",
                "",
            ]
        ),
    )

    _write(
        root,
        ".context/project/tasks/T-011-feature-precision.md",
        "\n".join(
            [
                "---",
                "id: T-011",
                "type: task",
                "title: T-011-feature-precision",
                "status: todo",
                "plan_ref: PLAN-MAIN",
                "priority: p1",
                "estimate: m",
                "scope:",
                "  in: []",
                "  out: []",
                "references:",
                "  modules: []",
                "  flows: []",
                "  schemas: []",
                "  governance: []",
                "deliverables: []",
                "verification: []",
                "links: [PLAN-MAIN]",
                "---",
                "",
                "# Task: T-011-feature-precision",
                "## Intent",
                "- intent",
                "## Goal",
                "- goal",
                "## Scope",
                "- scope",
                "## Implementation Approach",
                "- impl plan",
                "## Verification Approach",
                "- verify plan",
                "## Implementation Result",
                "- Pending",
                "## Verification Result",
                "- Pending",
                "",
            ]
        ),
    )

    config = {
        "docs": {
            "intent": ".context/project/overview.md",
            "architecture": ".context/project/architecture/index.md",
            "plan": ".context/project/plan.md",
            "glossary": ".context/project/architecture/schemas/glossary.md",
            "principles": [".context/governance/code-principles.md"],
            "todo": [".context/project/plan.md"],
            "doc_map": ".context/governance/doc/index.md",
            "tasks_glob": ".context/project/tasks/T-*.md",
        },
        "budget": {
            "default_tokens": 200,
            "priority_order": [
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ],
            "required_groups": [
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ],
        },
        "pack": {"common_required_refs": ["ARCH-INDEX", "PLAN-MAIN"]},
        "modules": {"git": {"path": ".context/governance/git/index.md"}},
    }
    (root / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


def test_task_complete_dry_run_preview_and_apply(tmp_path: Path) -> None:
    _write_context_repo(tmp_path)
    state = load_repo_state(tmp_path)

    dry = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "implemented closeout flow",
            "verification": "all checks passed",
            "dry_run": True,
        },
    )
    assert dry["ok"] is True
    assert dry["data"]["applied"] is False
    assert dry["data"]["status_to"] == "done"
    assert dry["data"]["next_active_task"] == "T-011"

    apply = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "implemented closeout flow",
            "verification": "all checks passed",
            "dry_run": False,
        },
    )
    assert apply["ok"] is True
    assert apply["data"]["applied"] is True
    assert apply["data"]["next_active_task"] == "T-011"

    task_path = ".context/project/tasks/T-010-task-closeout-automation.md"
    task_text = (tmp_path / task_path).read_text(encoding="utf-8")
    assert "status: done" in task_text
    assert "- implemented closeout flow" in task_text
    assert "- all checks passed" in task_text

    plan_text = (tmp_path / ".context/project/plan.md").read_text(encoding="utf-8")
    assert "active_tasks:" in plan_text
    assert "- T-011" in plan_text
    assert "- T-010" not in plan_text.split("next_tasks:", 1)[1]


def test_task_complete_rejects_already_done_task(tmp_path: Path) -> None:
    _write_context_repo(tmp_path)
    state = load_repo_state(tmp_path)

    first = call_tool(
        state,
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "done",
            "verification": "done",
            "dry_run": False,
        },
    )
    assert first["ok"] is True

    second = call_tool(
        load_repo_state(tmp_path),
        "task.complete",
        {
            "task_id": "T-010",
            "implementation": "again",
            "verification": "again",
            "dry_run": False,
        },
    )
    assert second["ok"] is False
    assert second["error"]["code"] == "task_already_done"
