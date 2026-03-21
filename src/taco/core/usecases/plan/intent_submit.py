from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState

from .intent_pipeline import plan_intent_create_many
from .stage_state import set_plan_stage


def plan_intent_submit_many(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    result = plan_intent_create_many(state, args)
    set_plan_stage(state, "design_change")
    return {
        **result,
        "stage_transition": "design_change",
        "next_action": {"tool": "plan.mode.guide", "args": {"stage": "design_change"}},
    }
