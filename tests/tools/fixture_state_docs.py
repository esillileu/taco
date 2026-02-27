from __future__ import annotations

from taco.core.indexing import DocumentInput, IndexConfig


def build_state_documents() -> list[DocumentInput]:
    return [
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


def state_index_config() -> IndexConfig:
    return IndexConfig(
        intent_path="docs/intent.md",
        architecture_path="docs/architecture.md",
        plan_path="docs/plan.md",
        glossary_path="docs/glossary.md",
        principles_paths=("docs/dev/principles.md",),
        todo_paths=("docs/dev/todo.md",),
        tasks_glob="docs/dev/tasks/T-*.md",
        git_module_path="docs/dev/git.md",
    )
