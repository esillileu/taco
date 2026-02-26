from __future__ import annotations

from typing import Any

from taco.core.packing import BudgetConfig, build_task_pack
from taco.core.plan import RepoState, ToolError, _required_str


def plan_pack(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    return pack_with_refs(state, args, task_id, "plan.pack")


def pack_with_refs(
    state: RepoState,
    args: dict[str, Any],
    task_id: str,
    tool_name: str,
) -> dict[str, Any]:
    budget_tokens = args.get("budget_tokens")
    budget_config = state.budget_config
    if budget_tokens is not None:
        if not isinstance(budget_tokens, int):
            raise ToolError(
                "invalid_input",
                "budget_tokens must be an integer",
                {"key": "budget_tokens"},
            )
        budget_config = BudgetConfig(
            default_tokens=budget_tokens,
            priority_order=state.budget_config.priority_order,
            required_groups=state.budget_config.required_groups,
        )

    result = build_task_pack(
        task_id,
        state.index,
        budget_config,
        common_required_refs=state.required_refs_by_tool.get(tool_name, ()),
    )
    return result.to_dict()
