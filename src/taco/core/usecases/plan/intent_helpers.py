from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _collect_string_list,
    _compose_front_matter,
    _placeholder_markers_in_text,
    _split_front_matter,
    _sync_plan_task_sections,
)
from taco.core.usecases.io import read_text, write_text


def plan_path_from_state(state: RepoState) -> str:
    docs = state.config_raw.get("docs", {})
    if isinstance(docs, dict):
        value = docs.get("plan")
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ToolError(
        "plan_not_found",
        "plan path is not configured",
        {"key": "docs.plan"},
    )


def tasks_dir_from_config(state: RepoState) -> str:
    docs = state.config_raw.get("docs", {})
    if isinstance(docs, dict):
        glob = docs.get("tasks_glob")
        if isinstance(glob, str) and glob.strip():
            raw = glob.strip()
            if "/" in raw:
                return raw.rsplit("/", 1)[0]
    return ".context/project/tasks"


def next_task_id(task_index: dict[str, str]) -> str:
    max_num = 0
    for task_id in task_index:
        match = re.fullmatch(r"T-(\d+)", task_id.strip())
        if not match:
            continue
        max_num = max(max_num, int(match.group(1)))
    return f"T-{max_num + 1:03d}"


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return normalized or "intent-work"


def build_task_blueprint(
    task_id: str,
    path: str,
    title: str,
    links: list[str],
    refs_modules: list[str],
    refs_flows: list[str],
    refs_schemas: list[str],
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "path": path,
        "front_matter_requirements": {
            "id": task_id,
            "type": "task",
            "title": title,
            "status": "active",
            "plan_ref": "PLAN-MAIN",
            "scope": {"in": ["src/taco", ".context/project"], "out": []},
            "references": {
                "modules": refs_modules,
                "flows": refs_flows,
                "schemas": refs_schemas,
            },
            "links": links,
        },
        "section_requirements": [
            {"heading": "Intent", "required": True},
            {"heading": "Goal", "required": True},
            {"heading": "Scope", "required": True},
            {"heading": "Implementation Approach", "required": True},
            {"heading": "Verification Approach", "required": True},
            {"heading": "Implementation Result", "required": True},
            {"heading": "Verification Result", "required": True},
        ],
        "readiness_requirements": [
            "task document must exist at declared path",
            "scope.in/out arrays in front matter",
            "references.modules/flows/schemas arrays with non-empty values",
            "Implementation Approach must include actionable items",
            "Verification Approach must include verification criteria",
            "placeholder markers are forbidden",
        ],
    }


