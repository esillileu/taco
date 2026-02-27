from __future__ import annotations

from pathlib import Path

from taco.core.indexing import (
    DocumentInput,
    IndexConfig,
    build_index,
    load_documents,
    scan_markdown_files,
)

from .fixture_index import base_config


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
    config = base_config()
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
