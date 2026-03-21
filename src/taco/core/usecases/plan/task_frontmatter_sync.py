from __future__ import annotations

from pathlib import Path
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _collect_string_list,
    _compose_front_matter,
    _fingerprint,
    _split_front_matter,
)
from taco.core.usecases.io import read_text, write_text

from .intent_pipeline import build_intent_pipeline_bundle


def _select_blueprint(bundle: dict[str, Any], path: str) -> dict[str, Any]:
    generated = bundle.get("generated_tasks")
    if not isinstance(generated, list) or not generated:
        raise ToolError(
            "task_blueprint_missing",
            "no generated task blueprint found for intent",
            {"intent_id": bundle.get("intent", {}).get("id", "")},
        )

    by_path = path.strip()
    for row in generated:
        if not isinstance(row, dict):
            continue
        if str(row.get("path", "")).strip() == by_path:
            return row
    return generated[0]


def _normalize_front_matter(
    merged: dict[str, Any],
    *,
    intent_id: str,
    blueprint: dict[str, Any],
) -> dict[str, Any]:
    fm = dict(merged)
    fm.setdefault("type", "task")
    fm.setdefault("status", "active")
    fm.setdefault("plan_ref", "PLAN-MAIN")

    scope = fm.get("scope")
    if not isinstance(scope, dict):
        scope = {}
    scope_in = _collect_string_list(scope.get("in"))
    scope_out = _collect_string_list(scope.get("out"))
    if not scope_in:
        scope_in = ["src/taco", ".context/project"]
    scope["in"] = scope_in
    scope["out"] = scope_out
    fm["scope"] = scope

    refs = fm.get("references")
    if not isinstance(refs, dict):
        refs = {}
    refs_modules = _collect_string_list(refs.get("modules")) or ["ARCH-INDEX"]
    refs_flows = _collect_string_list(refs.get("flows")) or ["PLAN-MAIN"]
    refs_schemas = _collect_string_list(refs.get("schemas")) or ["GOV-CODE-PRINCIPLES"]
    refs["modules"] = refs_modules
    refs["flows"] = refs_flows
    refs["schemas"] = refs_schemas
    fm["references"] = refs

    links = _collect_string_list(fm.get("links"))
    for required in ["PLAN-MAIN", intent_id, *refs_modules, *refs_flows, *refs_schemas]:
        if required not in links:
            links.append(required)
    fm["links"] = links

    base = blueprint.get("front_matter_requirements")
    if isinstance(base, dict):
        base_id = str(base.get("id", "")).strip()
        base_title = str(base.get("title", "")).strip()
        if not str(fm.get("id", "")).strip() and base_id:
            fm["id"] = base_id
        if not str(fm.get("title", "")).strip() and base_title:
            fm["title"] = base_title

    return fm


def plan_task_frontmatter_sync(
    state: RepoState, args: dict[str, Any]
) -> dict[str, Any]:
    intent_id = str(args.get("intent_id", "")).strip()
    if not intent_id:
        raise ToolError("invalid_input", "intent_id is required", {"key": "intent_id"})
    path = str(args.get("path", "")).strip()
    if not path:
        raise ToolError("invalid_input", "path is required", {"key": "path"})

    overrides = args.get("front_matter")
    if overrides is not None and not isinstance(overrides, dict):
        raise ToolError(
            "invalid_input",
            "front_matter must be an object when provided",
            {"key": "front_matter"},
        )

    target = Path(path)
    if state.storage is None or not state.storage.exists(target):
        raise ToolError(
            "task_document_missing",
            "task document must be authored by agent before frontmatter sync",
            {"path": path},
        )

    bundle = build_intent_pipeline_bundle(state, intent_id)
    blueprint = _select_blueprint(bundle, path)

    existing_text = read_text(state, path)
    existing_meta, body = _split_front_matter(existing_text)
    base_fm = blueprint.get("front_matter_requirements")
    merged: dict[str, Any] = {}
    if isinstance(base_fm, dict):
        merged.update(base_fm)
    if isinstance(existing_meta, dict):
        merged.update(existing_meta)
    if isinstance(overrides, dict):
        merged.update(overrides)

    normalized = _normalize_front_matter(
        merged, intent_id=intent_id, blueprint=blueprint
    )
    write_text(state, path, _compose_front_matter(normalized, body))

    task_id = str(normalized.get("id", "")).strip()
    return {
        "path": path,
        "intent_id": intent_id,
        "task_id": task_id,
        "front_matter": normalized,
        "fingerprint": _fingerprint(
            [intent_id, path, task_id, str(normalized.get("title", ""))]
        ),
    }