def authored_blueprints_for_intent(
    state: RepoState, intent_id: str
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in state.index.documents:
        if doc.doc_type != "task" or not isinstance(doc.metadata, dict):
            continue
        links = _collect_string_list(doc.metadata.get("links"))
        if intent_id not in links:
            continue
        task_id = (
            str(doc.metadata.get("id", "")).strip() or str(doc.task_id or "").strip()
        )
        if not task_id:
            continue
        refs = doc.metadata.get("references")
        refs_modules = (
            _collect_string_list(refs.get("modules")) if isinstance(refs, dict) else []
        )
        refs_flows = (
            _collect_string_list(refs.get("flows")) if isinstance(refs, dict) else []
        )
        refs_schemas = (
            _collect_string_list(refs.get("schemas")) if isinstance(refs, dict) else []
        )
        rows.append(
            build_task_blueprint(
                task_id=task_id,
                path=doc.path,
                title=str(doc.metadata.get("title", f"{task_id}-task")),
                links=links,
                refs_modules=refs_modules or ["ARCH-INDEX"],
                refs_flows=refs_flows or ["FLOW-MODE-TRANSITION"],
                refs_schemas=refs_schemas or ["GOV-CODE-PRINCIPLES"],
            )
        )
    rows.sort(
        key=lambda item: (str(item.get("task_id", "")), str(item.get("path", "")))
    )
    return rows


def derive_generated_tasks(
    state: RepoState,
    intent_id: str,
    intent: dict[str, Any],
    links: list[str],
    task_refs: list[str],
    gaps: list[str],
    tasks_dir: str,
) -> list[dict[str, Any]]:
    authored = authored_blueprints_for_intent(state, intent_id)
    if authored:
        return authored
    existing_refs = [
        task_id for task_id in task_refs if task_id in state.index.task_index
    ]
    if existing_refs and not gaps:
        return []

    next_id = next_task_id(state.index.task_index)
    slug_source = str(intent.get("title", "")) or intent_id.lower()
    slug = slugify(slug_source)
    path = str(PurePosixPath(tasks_dir) / f"{next_id}-{slug}.md")

    refs_modules = [v for v in links if v.startswith("MOD-") or v == "ARCH-INDEX"] or [
        "ARCH-INDEX"
    ]
    refs_flows = [v for v in links if v.startswith("FLOW-") or v == "PLAN-MAIN"] or [
        "FLOW-MODE-TRANSITION"
    ]
    refs_schemas = [
        v for v in links if v.startswith("SCH-") or v.startswith("GOV-")
    ] or ["GOV-CODE-PRINCIPLES"]

    return [
        build_task_blueprint(
            task_id=next_id,
            path=path,
            title=f"{next_id}-{slug}",
            links=list(
                dict.fromkeys(
                    ["PLAN-MAIN", intent_id, *refs_modules, *refs_flows, *refs_schemas]
                )
            ),
            refs_modules=refs_modules,
            refs_flows=refs_flows,
            refs_schemas=refs_schemas,
        )
    ]


def queue_update_preview(bundle: dict[str, Any]) -> tuple[str | None, list[str]]:
    generated = bundle["generated_tasks"]
    if not generated:
        return None, []
    promoted = generated[0]["task_id"]
    queued = [row["task_id"] for row in generated[1:]]
    deduped: list[str] = []
    for task_id in queued:
        if task_id not in deduped:
            deduped.append(task_id)
    return promoted, deduped


def merged_task_refs(bundle: dict[str, Any]) -> list[str]:
    merged = _collect_string_list(bundle.get("task_refs", []))
    for row in bundle.get("generated_tasks", []):
        if not isinstance(row, dict):
            continue
        task_id = str(row.get("task_id", "")).strip()
        if task_id and task_id not in merged:
            merged.append(task_id)
    return merged


def plan_intent_apply_preview(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    promoted, queued = queue_update_preview(bundle)
    return [
        {
            "path": bundle["intent_path"],
            "action": "update_front_matter_task_refs",
            "task_refs": merged_task_refs(bundle),
        },
        {
            "path": bundle["proposal"]["plan_path"],
            "action": "update_task_queue",
            "active_promoted": promoted,
            "next_appended": queued,
        },
    ]


def apply_intent_bundle(state: RepoState, bundle: dict[str, Any]) -> None:
    generated = bundle["generated_tasks"]
    plan_path = bundle["proposal"]["plan_path"]
    plan_text = state.index.document_texts.get(plan_path) or read_text(state, plan_path)
    plan_meta, plan_body = _split_front_matter(plan_text)
    if not plan_meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"document": "plan", "path": plan_path},
        )

    active = _collect_string_list(plan_meta.get("active_tasks"))
    if generated and active:
        raise ToolError(
            "queue_policy_violation",
            "active_tasks must be empty before auto promotion",
            {"active_tasks": active},
        )
    existing_next = _collect_string_list(plan_meta.get("next_tasks"))
    existing_blocked = _collect_string_list(plan_meta.get("blocked_tasks"))
    promoted, queued = queue_update_preview(bundle)

    plan_meta["active_tasks"] = [promoted] if promoted else active
    plan_meta["blocked_tasks"] = existing_blocked
    plan_meta["next_tasks"] = queued + [
        item for item in existing_next if item not in queued and item != promoted
    ]

    active_intents = _collect_string_list(plan_meta.get("active_intents"))
    if bundle["intent"]["id"] not in active_intents:
        active_intents.append(bundle["intent"]["id"])
    plan_meta["active_intents"] = active_intents

    synced_body = _sync_plan_task_sections(
        body=plan_body,
        plan_path=plan_path,
        task_index=state.index.task_index,
        active_tasks=plan_meta["active_tasks"],
        blocked_tasks=plan_meta["blocked_tasks"],
        next_tasks=plan_meta["next_tasks"],
    )
    write_text(state, plan_path, _compose_front_matter(plan_meta, synced_body))

    intent_path = bundle["intent_path"]
    intent_text = bundle["intent_text"]
    intent_meta, intent_body = _split_front_matter(intent_text)
    if not intent_meta:
        raise ToolError(
            "front_matter_missing",
            "intent front matter is required",
            {"document": "intent", "path": intent_path},
        )

    refs = merged_task_refs(bundle)
    intent_meta["task_refs"] = refs
    intent_links = _collect_string_list(intent_meta.get("links"))
    for task_id in refs:
        if task_id not in intent_links:
            intent_links.append(task_id)
    intent_meta["links"] = intent_links

    if _placeholder_markers_in_text(intent_text):
        raise ToolError(
            "intent_placeholder_detected",
            "intent placeholder markers must be removed before apply",
            {"path": intent_path},
        )

    write_text(state, intent_path, _compose_front_matter(intent_meta, intent_body))
