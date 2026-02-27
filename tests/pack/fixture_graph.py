from __future__ import annotations

from taco.core.indexing import DocumentInput, IndexConfig, build_index
from taco.core.packing import BudgetConfig


def index_config() -> IndexConfig:
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


def budget(default_tokens: int) -> BudgetConfig:
    return BudgetConfig(
        default_tokens=default_tokens,
        priority_order=(
            "task.core",
            "task.plans",
            "plan.snippets",
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
    )


def build_graph():
    docs = [
        DocumentInput.from_text(
            "docs/dev/tasks/T-003-pack-budget.md",
            "\n".join(
                [
                    "# Task: T-003-pack-budget",
                    "## Intent",
                    "<!-- taco:pack=task.core -->",
                    "intent detail",
                    "## Goal",
                    "<!-- taco:pack=task.core -->",
                    "goal detail",
                    "## Scope",
                    "<!-- taco:pack=task.core,pack.next_actions -->",
                    "- run parser",
                    "- build index",
                    "scope detail",
                    "## Context Requirements",
                    "- required: ARCH-SYSTEM-001, PLAN-PHASE-001, PRINCIPLES-RULES-001",
                    "- optional: GLOSSARY-TERM-001",
                    "## Implementation Approach",
                    "<!-- taco:pack=task.plans,pack.next_actions -->",
                    "1. implement candidate assembly",
                    "impl detail",
                    "## Verification Approach",
                    "<!-- taco:pack=task.plans,pack.acceptance_checks,"
                    "pack.verification_commands -->",
                    "- verify deterministic output",
                    "- uv run --extra dev pytest -q",
                    "verify detail",
                    "## Implementation Result",
                    "Pending",
                    "## Verification Result",
                    "Pending",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/architecture.md",
            "\n".join(
                [
                    "# Architecture",
                    "## System",
                    "<!-- taco:ref=ARCH-SYSTEM-001 -->",
                    "<!-- taco:pack=arch.snippets -->",
                    "arch system detail",
                    "## Pipeline",
                    "<!-- taco:pack=arch.snippets -->",
                    "arch pipeline detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/plan.md",
            "\n".join(
                [
                    "# Plan",
                    "## Phase 1",
                    "<!-- taco:ref=PLAN-PHASE-001 -->",
                    "<!-- taco:pack=plan.snippets -->",
                    "plan phase detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/dev/principles.md",
            "\n".join(
                [
                    "# Principles",
                    "## Rules",
                    "<!-- taco:ref=PRINCIPLES-RULES-001 -->",
                    "<!-- taco:pack=principles.snippets -->",
                    "principles detail",
                    "## Design",
                    "<!-- taco:pack=principles.snippets -->",
                    "design detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/glossary.md",
            "\n".join(
                [
                    "# Glossary",
                    "## Term",
                    "<!-- taco:ref=GLOSSARY-TERM-001 -->",
                    "<!-- taco:pack=glossary.terms -->",
                    "term detail",
                ]
            ),
        ),
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
    ]
    return build_index(docs, index_config())

