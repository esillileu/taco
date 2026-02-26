from __future__ import annotations

from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _collect_string_list,
    _fingerprint,
    _intent_design_impact,
    _intent_kind,
    _placeholder_markers_in_text,
)
from taco.core.usecases.plan.refactor_support import _build_refactor_analysis
from taco.core.usecases.plan.support import (
    _collect_arch_nodes,
    _has_flow_intent_ref,
    _intent_candidate_tasks,
    _intent_coverage,
    _is_intent_active_in_plan,
)


def load_intent_doc(state: RepoState, intent_id: str) -> tuple[str, dict[str, Any]]:
    path = state.index.node_index.get(intent_id)
    if not path:
        raise ToolError(
            "intent_not_found", "intent id not found in index", {"intent_id": intent_id}
        )
    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None or doc.doc_type != "intent":
        raise ToolError(
            "intent_not_found",
            "intent id is not mapped to an intent document",
            {"intent_id": intent_id, "path": path},
        )
    meta = doc.metadata if isinstance(doc.metadata, dict) else {}
    return path, meta


def build_intent_payload(
    intent_id: str, path: str, meta: dict[str, Any]
) -> dict[str, Any]:
    return {
        "id": intent_id,
        "path": path,
        "title": str(meta.get("title", "")),
        "status": str(meta.get("status", "")),
        "kind": _intent_kind(meta),
        "design_impact": _intent_design_impact(meta),
        "plan_ref": str(meta.get("plan_ref", "")),
        "task_refs": _collect_string_list(meta.get("task_refs")),
        "links": _collect_string_list(meta.get("links")),
    }


def plan_intent_list(state: RepoState, _args: dict[str, Any]) -> dict[str, Any]:
    intents = _collect_arch_nodes(state, "intent")
    return {"intents": intents, "count": len(intents)}


def plan_intent_view(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = str(args["intent_id"])
    path, meta = load_intent_doc(state, intent_id)
    return {"intent": build_intent_payload(intent_id, path, meta)}


def plan_intent_index(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = str(args["intent_id"])
    path, meta = load_intent_doc(state, intent_id)
    payload = build_intent_payload(intent_id, path, meta)

    task_refs = payload["task_refs"]
    kind = payload["kind"]
    design_impact = payload["design_impact"]
    refactor_analysis = _build_refactor_analysis(
        state=state,
        intent_id=intent_id,
        intent_path=path,
        kind=kind,
        design_impact=design_impact,
    )

    existing_refs = [
        task_id for task_id in task_refs if task_id in state.index.task_index
    ]
    coverage = _intent_coverage(existing_refs, state)
    candidate_tasks = _intent_candidate_tasks(existing_refs, state)

    gaps: list[str] = []
    if not task_refs:
        gaps.append("intent.task_refs_missing")
    if task_refs and not existing_refs:
        gaps.append("intent.no_existing_task_refs")
    if existing_refs and not coverage["modules"]:
        gaps.append("coverage.modules_missing")
    if existing_refs and not coverage["flows"]:
        gaps.append("coverage.flows_missing")
    if existing_refs and not coverage["schemas"]:
        gaps.append("coverage.schemas_missing")
    if not _has_flow_intent_ref(state, intent_id):
        gaps.append("flow_missing_intent_ref")
    if not _is_intent_active_in_plan(state, intent_id):
        gaps.append("plan_queue_mismatch")

    decision_fingerprint = _fingerprint(
        [
            intent_id,
            *task_refs,
            *[item["id"] for item in coverage["modules"]],
            *[item["id"] for item in coverage["flows"]],
            *[item["id"] for item in coverage["schemas"]],
            *gaps,
            str(refactor_analysis.get("completed", False)),
            str(refactor_analysis.get("max_file_lines", 0)),
            str(refactor_analysis.get("oversized_file_count", 0)),
        ]
    )

    return {
        "intent": payload,
        "analysis": refactor_analysis,
        "coverage": coverage,
        "candidate_tasks": candidate_tasks,
        "gaps": gaps,
        "required_refs_used": list(
            state.required_refs_by_tool.get("plan.intent.index", ())
        ),
        "decision_fingerprint": decision_fingerprint,
    }


def plan_intent_validate(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    indexed = plan_intent_index(state, args)
    intent = indexed["intent"]
    path = str(intent.get("path", ""))
    text = state.index.document_texts.get(path, "")

    issues: list[dict[str, Any]] = []
    for key in ("id", "title", "status", "plan_ref"):
        value = intent.get(key)
        if not isinstance(value, str) or not value.strip():
            issues.append({"code": "missing_required_fields", "field": key})

    refs = intent.get("task_refs", [])
    if not isinstance(refs, list):
        issues.append({"code": "missing_required_fields", "field": "task_refs"})

    unresolved = [
        gap
        for gap in indexed.get("gaps", [])
        if gap in {"intent.no_existing_task_refs"}
    ]
    if unresolved:
        issues.append({"code": "unresolved_references", "items": unresolved})

    markers = _placeholder_markers_in_text(text)
    if markers:
        issues.append({"code": "placeholder_detected", "markers": markers})

    if issues:
        raise ToolError(
            "intent_validation_failed",
            "intent document did not satisfy validation rules",
            {"intent_id": intent.get("id", ""), "issues": issues},
        )

    return {
        "intent_id": intent["id"],
        "valid": True,
        "checked_rules": [
            "required_fields",
            "reference_integrity",
            "placeholder_policy",
        ],
    }
