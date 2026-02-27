from __future__ import annotations

import pytest

from taco.core.indexing import DocumentInput, IndexerError, build_index

from .fixture_index import base_config


def test_build_index_classifies_docs_and_tasks() -> None:
    config = base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/architecture.md", "# Architecture\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
        DocumentInput.from_text(
            "docs/dev/tasks/T-001-parser-foundation.md", "# T-001\n"
        ),
        DocumentInput.from_text("docs/dev/todo.md", "# Todo\n"),
    ]

    graph = build_index(docs, config)
    task_doc = next(
        doc
        for doc in graph.documents
        if doc.path == "docs/dev/tasks/T-001-parser-foundation.md"
    )
    assert task_doc.doc_type == "task"
    assert task_doc.task_id == "T-001"
    assert graph.task_index["T-001"] == "docs/dev/tasks/T-001-parser-foundation.md"


def test_build_index_extracts_local_links() -> None:
    config = base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/architecture.md", "# Architecture\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
        DocumentInput.from_text(
            "docs/dev/todo.md", "[Task](./tasks/T-001-parser-foundation.md)\n"
        ),
    ]

    graph = build_index(docs, config)
    assert graph.link_graph["docs/dev/todo.md"] == (
        "./tasks/T-001-parser-foundation.md",
    )


def test_build_index_rejects_missing_required_docs() -> None:
    config = base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
    ]

    with pytest.raises(IndexerError) as exc:
        build_index(docs, config)

    assert exc.value.code == "missing_required_docs"


def test_build_index_collects_reference_lookup() -> None:
    config = base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text(
            "docs/architecture.md",
            "\n".join(
                [
                    "# Architecture",
                    "## Boundary",
                    "<!-- taco:ref=ARCH-BOUNDARY-001 -->",
                    "detail",
                ]
            ),
        ),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
    ]
    graph = build_index(docs, config)
    assert (
        graph.reference_lookup["ARCH-BOUNDARY-001"]
        == "docs/architecture.md#boundary"
    )


def test_build_index_rejects_duplicate_reference_ids() -> None:
    config = base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text(
            "docs/architecture.md",
            "\n".join(
                [
                    "# Architecture",
                    "## Boundary",
                    "<!-- taco:ref=REF-DUP-001 -->",
                    "detail",
                ]
            ),
        ),
        DocumentInput.from_text(
            "docs/plan.md",
            "\n".join(
                [
                    "# Plan",
                    "## Phase",
                    "<!-- taco:ref=REF-DUP-001 -->",
                    "detail",
                ]
            ),
        ),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
    ]
    with pytest.raises(IndexerError) as exc:
        build_index(docs, config)
    assert exc.value.code == "duplicate_reference_id"
