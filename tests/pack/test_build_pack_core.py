from __future__ import annotations

import pytest

from taco.core.indexing import DocumentInput, build_index
from taco.core.packing import PackError, build_task_pack

from .fixture_graph import budget, build_graph, index_config


def test_build_task_pack_constructs_for_valid_task() -> None:
    graph = build_graph()
    result = build_task_pack("T-003", graph, budget(default_tokens=200))
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
    graph = build_graph()
    with pytest.raises(PackError) as exc:
        build_task_pack("T-999", graph, budget(default_tokens=200))
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
    graph = build_index(docs, index_config())
    with pytest.raises(PackError) as exc:
        build_task_pack("T-003", graph, budget(default_tokens=200))
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
    graph = build_index(docs, index_config())
    with pytest.raises(PackError) as exc:
        build_task_pack("T-003", graph, budget(default_tokens=200))
    assert exc.value.code == "pack_not_ready"
    assert exc.value.details.get("missing_refs") == "ARCH-MISSING-001"

