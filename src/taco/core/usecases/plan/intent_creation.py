from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _collect_string_list,
    _compose_front_matter,
    _fingerprint,
)
from taco.core.usecases.io import write_text


def intents_dir_from_state(state: RepoState) -> str:
    docs = state.config_raw.get("docs", {})
    if isinstance(docs, dict):
        intents_glob = docs.get("intents_glob")
        if isinstance(intents_glob, str) and "/" in intents_glob:
            return intents_glob.rsplit("/", 1)[0].strip()
        intent_path = docs.get("intent")
        if isinstance(intent_path, str) and intent_path.strip():
            cleaned = intent_path.strip()
            if cleaned.endswith("/index.md"):
                return cleaned.rsplit("/", 1)[0]
            if "/" in cleaned:
                return f"{cleaned.rsplit('/', 1)[0]}/intents"
    return ".context/project/intents"


def next_intent_num(state: RepoState) -> int:
    max_num = 0
    for doc in state.index.documents:
        if doc.doc_type != "intent" or not isinstance(doc.metadata, dict):
            continue
        raw = str(doc.metadata.get("id", "")).strip()
        match = re.fullmatch(r"I-(\d+)", raw)
        if match:
            max_num = max(max_num, int(match.group(1)))
    intents_path = state.root / intents_dir_from_state(state)
    if intents_path.exists():
        for path in intents_path.glob("I-*.md"):
            match = re.match(r"I-(\d+)", path.name)
            if match:
                max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return normalized or "intent"


def _plan_node_id(state: RepoState) -> str:
    for doc in state.index.documents:
        if doc.doc_type != "plan" or not isinstance(doc.metadata, dict):
            continue
        node_id = str(doc.metadata.get("id", "")).strip()
        if node_id:
            return node_id
    return "PLAN-MAIN"


def _default_links(state: RepoState, plan_ref: str) -> list[str]:
    links: list[str] = []
    for candidate in ("PROJ-INTENT-INDEX", "PROJ-INTENT", plan_ref, "ARCH-INDEX"):
        if candidate == plan_ref:
            links.append(candidate)
            continue
        if candidate in state.index.node_index:
            links.append(candidate)
    return list(dict.fromkeys(links))


def _render_scope(scope_in: list[str], scope_out: list[str]) -> str:
    lines = ["## Scope", ""]
    if scope_in:
        lines.append("- In Scope:")
        lines.extend(f"  - {item}" for item in scope_in)
    else:
        lines.append("- In Scope: refine during planning.")
    if scope_out:
        lines.append("- Out of Scope:")
        lines.extend(f"  - {item}" for item in scope_out)
    else:
        lines.append("- Out of Scope: none declared.")
    return "\n".join(lines)


def _render_intent_doc(
    *,
    intent_id: str,
    title: str,
    intent_text: str,
    plan_ref: str,
    links: list[str],
    scope_in: list[str],
    scope_out: list[str],
    kind: str | None,
    design_impact: str | None,
) -> str:
    meta: dict[str, Any] = {
        "id": intent_id,
        "type": "intent",
        "title": title,
        "status": "active",
        "plan_ref": plan_ref,
        "task_refs": [],
        "links": links,
    }
    if kind:
        meta["kind"] = kind
    if design_impact:
        meta["design_impact"] = design_impact
    body = "\n".join(
        [
            f"# Intent: {intent_id.lower()}-{_slugify(title)}",
            "",
            "## Intent",
            "",
            f"- {intent_text.strip()}",
            "",
            _render_scope(scope_in, scope_out),
            "",
            "## Source",
            "",
            "- input_type: agent_decomposed",
        ]
    )
    return _compose_front_matter(meta, body)


def create_many_intents(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intents = args.get("intents")
    if not isinstance(intents, list) or not intents:
        raise ToolError(
            "invalid_input",
            "intents must be a non-empty array",
            {"key": "intents"},
        )
    plan_ref_override = args.get("plan_ref")
    if plan_ref_override is not None and not isinstance(plan_ref_override, str):
        raise ToolError(
            "invalid_input", "plan_ref must be a string", {"key": "plan_ref"}
        )
    plan_ref = (
        plan_ref_override.strip()
        if isinstance(plan_ref_override, str) and plan_ref_override.strip()
        else _plan_node_id(state)
    )

    created: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []
    next_num = next_intent_num(state)
    intents_dir = intents_dir_from_state(state)
    for idx, raw in enumerate(intents):
        if not isinstance(raw, dict):
            raise ToolError(
                "invalid_input",
                "each intent must be an object",
                {"index": idx},
            )
        title = str(raw.get("title", "")).strip()
        intent_text = str(raw.get("intent", "")).strip()
        if not title or not intent_text:
            raise ToolError(
                "invalid_input",
                "intent item requires title and intent",
                {"index": idx, "required": ["title", "intent"]},
            )
        scope_in = _collect_string_list(raw.get("scope_in"))
        scope_out = _collect_string_list(raw.get("scope_out"))
        if not scope_in:
            warnings.append({"index": str(idx), "code": "scope_in_empty"})
        links = _collect_string_list(raw.get("links")) or _default_links(
            state, plan_ref
        )
        kind = str(raw.get("kind", "")).strip() or None
        design_impact = str(raw.get("design_impact", "")).strip() or None

        intent_id = ""
        intent_path = ""
        for _ in range(1000):
            intent_id = f"I-{next_num:03d}"
            filename = f"{intent_id}-{_slugify(title)}.md"
            intent_path = str(PurePosixPath(intents_dir) / filename)
            next_num += 1
            if state.storage is None or not state.storage.exists(Path(intent_path)):
                break
        markdown = _render_intent_doc(
            intent_id=intent_id,
            title=title,
            intent_text=intent_text,
            plan_ref=plan_ref,
            links=links,
            scope_in=scope_in,
            scope_out=scope_out,
            kind=kind,
            design_impact=design_impact,
        )
        write_text(state, intent_path, markdown)
        created.append(
            {
                "intent_id": intent_id,
                "path": intent_path,
                "title": title,
                "fingerprint": _fingerprint([intent_id, title, intent_text, plan_ref]),
            }
        )
    return {"created": created, "count": len(created), "warnings": warnings}
