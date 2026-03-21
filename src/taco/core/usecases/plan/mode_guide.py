from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState

from .stage_state import current_plan_stage


def plan_mode_guide(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    stage = args.get("stage")
    stage_value = str(stage).strip().lower() if isinstance(stage, str) else ""
    if stage_value not in {"intent_decomposition", "design_change", "task_authoring"}:
        stage_value = current_plan_stage(state)

    common = {
        "policy": "hard_fail",
        "authoring_model": "agent_submits_taco_formats_and_applies",
        "allowed_stages": ["intent_decomposition", "design_change", "task_authoring"],
    }
    if stage_value == "intent_decomposition":
        return {
            **common,
            "current_stage": stage_value,
            "instructions": [
                "Call plan.intent.template and read required fields.",
                "Decompose user design into multiple intents (minimum 2).",
                "Submit with plan.intent.submit_many.",
            ],
            "required_fields": ["title", "intent", "scope_in", "scope_out"],
            "next_action": {"tool": "plan.intent.submit_many"},
        }
    if stage_value == "design_change":
        return {
            **common,
            "current_stage": stage_value,
            "instructions": [
                "Use plan.intent.index/propose outputs to identify impacted docs.",
                (
                    "Prepare section-level content updates for "
                    "architecture/plan/intent docs."
                ),
                (
                    "Submit changes with base fingerprints using "
                    "plan.design.submit_changes."
                ),
            ],
            "required_fields": ["path", "section_id", "content", "base_fingerprint"],
            "next_action": {"tool": "plan.design.submit_changes"},
        }
    return {
        **common,
        "current_stage": stage_value,
        "instructions": [
            "Call plan.task.template to get front matter + section requirements.",
            "Agent authors task body, then run plan.task.frontmatter.sync.",
            "Run plan.task.lint until valid, then execute review/apply chain.",
        ],
        "required_fields": ["intent_id", "path", "front_matter", "required_sections"],
        "next_action": {"tool": "plan.task.template"},
    }
