from __future__ import annotations

import re

from taco.core.indexing import IndexedDocument
from taco.core.packing.extract import _extract_front_matter
from taco.core.packing.models import PackSnippet
from taco.core.routing.policy import mode_for_heading


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
    for heading in task_doc.headings:
        mode = mode_for_heading(heading.heading)
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

def _derive_execution_intent(task_path: str, document_texts: dict[str, str]) -> str:
    text = document_texts.get(task_path, "")
    lines = text.splitlines()
    in_goal = False
    for raw in lines:
        line = raw.strip()
        if line == "## Goal":
            in_goal = True
            continue
        if in_goal and line.startswith("## "):
            break
        if in_goal and line.startswith("- "):
            return line[2:].strip()
    return "Execute task scope and verification criteria deterministically."

def _derive_scope_boundary(
    task_path: str, document_texts: dict[str, str]
) -> dict[str, tuple[str, ...]]:
    text = document_texts.get(task_path, "")
    fm = _extract_front_matter(text)
    scope = fm.get("scope", {})
    if not isinstance(scope, dict):
        return {"allowed_paths": (), "forbidden_paths": ()}
    allowed = tuple(
        dict.fromkeys(
            item.strip()
            for item in scope.get("in", [])
            if isinstance(item, str) and item.strip()
        )
    )
    forbidden = tuple(
        dict.fromkeys(
            item.strip()
            for item in scope.get("out", [])
            if isinstance(item, str) and item.strip()
        )
    )
    return {"allowed_paths": allowed, "forbidden_paths": forbidden}

def _derive_reference_slices(
    snippets: list[PackSnippet],
) -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in snippets:
        if not item.group.startswith("ref:"):
            continue
        key = f"{item.path}#{item.anchor_id}"
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "path": item.path,
                "anchor_id": item.anchor_id,
                "heading": item.heading,
            }
        )
    return tuple(rows)
