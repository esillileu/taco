from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from fnmatch import fnmatch
from pathlib import Path

from taco.parser import SectionSlice, parse_markdown_sections

TASK_ID_RE = re.compile(r"(T-\d{3})")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


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
    start_line: int
    end_line: int

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True)
class IndexedDocument:
    path: str
    doc_type: str
    task_id: str | None
    headings: tuple[HeadingRef, ...]
    links: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "doc_type": self.doc_type,
            "task_id": self.task_id,
            "headings": [heading.to_dict() for heading in self.headings],
            "links": list(self.links),
        }


@dataclass(frozen=True)
class IndexGraph:
    documents: tuple[IndexedDocument, ...]
    task_index: dict[str, str]
    link_graph: dict[str, tuple[str, ...]]
    heading_lookup: dict[str, HeadingRef]
    document_texts: dict[str, str]


class IndexerError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def scan_markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def load_documents(root: Path, paths: list[str]) -> list[DocumentInput]:
    docs: list[DocumentInput] = []
    for rel_path in sorted(paths):
        text = (root / rel_path).read_text(encoding="utf-8")
        docs.append(DocumentInput.from_text(path=rel_path, text=text))
    return docs


def build_index(documents: list[DocumentInput], config: IndexConfig) -> IndexGraph:
    sorted_docs = sorted(documents, key=lambda doc: doc.path)
    by_path = {doc.path: doc for doc in sorted_docs}
    _validate_required_docs(by_path, config)

    indexed_docs: list[IndexedDocument] = []
    task_index: dict[str, str] = {}
    link_graph: dict[str, tuple[str, ...]] = {}
    heading_lookup: dict[str, HeadingRef] = {}

    for doc in sorted_docs:
        doc_type = _classify_doc_type(doc.path, config)
        task_id = _extract_task_id(doc.path)
        if task_id:
            task_index[task_id] = doc.path

        headings = tuple(
            HeadingRef(
                level=section.level,
                heading=section.heading,
                anchor_id=section.anchor_id,
                pack_groups=section.pack_groups,
                start_line=section.start_line,
                end_line=section.end_line,
            )
            for section in doc.sections
        )
        links = tuple(_extract_local_links(doc.text))
        link_graph[doc.path] = links
        for heading in headings:
            heading_lookup[f"{doc.path}#{heading.anchor_id}"] = heading

        indexed_docs.append(
            IndexedDocument(
                path=doc.path,
                doc_type=doc_type,
                task_id=task_id,
                headings=headings,
                links=links,
            )
        )

    return IndexGraph(
        documents=tuple(indexed_docs),
        task_index=task_index,
        link_graph=link_graph,
        heading_lookup=heading_lookup,
        document_texts={doc.path: doc.text for doc in sorted_docs},
    )


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


def _validate_required_docs(
    by_path: dict[str, DocumentInput], config: IndexConfig
) -> None:
    required = {
        config.intent_path,
        config.architecture_path,
        config.plan_path,
        config.glossary_path,
    }
    missing = sorted(required - set(by_path))
    if missing:
        raise IndexerError(
            code="missing_required_docs",
            message="required SSOT docs are missing",
            details={"missing": ", ".join(missing)},
        )


def _classify_doc_type(path: str, config: IndexConfig) -> str:
    if path == config.intent_path:
        return "intent"
    if path == config.architecture_path:
        return "architecture"
    if path == config.plan_path:
        return "plan"
    if path == config.glossary_path:
        return "glossary"
    if path in config.principles_paths:
        return "principles"
    if path in config.todo_paths:
        return "todo"
    if config.git_module_path and path == config.git_module_path:
        return "git"
    if fnmatch(path, config.tasks_glob):
        return "task"
    if path.startswith("docs/dev/git/"):
        return "git-detail"
    return "doc"


def _extract_task_id(path: str) -> str | None:
    match = TASK_ID_RE.search(path)
    if not match:
        return None
    return match.group(1)


def _extract_local_links(text: str) -> list[str]:
    links: list[str] = []
    for link in LINK_RE.findall(text):
        if (
            link.startswith("http://")
            or link.startswith("https://")
            or link.startswith("#")
        ):
            continue
        links.append(link)
    return links
