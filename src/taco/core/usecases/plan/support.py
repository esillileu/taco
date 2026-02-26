from __future__ import annotations

from typing import Any

from taco.core.indexing import IndexGraph
from taco.core.plan import (
    RepoState,
    _collect_string_list,
    _plan_path_from_config,
    _split_front_matter,
)
from taco.core.task.pack import _task_pack_readiness_missing
from taco.core.usecases.io import read_text


def _task_summaries(task_ids: list[str], index: IndexGraph) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        path = index.task_index.get(task_id, "")
        doc = next((item for item in index.documents if item.path == path), None)
        title = ""
        status = ""
        if doc and isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", ""))
            status = str(doc.metadata.get("status", ""))
        rows.append(
            {
                "task_id": task_id,
                "path": path,
                "status": status,
                "title": title,
            }
        )
    return rows

def _intent_summaries(intent_ids: list[str], index: IndexGraph) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for intent_id in intent_ids:
        path = index.node_index.get(intent_id, "")
        doc = next((item for item in index.documents if item.path == path), None)
        if doc is None or doc.doc_type != "intent":
            rows.append({"intent_id": intent_id, "path": "", "title": "", "status": ""})
            continue
        title = ""
        status = ""
        if isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", "") or "")
            status = str(doc.metadata.get("status", "") or "")
        rows.append(
            {
                "intent_id": intent_id,
                "path": path,
                "title": title,
                "status": status,
            }
        )
    return rows

def _intent_candidate_tasks(
    task_ids: list[str], state: RepoState
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        path = state.index.task_index.get(task_id, "")
        if not path:
            continue
        doc = next((item for item in state.index.documents if item.path == path), None)
        title = ""
        status = ""
        if doc and isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", "") or "")
            status = str(doc.metadata.get("status", "") or "")
        missing = _task_pack_readiness_missing(state, task_id)
        rows.append(
            {
                "task_id": task_id,
                "path": path,
                "title": title,
                "status": status,
                "ready_for_build": len(missing) == 0,
                "missing_requirements": missing,
            }
        )
    return rows

def _intent_coverage(
    task_ids: list[str], state: RepoState
) -> dict[str, list[dict[str, str]]]:
    module_ids: list[str] = []
    flow_ids: list[str] = []
    schema_ids: list[str] = []
    for task_id in task_ids:
        task_path = state.index.task_index.get(task_id)
        if not task_path:
            continue
        doc = next(
            (item for item in state.index.documents if item.path == task_path),
            None,
        )
        if doc is None or not isinstance(doc.metadata, dict):
            continue
        refs = doc.metadata.get("references")
        if not isinstance(refs, dict):
            continue
        for value in _collect_string_list(refs.get("modules")):
            if value not in module_ids:
                module_ids.append(value)
        for value in _collect_string_list(refs.get("flows")):
            if value not in flow_ids:
                flow_ids.append(value)
        for value in _collect_string_list(refs.get("schemas")):
            if value not in schema_ids:
                schema_ids.append(value)
    return {
        "modules": _summarize_ref_nodes(module_ids, state),
        "flows": _summarize_ref_nodes(flow_ids, state),
        "schemas": _summarize_ref_nodes(schema_ids, state),
    }

def _summarize_ref_nodes(ref_ids: list[str], state: RepoState) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ref_id in ref_ids:
        path = state.index.node_index.get(ref_id, "")
        doc = next((item for item in state.index.documents if item.path == path), None)
        title = ""
        doc_type = ""
        if doc and isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", "") or "")
            doc_type = doc.doc_type
        rows.append(
            {
                "id": ref_id,
                "path": path,
                "title": title,
                "type": doc_type,
            }
        )
    return rows

def _has_flow_intent_ref(state: RepoState, intent_id: str) -> bool:
    for doc in state.index.documents:
        if doc.doc_type != "flow":
            continue
        meta = doc.metadata if isinstance(doc.metadata, dict) else {}
        refs = _collect_string_list(meta.get("intent_refs"))
        if intent_id in refs:
            return True
    return False

def _is_intent_active_in_plan(state: RepoState, intent_id: str) -> bool:
    plan_path = _plan_path_from_config(state.config_raw)
    text = state.index.document_texts.get(plan_path)
    if text is None:
        text = read_text(state, plan_path)
    meta, _ = _split_front_matter(text)
    values = _collect_string_list(meta.get("active_intents"))
    return intent_id in values

def _fallback_plan_validation(state: RepoState) -> list[str]:
    errors: list[str] = []
    if not state.index.documents:
        errors.append(".context: no markdown documents found")
    ids = [doc.node_id for doc in state.index.documents if doc.node_id]
    if len(ids) != len(set(ids)):
        errors.append("duplicate id detected in index")
    return errors

def _collect_arch_nodes(state: RepoState, doc_type: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in state.index.documents:
        if doc.doc_type != doc_type:
            continue
        title = doc.metadata.get("title", "") if isinstance(doc.metadata, dict) else ""
        rows.append(
            {
                "id": doc.node_id or "",
                "path": doc.path,
                "title": title,
            }
        )
    rows.sort(key=lambda item: (str(item["path"]), str(item["id"])))
    return rows
