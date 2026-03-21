from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError, _required_str

from .intent_apply import plan_intent_apply
from .intent_pipeline import (
    plan_intent_autodesign,
    plan_intent_create_many,
    plan_intent_generate_tasks,
    plan_intent_propose,
)
from .intent_query import (
    plan_intent_index,
    plan_intent_list,
    plan_intent_validate,
    plan_intent_view,
)
from .intent_review import plan_intent_review_bundle
from .intent_submit import plan_intent_submit_many
from .intent_template import plan_intent_template


def _plan_intent_list(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    return plan_intent_list(state, args)


def _plan_intent_template(_state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    return plan_intent_template(args)


def _plan_intent_view(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    args = {"intent_id": _required_str(args, "intent_id")}
    return plan_intent_view(state, args)


def _plan_intent_index(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    args = {"intent_id": _required_str(args, "intent_id")}
    return plan_intent_index(state, args)


def _plan_intent_validate(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    args = {"intent_id": _required_str(args, "intent_id")}
    return plan_intent_validate(state, args)


def _plan_intent_propose(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = args.get("intent_id")
    if isinstance(intent_id, str) and intent_id.strip():
        return plan_intent_propose(state, {"intent_id": intent_id.strip()})

    intent_text = args.get("intent_text")
    if isinstance(intent_text, str) and intent_text.strip():
        payload: dict[str, Any] = {"intent_text": intent_text.strip()}
        title = args.get("title")
        if title is not None:
            if not isinstance(title, str) or not title.strip():
                raise ToolError(
                    "invalid_input",
                    "title must be a non-empty string when provided",
                    {"key": "title"},
                )
            payload["title"] = title.strip()
        return plan_intent_propose(state, payload)

    raise ToolError(
        "invalid_input",
        "either intent_id or intent_text must be provided",
        {"keys": ["intent_id", "intent_text"]},
    )


def _plan_intent_create_many(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intents = args.get("intents")
    if not isinstance(intents, list):
        raise ToolError("invalid_input", "intents must be an array", {"key": "intents"})
    payload: dict[str, Any] = {"intents": intents}
    plan_ref = args.get("plan_ref")
    if plan_ref is not None:
        if not isinstance(plan_ref, str):
            raise ToolError(
                "invalid_input", "plan_ref must be string", {"key": "plan_ref"}
            )
        payload["plan_ref"] = plan_ref
    return plan_intent_create_many(state, payload)


def _plan_intent_submit_many(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intents = args.get("intents")
    if not isinstance(intents, list):
        raise ToolError("invalid_input", "intents must be an array", {"key": "intents"})
    payload: dict[str, Any] = {"intents": intents}
    plan_ref = args.get("plan_ref")
    if plan_ref is not None:
        if not isinstance(plan_ref, str):
            raise ToolError(
                "invalid_input", "plan_ref must be string", {"key": "plan_ref"}
            )
        payload["plan_ref"] = plan_ref
    return plan_intent_submit_many(state, payload)


def _plan_intent_autodesign(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    args = {
        "intent_id": _required_str(args, "intent_id"),
        "proposal_fingerprint": _required_str(args, "proposal_fingerprint"),
    }
    return plan_intent_autodesign(state, args)


def _plan_intent_generate_tasks(
    state: RepoState, args: dict[str, Any]
) -> dict[str, Any]:
    args = {
        "intent_id": _required_str(args, "intent_id"),
        "design_fingerprint": _required_str(args, "design_fingerprint"),
    }
    return plan_intent_generate_tasks(state, args)


def _plan_intent_review_bundle(
    state: RepoState, args: dict[str, Any]
) -> dict[str, Any]:
    payload = {
        "intent_id": _required_str(args, "intent_id"),
        "proposal_fingerprint": _required_str(args, "proposal_fingerprint"),
        "design_fingerprint": _required_str(args, "design_fingerprint"),
        "taskset_fingerprint": _required_str(args, "taskset_fingerprint"),
        "retry_on_fail": args.get("retry_on_fail", 0),
    }
    return plan_intent_review_bundle(state, payload)


def _plan_intent_apply(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "intent_id": _required_str(args, "intent_id"),
        "decision_fingerprint": _required_str(args, "decision_fingerprint"),
        "approve": args.get("approve", False),
        "dry_run": args.get("dry_run", True),
    }
    return plan_intent_apply(state, payload)
