from __future__ import annotations

import pytest

from taco.core.indexing import DocumentInput, IndexConfig, build_index
from taco.core.routing import RouterConfig, RouterError, resolve_write_target


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


def _build_graph(task_text: str):
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/architecture.md", "# Architecture\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
        DocumentInput.from_text(
            "docs/dev/tasks/T-004-write-target-router.md", task_text
        ),
    ]
    return build_index(docs, _index_config())


def test_resolve_write_target_for_implementation_result() -> None:
    graph = _build_graph(
        "\n".join(
            [
                "# Task: T-004-write-target-router",
                "## Implementation Result",
                "Pending",
                "## Verification Result",
                "Pending",
            ]
        )
    )
    target = resolve_write_target("T-004", "implementation_result", graph)
    assert target.path == "docs/dev/tasks/T-004-write-target-router.md"
    assert target.heading == "Implementation Result"
    assert target.mode == "append_implementation"


def test_resolve_write_target_for_verification_result() -> None:
    graph = _build_graph(
        "\n".join(
            [
                "# Task: T-004-write-target-router",
                "## Implementation Result",
                "Pending",
                "## Verification Result",
                "Pending",
            ]
        )
    )
    target = resolve_write_target("T-004", "verification_result", graph)
    assert target.heading == "Verification Result"
    assert target.mode == "append_verification"


def test_resolve_write_target_accepts_short_aliases() -> None:
    graph = _build_graph(
        "\n".join(
            [
                "# Task: T-004-write-target-router",
                "## Implementation Result",
                "Pending",
                "## Verification Result",
                "Pending",
            ]
        )
    )
    implementation = resolve_write_target("T-004", "implementation", graph)
    verification = resolve_write_target("T-004", "verification", graph)
    assert implementation.heading == "Implementation Result"
    assert verification.heading == "Verification Result"
    assert implementation.mode == "append_implementation"
    assert verification.mode == "append_verification"


def test_resolve_write_target_missing_heading() -> None:
    graph = _build_graph(
        "\n".join(
            [
                "# Task: T-004-write-target-router",
                "## Implementation Result",
                "Pending",
            ]
        )
    )
    with pytest.raises(RouterError) as exc:
        resolve_write_target("T-004", "verification_result", graph)
    assert exc.value.code == "target_heading_not_found"


def test_resolve_write_target_ambiguous_heading() -> None:
    graph = _build_graph(
        "\n".join(
            [
                "# Task: T-004-write-target-router",
                "## Verification Result",
                "one",
                "## Verification Result",
                "two",
            ]
        )
    )
    with pytest.raises(RouterError) as exc:
        resolve_write_target("T-004", "verification_result", graph)
    assert exc.value.code == "ambiguous_target_heading"


def test_resolve_write_target_issue_route_and_contract_shape() -> None:
    graph = _build_graph(
        "\n".join(
            [
                "# Task: T-004-write-target-router",
                "## Verification Result",
                "Pending",
            ]
        )
    )
    target = resolve_write_target(
        "T-004", "issue_record", graph, RouterConfig.default()
    )
    payload = target.to_dict()
    assert payload["mode"] == "append_issue"
    assert set(payload.keys()) == {"path", "heading", "line_hint", "mode"}
