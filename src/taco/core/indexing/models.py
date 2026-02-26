from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from taco.core.parsing.parser import SectionSlice, parse_markdown_sections


def _get_str(raw: dict[str, object], key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise IndexerError(
            code="invalid_config",
            message=f"config key '{key}' must be a string",
            details={"key": key},
        )
    return value


def _get_str_list(raw: dict[str, object], key: str) -> list[str]:
    value = raw.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise IndexerError(
            code="invalid_config",
            message=f"config key '{key}' must be a list of strings",
            details={"key": key},
        )
    return value


@dataclass(frozen=True)
class IndexConfig:
    intent_path: str
    architecture_path: str
    plan_path: str
    glossary_path: str
    principles_paths: tuple[str, ...]
    todo_paths: tuple[str, ...]
    tasks_glob: str
    git_module_path: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> IndexConfig:
        docs = raw.get("docs", {})
        modules = raw.get("modules", {})
        if not isinstance(docs, dict):
            raise IndexerError(
                code="invalid_config",
                message="docs config must be an object",
                details={},
            )
        if not isinstance(modules, dict):
            raise IndexerError(
                code="invalid_config",
                message="modules config must be an object",
                details={},
            )

        git_module_path: str | None = None
        git_cfg = modules.get("git")
        if isinstance(git_cfg, dict):
            git_path = git_cfg.get("path")
            if isinstance(git_path, str):
                git_module_path = git_path

        return cls(
            intent_path=_get_str(docs, "intent"),
            architecture_path=_get_str(docs, "architecture"),
            plan_path=_get_str(docs, "plan"),
            glossary_path=_get_str(docs, "glossary"),
            principles_paths=tuple(_get_str_list(docs, "principles")),
            todo_paths=tuple(_get_str_list(docs, "todo")),
            tasks_glob=_get_str(docs, "tasks_glob"),
            git_module_path=git_module_path,
        )

@dataclass(frozen=True)
class DocumentInput:
    path: str
    text: str
    sections: tuple[SectionSlice, ...]

    @classmethod
    def from_text(cls, path: str, text: str) -> DocumentInput:
        sections = tuple(parse_markdown_sections(path, text))
        return cls(path=path, text=text, sections=sections)

@dataclass(frozen=True)
class HeadingRef:
    level: int
    heading: str
    anchor_id: str
    pack_groups: tuple[str, ...]
    ref_ids: tuple[str, ...]
    start_line: int
    end_line: int

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)

@dataclass(frozen=True)
class IndexedDocument:
    path: str
    doc_type: str
    task_id: str | None
    node_id: str | None
    node_type: str | None
    metadata: dict[str, Any]
    headings: tuple[HeadingRef, ...]
    links: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "doc_type": self.doc_type,
            "task_id": self.task_id,
            "node_id": self.node_id,
            "node_type": self.node_type,
            "headings": [heading.to_dict() for heading in self.headings],
            "links": list(self.links),
        }

@dataclass(frozen=True)
class IndexGraph:
    documents: tuple[IndexedDocument, ...]
    task_index: dict[str, str]
    node_index: dict[str, str]
    link_graph: dict[str, tuple[str, ...]]
    heading_lookup: dict[str, HeadingRef]
    reference_lookup: dict[str, str]
    document_texts: dict[str, str]

class IndexerError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)
