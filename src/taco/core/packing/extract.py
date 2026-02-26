from __future__ import annotations

from collections.abc import Callable
from typing import Any

import yaml

from taco.core.indexing import HeadingRef, IndexedDocument
from taco.core.packing.models import PackError, _CandidateSnippet


def _extract_task_context_requirements(
    task_doc: IndexedDocument,
    document_texts: dict[str, str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    from_frontmatter = _extract_task_front_matter_requirements(
        task_doc.path, document_texts
    )
    heading = next(
        (item for item in task_doc.headings if item.heading == "Context Requirements"),
        None,
    )
    if heading is None:
        return from_frontmatter

    text = document_texts.get(task_doc.path)
    if text is None:
        return from_frontmatter
    lines = text.splitlines()
    start = max(heading.start_line - 1, 0)
    end = min(heading.end_line, len(lines))
    block = "\n".join(lines[start:end])

    required_refs = tuple(
        dict.fromkeys(from_frontmatter[0] + _extract_refs_for_key(block, "required"))
    )
    optional_refs = tuple(
        dict.fromkeys(from_frontmatter[1] + _extract_refs_for_key(block, "optional"))
    )
    return required_refs, optional_refs

def _extract_refs_for_key(block: str, key: str) -> tuple[str, ...]:
    values: list[str] = []
    prefix = f"- {key}:"
    for line in block.splitlines():
        raw = line.strip()
        if not raw.lower().startswith(prefix):
            continue
        payload = raw[len(prefix) :].strip()
        for part in payload.split(","):
            value = part.strip().strip("`")
            if not value:
                continue
            if value not in values:
                values.append(value)
    return tuple(values)

def _extract_task_front_matter_requirements(
    task_path: str, document_texts: dict[str, str]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    text = document_texts.get(task_path)
    if text is None:
        return (), ()
    front_matter = _extract_front_matter(text)
    required: list[str] = []
    optional: list[str] = []

    plan_ref = front_matter.get("plan_ref")
    if isinstance(plan_ref, str) and plan_ref.strip():
        required.append(plan_ref.strip())

    refs = front_matter.get("references")
    if not isinstance(refs, dict):
        return tuple(required), tuple(optional)
    for key in ("modules", "flows", "schemas", "governance"):
        values = refs.get(key)
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, str):
                continue
            value = item.strip()
            if not value:
                continue
            if value not in required:
                required.append(value)
    return tuple(required), tuple(optional)

def _extract_front_matter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end < 0:
        return {}
    raw = "\n".join(lines[1:end]).strip()
    if not raw:
        return {}
    loaded = yaml.safe_load(raw)
    if not isinstance(loaded, dict):
        return {}
    return loaded

def _infer_task_groups(heading: str) -> tuple[str, ...]:
    if heading in {"Intent", "Goal"}:
        return ("task.core",)
    if heading == "Scope":
        return ("task.core", "pack.next_actions")
    if heading == "Implementation Approach":
        return ("task.plans", "pack.next_actions")
    if heading == "Verification Approach":
        return ("task.plans", "pack.acceptance_checks", "pack.verification_commands")
    return ()

def _to_candidate(
    group: str,
    path: str,
    heading: HeadingRef,
    document_texts: dict[str, str],
    estimator: Callable[[str], int],
    reason: str | None = None,
    required: bool = False,
) -> _CandidateSnippet:
    content = _extract_section_text(path, heading, document_texts)
    return _CandidateSnippet(
        group=group,
        path=path,
        heading_ref=heading,
        content=content,
        estimated_tokens=estimator(content),
        reason=reason or "task_relevance",
        required=required,
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
