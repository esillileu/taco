from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError, _collect_string_list, _fingerprint

from .intent_helpers import (
    derive_generated_tasks,
    plan_path_from_state,
    tasks_dir_from_config,
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
    intent_id = str(args["intent_id"])
    bundle = build_intent_pipeline_bundle(state, intent_id)
    return {
        "intent": bundle["intent"],
        "proposal": bundle["proposal"],
        "proposal_fingerprint": bundle["proposal_fingerprint"],
        "gaps": bundle["gaps"],
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
        "generated_tasks": bundle["generated_tasks"],
        "taskset_fingerprint": bundle["taskset_fingerprint"],
    }
