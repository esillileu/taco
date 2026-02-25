from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import asdict, dataclass

from taco.indexer import HeadingRef, IndexedDocument, IndexGraph


@dataclass(frozen=True)
class BudgetConfig:
    default_tokens: int
    priority_order: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> BudgetConfig:
        budget = raw.get("budget")
        if not isinstance(budget, dict):
            raise PackError("invalid_config", "budget config must be an object", {})
        default_tokens = budget.get("default_tokens")
        priority_order = budget.get("priority_order")
        if not isinstance(default_tokens, int):
            raise PackError(
                "invalid_config",
                "budget.default_tokens must be an integer",
                {"key": "default_tokens"},
            )
        if not isinstance(priority_order, list) or not all(
            isinstance(item, str) for item in priority_order
        ):
            raise PackError(
                "invalid_config",
                "budget.priority_order must be a list of strings",
                {"key": "priority_order"},
            )
        return cls(default_tokens=default_tokens, priority_order=tuple(priority_order))


@dataclass(frozen=True)
class PackSnippet:
    group: str
    path: str
    heading: str
    anchor_id: str
    content: str
    estimated_tokens: int
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class DroppedSnippet:
    group: str
    path: str
    heading: str
    estimated_tokens: int
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PackResult:
    task_id: str
    budget_tokens: int
    used_tokens: int
    snippets: tuple[PackSnippet, ...]
    dropped: tuple[DroppedSnippet, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "budget_tokens": self.budget_tokens,
            "used_tokens": self.used_tokens,
            "snippets": [snippet.to_dict() for snippet in self.snippets],
            "dropped": [item.to_dict() for item in self.dropped],
        }


class PackError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def build_task_pack(
    task_id: str,
    index: IndexGraph,
    budget: BudgetConfig,
    token_estimator: Callable[[str], int] | None = None,
) -> PackResult:
    estimator = token_estimator or estimate_tokens
    task_path = index.task_index.get(task_id)
    if not task_path:
        raise PackError(
            code="task_not_found",
            message="task id not found in index",
            details={"task_id": task_id},
        )

    candidates = _build_candidates(task_id, task_path, index, estimator)
    if not candidates:
        raise PackError(
            code="empty_pack",
            message="no snippets could be assembled for task",
            details={"task_id": task_id},
        )

    priority_rank = {group: rank for rank, group in enumerate(budget.priority_order)}
    sorted_candidates = sorted(
        candidates,
        key=lambda item: (
            priority_rank.get(item.group, len(priority_rank)),
            item.path,
            item.heading_ref.start_line,
        ),
    )

    used_tokens = 0
    included: list[PackSnippet] = []
    dropped: list[DroppedSnippet] = []

    for candidate in sorted_candidates:
        next_used = used_tokens + candidate.estimated_tokens
        if next_used <= budget.default_tokens:
            used_tokens = next_used
            included.append(
                PackSnippet(
                    group=candidate.group,
                    path=candidate.path,
                    heading=candidate.heading_ref.heading,
                    anchor_id=candidate.heading_ref.anchor_id,
                    content=candidate.content,
                    estimated_tokens=candidate.estimated_tokens,
                    reason=candidate.reason,
                )
            )
            continue
        dropped.append(
            DroppedSnippet(
                group=candidate.group,
                path=candidate.path,
                heading=candidate.heading_ref.heading,
                estimated_tokens=candidate.estimated_tokens,
                reason="budget_exceeded",
            )
        )

    return PackResult(
        task_id=task_id,
        budget_tokens=budget.default_tokens,
        used_tokens=used_tokens,
        snippets=tuple(included),
        dropped=tuple(dropped),
    )


def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"\S+", text)))


@dataclass(frozen=True)
class _CandidateSnippet:
    group: str
    path: str
    heading_ref: HeadingRef
    content: str
    estimated_tokens: int
    reason: str


def _build_candidates(
    task_id: str,
    task_path: str,
    index: IndexGraph,
    estimator: Callable[[str], int],
) -> list[_CandidateSnippet]:
    task_doc = _find_doc(index.documents, task_path)
    if not task_doc:
        raise PackError(
            code="task_doc_missing",
            message="task document missing from indexed docs",
            details={"task_id": task_id, "path": task_path},
        )

    candidates: list[_CandidateSnippet] = []
    task_core_headings = {"Intent", "Goal", "Scope"}
    task_plan_headings = {"Implementation Approach", "Verification Approach"}

    for heading in task_doc.headings:
        group = None
        if heading.heading in task_core_headings:
            group = "task.core"
        elif heading.heading in task_plan_headings:
            group = "task.plans"
        if group:
            candidates.append(
                _to_candidate(
                    group,
                    task_doc.path,
                    heading,
                    index.document_texts,
                    estimator,
                )
            )

    arch_doc = _find_first_doc_by_type(index.documents, "architecture")
    if arch_doc:
        candidates.extend(
            _collect_first_n(
                group="arch.snippets",
                doc=arch_doc,
                n=2,
                document_texts=index.document_texts,
                estimator=estimator,
                reason="architecture_context",
            )
        )

    principles_doc = _find_first_doc_by_type(index.documents, "principles")
    if principles_doc:
        candidates.extend(
            _collect_first_n(
                group="principles.snippets",
                doc=principles_doc,
                n=2,
                document_texts=index.document_texts,
                estimator=estimator,
                reason="principles_context",
            )
        )

    glossary_doc = _find_first_doc_by_type(index.documents, "glossary")
    if glossary_doc:
        candidates.extend(
            _collect_first_n(
                group="glossary.terms",
                doc=glossary_doc,
                n=1,
                document_texts=index.document_texts,
                estimator=estimator,
                reason="glossary_context",
            )
        )

    return candidates


def _collect_first_n(
    group: str,
    doc: IndexedDocument,
    n: int,
    document_texts: dict[str, str],
    estimator: Callable[[str], int],
    reason: str,
) -> list[_CandidateSnippet]:
    selected = list(doc.headings[:n])
    return [
        _to_candidate(group, doc.path, heading, document_texts, estimator, reason)
        for heading in selected
    ]


def _to_candidate(
    group: str,
    path: str,
    heading: HeadingRef,
    document_texts: dict[str, str],
    estimator: Callable[[str], int],
    reason: str | None = None,
) -> _CandidateSnippet:
    content = _extract_section_text(path, heading, document_texts)
    return _CandidateSnippet(
        group=group,
        path=path,
        heading_ref=heading,
        content=content,
        estimated_tokens=estimator(content),
        reason=reason or "task_relevance",
    )


def _extract_section_text(
    path: str, heading: HeadingRef, document_texts: dict[str, str]
) -> str:
    text = document_texts.get(path)
    if text is None:
        raise PackError(
            code="document_text_missing",
            message="indexed document text is missing",
            details={"path": path},
        )
    lines = text.splitlines()
    start = max(heading.start_line - 1, 0)
    end = min(heading.end_line, len(lines))
    snippet = "\n".join(lines[start:end]).strip()
    return snippet


def _find_doc(
    documents: tuple[IndexedDocument, ...], path: str
) -> IndexedDocument | None:
    for doc in documents:
        if doc.path == path:
            return doc
    return None


def _find_first_doc_by_type(
    documents: tuple[IndexedDocument, ...], doc_type: str
) -> IndexedDocument | None:
    for doc in documents:
        if doc.doc_type == doc_type:
            return doc
    return None
