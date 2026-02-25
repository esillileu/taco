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
            "arch.snippets",
            "principles.snippets",
            "glossary.terms",
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
                    "intent detail",
                    "## Goal",
                    "goal detail",
                    "## Scope",
                    "scope detail",
                    "## Implementation Approach",
                    "impl detail",
                    "## Verification Approach",
                    "verify detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/architecture.md",
            "\n".join(
                [
                    "# Architecture",
                    "## System",
                    "arch system detail",
                    "## Pipeline",
                    "arch pipeline detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/dev/principles.md",
            "\n".join(
                [
                    "# Principles",
                    "## Rules",
                    "principles detail",
                    "## Design",
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
                    "term detail",
                ]
            ),
        ),
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
    ]
    return build_index(docs, _index_config())


def test_build_task_pack_constructs_for_valid_task() -> None:
    graph = _build_graph()
    result = build_task_pack("T-003", graph, _budget(default_tokens=200))
    assert result.task_id == "T-003"
    assert result.used_tokens <= result.budget_tokens
    groups = [item.group for item in result.snippets]
    assert "task.core" in groups
    assert "task.plans" in groups


def test_build_task_pack_raises_for_missing_task_id() -> None:
    graph = _build_graph()
    with pytest.raises(PackError) as exc:
        build_task_pack("T-999", graph, _budget(default_tokens=200))
    assert exc.value.code == "task_not_found"


def test_build_task_pack_respects_budget_boundaries() -> None:
    graph = _build_graph()
    high_budget = build_task_pack("T-003", graph, _budget(default_tokens=200))
    low_budget = build_task_pack("T-003", graph, _budget(default_tokens=5))
    equal_budget = build_task_pack(
        "T-003", graph, _budget(default_tokens=low_budget.used_tokens)
    )

    assert len(low_budget.dropped) > 0
    assert low_budget.used_tokens <= 5
    assert equal_budget.used_tokens == low_budget.used_tokens
    assert len(high_budget.snippets) >= len(equal_budget.snippets)


def test_build_task_pack_order_is_stable() -> None:
    graph = _build_graph()
    first = build_task_pack("T-003", graph, _budget(default_tokens=200)).to_dict()
    second = build_task_pack("T-003", graph, _budget(default_tokens=200)).to_dict()
    assert first == second


def test_build_task_pack_matches_golden_shape() -> None:
    graph = _build_graph()
    result = build_task_pack("T-003", graph, _budget(default_tokens=20)).to_dict()
    assert set(result.keys()) == {
        "task_id",
        "budget_tokens",
        "used_tokens",
        "snippets",
        "dropped",
    }
    assert result["task_id"] == "T-003"
    assert isinstance(result["snippets"], list)
    assert isinstance(result["dropped"], list)
