from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, _required_str

from .intent_apply import plan_intent_apply
from .intent_pipeline import (
    plan_intent_autodesign,
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


def _plan_intent_list(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    return plan_intent_list(state, args)


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
    args = {"intent_id": _required_str(args, "intent_id")}
    return plan_intent_propose(state, args)


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
