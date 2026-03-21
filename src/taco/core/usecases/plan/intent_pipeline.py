from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError, _collect_string_list, _fingerprint

from .intent_helpers import (
    derive_generated_tasks,
    plan_path_from_state,
    tasks_dir_from_config,
)
from .intent_intake import (
    create_many_intents,
    ingest_natural_language_intent,
    rebuild_state_index,
)
from .intent_query import plan_intent_index


def build_intent_pipeline_bundle(state: RepoState, intent_id: str) -> dict[str, Any]:
    indexed = plan_intent_index(state, {"intent_id": intent_id})
    intent = indexed["intent"]
    intent_path = str(intent.get("path", ""))
    if not intent_path:
        raise ToolError(
            "intent_not_found", "intent path is missing", {"intent_id": intent_id}
        )

    task_refs = _collect_string_list(intent.get("task_refs"))
    links = _collect_string_list(intent.get("links"))
    gaps = [str(item) for item in indexed.get("gaps", []) if isinstance(item, str)]

    proposal_fingerprint = _fingerprint(
        [intent_id, *task_refs, *gaps, str(indexed.get("decision_fingerprint", ""))]
    )

    plan_path = plan_path_from_state(state)
    tasks_dir = tasks_dir_from_config(state)
    design_updates = [
        {
            "path": intent_path,
            "kind": "intent",
            "operation": "sync_task_refs_and_links",
        },
        {"path": plan_path, "kind": "plan", "operation": "promote_generated_tasks"},
    ]
    design_fingerprint = _fingerprint(
        [proposal_fingerprint, plan_path, tasks_dir, *gaps]
    )

    generated_tasks = derive_generated_tasks(
        state=state,
        intent_id=intent_id,
        intent=intent,
        links=links,
        task_refs=task_refs,
        gaps=gaps,
        tasks_dir=tasks_dir,
    )
    taskset_fingerprint = _fingerprint(
        [
            design_fingerprint,
            *[row["task_id"] for row in generated_tasks],
            *[row["path"] for row in generated_tasks],
        ]
    )
    decision_fingerprint = _fingerprint(
        [proposal_fingerprint, design_fingerprint, taskset_fingerprint]
    )

    intent_text = state.index.document_texts.get(intent_path, "")

    return {
        "intent": intent,
        "intent_path": intent_path,
        "intent_text": intent_text,
        "task_refs": task_refs,
        "proposal": {
            "intent_id": intent_id,
            "intent_path": intent_path,
            "plan_path": plan_path,
            "tasks_dir": tasks_dir,
            "gaps": gaps,
        },
        "gaps": gaps,
        "design_updates": design_updates,
        "generated_tasks": generated_tasks,
        "proposal_fingerprint": proposal_fingerprint,
        "design_fingerprint": design_fingerprint,
        "taskset_fingerprint": taskset_fingerprint,
        "decision_fingerprint": decision_fingerprint,
    }


def plan_intent_propose(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_text = args.get("intent_text")
    if isinstance(intent_text, str) and intent_text.strip():
        title = args.get("title")
        if title is not None and not isinstance(title, str):
            raise ToolError(
                "invalid_input", "title must be a string", {"key": "title"}
            )
        created = ingest_natural_language_intent(
            state,
            intent_text=intent_text,
            title=title if isinstance(title, str) else None,
        )
        refreshed = rebuild_state_index(state)
        bundle = build_intent_pipeline_bundle(refreshed, created["intent_id"])
        return {
            "created_intent": True,
            "intent": bundle["intent"],
            "proposal": bundle["proposal"],
            "proposal_fingerprint": bundle["proposal_fingerprint"],
            "gaps": bundle["gaps"],
            "deprecation": {
                "code": "intent_text_propose_deprecated",
                "message": (
                    "Use plan.intent.template + plan.intent.create_many for natural "
                    "language decomposition before propose."
                ),
            },
        }

    intent_id = str(args["intent_id"])
    try:
        bundle = build_intent_pipeline_bundle(state, intent_id)
    except ToolError as exc:
        if exc.code != "intent_not_found":
            raise
        refreshed = rebuild_state_index(state)
        bundle = build_intent_pipeline_bundle(refreshed, intent_id)
    return {
        "created_intent": False,
        "intent": bundle["intent"],
        "proposal": bundle["proposal"],
        "proposal_fingerprint": bundle["proposal_fingerprint"],
        "gaps": bundle["gaps"],
    }


def plan_intent_create_many(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    result = create_many_intents(state, args)
    refreshed = rebuild_state_index(state)
    created = result.get("created", [])
    mapped: list[dict[str, Any]] = []
    if isinstance(created, list):
        for row in created:
            if not isinstance(row, dict):
                continue
            intent_id = str(row.get("intent_id", "")).strip()
            if not intent_id:
                continue
            indexed = plan_intent_index(refreshed, {"intent_id": intent_id})
            mapped.append(
                {
                    "intent_id": intent_id,
                    "path": str(row.get("path", "")),
                    "title": str(row.get("title", "")),
                    "fingerprint": str(row.get("fingerprint", "")),
                    "intent": indexed.get("intent", {}),
                }
            )
    return {
        "created": mapped,
        "count": int(result.get("count", 0)),
        "warnings": result.get("warnings", []),
    }


def plan_intent_autodesign(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = str(args["intent_id"])
    proposal_fingerprint = str(args["proposal_fingerprint"])
    bundle = build_intent_pipeline_bundle(state, intent_id)
    if proposal_fingerprint != bundle["proposal_fingerprint"]:
        raise ToolError(
            "fingerprint_mismatch",
            "proposal fingerprint mismatch",
            {
                "expected": bundle["proposal_fingerprint"],
                "actual": proposal_fingerprint,
                "stage": "proposal",
            },
        )
    return {
        "intent_id": intent_id,
        "design_updates": bundle["design_updates"],
        "design_fingerprint": bundle["design_fingerprint"],
    }


def plan_intent_generate_tasks(
    state: RepoState, args: dict[str, Any]
) -> dict[str, Any]:
    intent_id = str(args["intent_id"])
    design_fingerprint = str(args["design_fingerprint"])
    bundle = build_intent_pipeline_bundle(state, intent_id)
    if design_fingerprint != bundle["design_fingerprint"]:
        raise ToolError(
            "fingerprint_mismatch",
            "design fingerprint mismatch",
            {
                "expected": bundle["design_fingerprint"],
                "actual": design_fingerprint,
                "stage": "design",
            },
        )
    return {
        "intent_id": intent_id,
        "authoring_required": True,
        "generated_tasks": bundle["generated_tasks"],
        "taskset_fingerprint": bundle["taskset_fingerprint"],
        "next_action": {"tool": "plan.task.template"},
    }
