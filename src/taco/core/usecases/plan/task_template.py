from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError

from .intent_pipeline import build_intent_pipeline_bundle
from .task_contract import REQUIRED_HEADINGS


def _select_blueprint(bundle: dict[str, Any], task_id: str | None) -> dict[str, Any]:
    generated = bundle.get("generated_tasks")
    if not isinstance(generated, list) or not generated:
        raise ToolError(
            "task_blueprint_missing",
            "no generated task blueprint found for intent",
            {"intent_id": bundle.get("intent", {}).get("id", "")},
        )
    if task_id:
        for row in generated:
            if not isinstance(row, dict):
                continue
            if str(row.get("task_id", "")).strip() == task_id:
                return row
        raise ToolError(
            "task_blueprint_not_found",
            "task_id not found in generated blueprints",
            {"task_id": task_id},
        )
    return generated[0]


def plan_task_template(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = str(args.get("intent_id", "")).strip()
    if not intent_id:
        raise ToolError("invalid_input", "intent_id is required", {"key": "intent_id"})
    task_id_raw = args.get("task_id")
    task_id = str(task_id_raw).strip() if isinstance(task_id_raw, str) else None

    bundle = build_intent_pipeline_bundle(state, intent_id)
    blueprint = _select_blueprint(bundle, task_id)

    return {
        "intent_id": intent_id,
        "authoring_required": True,
        "task_blueprint": blueprint,
        "front_matter_template": blueprint.get("front_matter_requirements", {}),
        "required_sections": list(REQUIRED_HEADINGS),
        "lint_rules": [
            "all required sections must exist",
            "implementation and verification sections need at least 2 non-empty lines",
            "scope.out must include at least one non-goal",
            "implementation section should include boundary rationale terms",
            "verification section should include executable command/condition terms",
        ],
        "next_action": {
            "tool": "plan.task.frontmatter.sync",
            "then": "plan.task.lint",
        },
    }
