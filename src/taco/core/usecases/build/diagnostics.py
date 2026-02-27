from __future__ import annotations

from typing import Any


def build_drift_details(
    *,
    task_id: str,
    failed_rule: str,
    changed_paths: list[str],
    suggested_plan_actions: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "task_id": task_id,
        "failed_rule": failed_rule,
        "changed_paths_snapshot": changed_paths,
        "suggested_plan_actions": suggested_plan_actions
        or [
            "revise task scope and references in plan mode",
            "split task if scope exceeds allowed boundary",
            "rerun build loop after scope and output alignment",
        ],
    }
    if extra:
        details.update(extra)
    return details

