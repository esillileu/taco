from __future__ import annotations

from pathlib import Path

import pytest

from taco.core.indexing import (
    DocumentInput,
    IndexConfig,
    IndexerError,
    build_index,
    load_documents,
    scan_markdown_files,
)


def _base_config() -> IndexConfig:
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


def test_build_index_classifies_docs_and_tasks() -> None:
    config = _base_config()
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
    config = _base_config()
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
    config = _base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
    ]

    with pytest.raises(IndexerError) as exc:
        build_index(docs, config)

    assert exc.value.code == "missing_required_docs"


def test_scan_markdown_files_is_stable(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "b.md").write_text("# b\n", encoding="utf-8")
    (tmp_path / "docs" / "a.md").write_text("# a\n", encoding="utf-8")

    found = scan_markdown_files(tmp_path)
    assert [path.as_posix() for path in found] == sorted(
        path.as_posix() for path in found
    )


def test_load_documents_reads_markdown_files(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    doc = tmp_path / "docs" / "intent.md"
    doc.write_text("# Intent\n", encoding="utf-8")

    loaded = load_documents(tmp_path, ["docs/intent.md"])
    assert loaded[0].path == "docs/intent.md"
    assert loaded[0].sections[0].heading == "Intent"


def test_index_config_from_dict_supports_overrides() -> None:
    raw = {
        "docs": {
            "intent": "custom/intent.md",
            "architecture": "custom/arch.md",
            "plan": "custom/plan.md",
            "glossary": "custom/glossary.md",
            "principles": ["custom/principles.md"],
            "todo": ["custom/todo.md"],
            "tasks_glob": "custom/tasks/T-*.md",
        },
        "modules": {
            "git": {"path": "custom/git.md"},
        },
    }

    cfg = IndexConfig.from_dict(raw)
    assert cfg.intent_path == "custom/intent.md"
    assert cfg.tasks_glob == "custom/tasks/T-*.md"
    assert cfg.git_module_path == "custom/git.md"


def test_index_document_contract_to_dict() -> None:
    config = _base_config()
    docs = [
        DocumentInput.from_text("docs/intent.md", "# Intent\n"),
        DocumentInput.from_text("docs/architecture.md", "# Architecture\n"),
        DocumentInput.from_text("docs/plan.md", "# Plan\n"),
        DocumentInput.from_text("docs/glossary.md", "# Glossary\n"),
    ]
    graph = build_index(docs, config)
    payload = graph.documents[0].to_dict()

    assert set(payload.keys()) == {
        "path",
        "doc_type",
        "task_id",
        "node_id",
        "node_type",
        "headings",
        "links",
    }


def test_build_index_collects_reference_lookup() -> None:
    config = _base_config()
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
    config = _base_config()
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
