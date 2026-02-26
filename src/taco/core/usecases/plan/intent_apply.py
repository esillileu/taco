from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError

from .intent_helpers import apply_intent_bundle, plan_intent_apply_preview
from .intent_pipeline import build_intent_pipeline_bundle
from .intent_review import review_issues


def plan_intent_apply(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = str(args["intent_id"])
    decision_fingerprint = str(args["decision_fingerprint"])

    approve = args.get("approve", False)
    if not isinstance(approve, bool):
        raise ToolError("invalid_input", "approve must be boolean", {"key": "approve"})
    if not approve:
        raise ToolError(
            "approval_required",
            "explicit approval is required for apply",
            {"key": "approve"},
        )

    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})

    bundle = build_intent_pipeline_bundle(state, intent_id)
    if decision_fingerprint != bundle["decision_fingerprint"]:
        raise ToolError(
            "fingerprint_mismatch",
            "decision fingerprint mismatch",
            {
                "expected": bundle["decision_fingerprint"],
                "actual": decision_fingerprint,
                "stage": "decision",
            },
        )

    review = review_issues(
        state,
        bundle,
        proposal_fingerprint=bundle["proposal_fingerprint"],
        design_fingerprint=bundle["design_fingerprint"],
        taskset_fingerprint=bundle["taskset_fingerprint"],
    )
    if review:
        raise ToolError(
            "plan_review_failed",
            "review gate failed; apply is blocked",
            {"intent_id": intent_id, "issues": review},
        )

    preview = plan_intent_apply_preview(bundle)
    if dry_run:
        return {
            "intent_id": intent_id,
            "applied": False,
            "decision_fingerprint": bundle["decision_fingerprint"],
            "writes": preview,
        }

    apply_intent_bundle(state, bundle)
    return {
        "intent_id": intent_id,
        "applied": True,
        "decision_fingerprint": bundle["decision_fingerprint"],
        "writes": preview,
    }
