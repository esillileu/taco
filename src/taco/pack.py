from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import asdict, dataclass

from taco.indexer import HeadingRef, IndexedDocument, IndexGraph


@dataclass(frozen=True)
class BudgetConfig:
    default_tokens: int
    priority_order: tuple[str, ...]
    required_groups: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> BudgetConfig:
        budget = raw.get("budget")
        if not isinstance(budget, dict):
            raise PackError("invalid_config", "budget config must be an object", {})
        default_tokens = budget.get("default_tokens")
        priority_order = budget.get("priority_order")
        required_groups = budget.get(
            "required_groups",
            [
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ],
        )
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
        if not isinstance(required_groups, list) or not all(
            isinstance(item, str) for item in required_groups
        ):
            raise PackError(
                "invalid_config",
                "budget.required_groups must be a list of strings",
                {"key": "required_groups"},
            )
        return cls(
            default_tokens=default_tokens,
            priority_order=tuple(priority_order),
            required_groups=tuple(required_groups),
        )


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
    pack_version: str
    task_id: str
    budget_tokens: int
    used_tokens: int
    next_actions: tuple[str, ...]
    acceptance_checks: tuple[str, ...]
    verification_commands: tuple[str, ...]
    write_targets: tuple[dict[str, str | int], ...]
    context_snippets: tuple[PackSnippet, ...]
    unknowns: tuple[str, ...]
    coverage: dict[str, list[str]]
    dropped: tuple[DroppedSnippet, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "pack_version": self.pack_version,
            "task_id": self.task_id,
            "budget_tokens": self.budget_tokens,
            "used_tokens": self.used_tokens,
            "next_actions": list(self.next_actions),
            "acceptance_checks": list(self.acceptance_checks),
            "verification_commands": list(self.verification_commands),
            "write_targets": list(self.write_targets),
            "context_snippets": [
                snippet.to_dict() for snippet in self.context_snippets
            ],
            "unknowns": list(self.unknowns),
            "coverage": self.coverage,
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

    task_doc = _find_doc(index.documents, task_path)
    if not task_doc:
        raise PackError(
            code="task_doc_missing",
            message="task document missing from indexed docs",
            details={"task_id": task_id, "path": task_path},
        )

    candidates = _build_candidates(task_id, task_path, index, estimator)
    if not candidates:
        raise PackError(
            code="pack_not_ready",
            message="required selector groups are missing",
            details={
                "task_id": task_id,
                "missing_groups": ",".join(sorted(set(budget.required_groups))),
            },
        )

    by_group: dict[str, list[_CandidateSnippet]] = {}
    for item in candidates:
        by_group.setdefault(item.group, []).append(item)

    missing_groups = sorted(set(budget.required_groups) - set(by_group))
    if missing_groups:
        raise PackError(
            code="pack_not_ready",
            message="required selector groups are missing",
            details={"task_id": task_id, "missing_groups": ",".join(missing_groups)},
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
    required_set = set(budget.required_groups)

    for candidate in sorted_candidates:
        is_required = candidate.group in required_set
        next_used = used_tokens + candidate.estimated_tokens
        if is_required or next_used <= budget.default_tokens:
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

    next_actions = _collect_action_items(included, "pack.next_actions")
    acceptance_checks = _collect_action_items(included, "pack.acceptance_checks")
    verification_commands = _collect_action_items(
        included, "pack.verification_commands"
    )
    unknowns = tuple(_collect_action_items(included, "pack.unknowns"))
    write_targets = _derive_write_targets(task_doc)

    return PackResult(
        pack_version="2",
        task_id=task_id,
        budget_tokens=budget.default_tokens,
        used_tokens=used_tokens,
        next_actions=tuple(next_actions),
        acceptance_checks=tuple(acceptance_checks),
        verification_commands=tuple(verification_commands),
        write_targets=write_targets,
        context_snippets=tuple(included),
        unknowns=unknowns,
        coverage={
            "required_groups": sorted(required_set),
            "missing_groups": missing_groups,
        },
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
    candidates: list[_CandidateSnippet] = []
    for doc in index.documents:
        if doc.path.startswith("docs/dev/tasks/") and doc.path != task_path:
            continue
        for heading in doc.headings:
            for group in heading.pack_groups:
                if group.startswith("task.") and doc.path != task_path:
                    continue
                candidates.append(
                    _to_candidate(
                        group=group,
                        path=doc.path,
                        heading=heading,
                        document_texts=index.document_texts,
                        estimator=estimator,
                        reason="selector_match",
                    )
                )
    return candidates


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


def _collect_action_items(snippets: list[PackSnippet], group: str) -> list[str]:
    values: list[str] = []
    for snippet in snippets:
        if snippet.group != group:
            continue
        for line in snippet.content.splitlines():
            raw = line.strip()
            if not raw:
                continue
            if raw.startswith("## "):
                continue
            if raw.startswith("<!--"):
                continue
            if raw.startswith("- "):
                values.append(raw[2:].strip())
            elif re.match(r"^\d+\.\s+", raw):
                values.append(re.sub(r"^\d+\.\s+", "", raw))
            else:
                values.append(raw)
    deduped: list[str] = []
    for item in values:
        if item not in deduped:
            deduped.append(item)
    return deduped


def _derive_write_targets(
    task_doc: IndexedDocument,
) -> tuple[dict[str, str | int], ...]:
    targets: list[dict[str, str | int]] = []
    heading_to_mode = {
        "Implementation Result": "append_implementation",
        "Verification Result": "append_verification",
    }
    for heading in task_doc.headings:
        mode = heading_to_mode.get(heading.heading)
        if not mode:
            continue
        targets.append(
            {
                "path": task_doc.path,
                "heading": heading.heading,
                "line_hint": heading.end_line,
                "mode": mode,
            }
        )
    return tuple(targets)
