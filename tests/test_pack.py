from __future__ import annotations

import pytest

from taco.indexer import DocumentInput, IndexConfig, build_index
from taco.pack import BudgetConfig, PackError, build_task_pack


def _index_config() -> IndexConfig:
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


def _budget(default_tokens: int) -> BudgetConfig:
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


def _build_graph():
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
    return build_index(docs, _index_config())


def test_build_task_pack_constructs_for_valid_task() -> None:
    graph = _build_graph()
    result = build_task_pack("T-003", graph, _budget(default_tokens=200))
    assert result.task_id == "T-003"
    groups = [item.group for item in result.context_snippets]
    assert "task.core" in groups
    assert "task.plans" in groups
    assert any(item.path == "docs/architecture.md" for item in result.context_snippets)
    assert any(item.path == "docs/plan.md" for item in result.context_snippets)
    assert any(
        item.path == "docs/dev/principles.md" for item in result.context_snippets
    )
    assert len(result.next_actions) > 0
    assert len(result.acceptance_checks) > 0
    assert len(result.verification_commands) > 0


def test_build_task_pack_raises_for_missing_task_id() -> None:
    graph = _build_graph()
    with pytest.raises(PackError) as exc:
        build_task_pack("T-999", graph, _budget(default_tokens=200))
    assert exc.value.code == "task_not_found"


def test_build_task_pack_fails_when_required_groups_missing() -> None:
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/architecture.md", "# Architecture\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
        DocumentInput.from_text("docs/dev/principles.md", "# Principles\n"),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
        DocumentInput.from_text(
            "docs/dev/tasks/T-003-pack-budget.md",
            "\n".join(["# Task: T-003-pack-budget", "## Intent", "no selectors"]),
        ),
    ]
    graph = build_index(docs, _index_config())
    with pytest.raises(PackError) as exc:
        build_task_pack("T-003", graph, _budget(default_tokens=200))
    assert exc.value.code == "pack_not_ready"


def test_build_task_pack_uses_task_heading_fallback_without_selectors() -> None:
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/architecture.md", "# Architecture\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
        DocumentInput.from_text("docs/dev/principles.md", "# Principles\n"),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
        DocumentInput.from_text(
            "docs/dev/tasks/T-003-pack-budget.md",
            "\n".join(
                [
                    "# Task: T-003-pack-budget",
                    "## Intent",
                    "intent detail",
                    "## Goal",
                    "goal detail",
                    "## Scope",
                    "- run parser",
                    "## Context Requirements",
                    "- required: ARCH-MISSING-001",
                    "## Implementation Approach",
                    "1. implement candidate assembly",
                    "## Verification Approach",
                    "- verify deterministic output",
                    "- uv run --extra dev pytest -q",
                    "## Implementation Result",
                    "Pending",
                    "## Verification Result",
                    "Pending",
                ]
            ),
        ),
    ]
    graph = build_index(docs, _index_config())
    with pytest.raises(PackError) as exc:
        build_task_pack("T-003", graph, _budget(default_tokens=200))
    assert exc.value.code == "pack_not_ready"
    assert exc.value.details.get("missing_refs") == "ARCH-MISSING-001"


def test_build_task_pack_resolves_context_requirement_refs() -> None:
    graph = _build_graph()
    result = build_task_pack("T-003", graph, _budget(default_tokens=200))
    ref_reasons = [
        item.reason
        for item in result.context_snippets
        if item.reason == "context_requirement"
    ]
    assert len(ref_reasons) >= 3


def test_build_task_pack_respects_budget_boundaries() -> None:
    graph = _build_graph()
    high_budget = build_task_pack("T-003", graph, _budget(default_tokens=200))
    low_budget = build_task_pack("T-003", graph, _budget(default_tokens=5))
    equal_budget = build_task_pack(
        "T-003", graph, _budget(default_tokens=low_budget.used_tokens)
    )

    assert len(low_budget.dropped) > 0
    assert low_budget.used_tokens >= 5
    assert equal_budget.used_tokens >= low_budget.used_tokens
    assert len(high_budget.context_snippets) >= len(equal_budget.context_snippets)


def test_build_task_pack_order_is_stable() -> None:
    graph = _build_graph()
    first = build_task_pack("T-003", graph, _budget(default_tokens=200)).to_dict()
    second = build_task_pack("T-003", graph, _budget(default_tokens=200)).to_dict()
    assert first == second


def test_build_task_pack_matches_golden_shape() -> None:
    graph = _build_graph()
    result = build_task_pack("T-003", graph, _budget(default_tokens=20)).to_dict()
    assert set(result.keys()) == {
        "pack_version",
        "task_id",
        "budget_tokens",
        "used_tokens",
        "next_actions",
        "acceptance_checks",
        "verification_commands",
        "write_targets",
        "context_snippets",
        "unknowns",
        "coverage",
        "dropped",
    }
    assert result["task_id"] == "T-003"
    assert isinstance(result["context_snippets"], list)
    assert isinstance(result["dropped"], list)
