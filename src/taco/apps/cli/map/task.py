from __future__ import annotations

from typing import Any

from taco.apps.cli.errors import CliError

from .common import optional_budget_tokens, optional_dry_run, required_str_option


def map_task_action(action: str, options: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if action == "list":
        return "task.list", {}
    if action == "pack":
        payload: dict[str, Any] = {}
        task_id = options.get("task_id")
        if task_id is not None:
            if not isinstance(task_id, str) or not task_id.strip():
                raise CliError(
                    "invalid_option",
                    "task_id must be a non-empty string",
                    {"key": "task_id"},
                )
            payload["task_id"] = task_id.strip()
        optional_budget_tokens(options, payload)
        return "task.pack", payload
    if action == "targets":
        return "task.targets", {
            "task_id": required_str_option(options, "task_id"),
            "route_type": required_str_option(options, "route_type"),
        }
    if action == "record":
        payload: dict[str, Any] = {
            "task_id": required_str_option(options, "task_id"),
            "route_type": required_str_option(options, "route_type"),
            "content": required_str_option(options, "content"),
        }
        optional_dry_run(options, payload)
        return "task.record", payload
    if action == "complete":
        payload: dict[str, Any] = {
            "task_id": required_str_option(options, "task_id"),
            "implementation": required_str_option(options, "implementation"),
            "verification": required_str_option(options, "verification"),
        }
        optional_dry_run(options, payload)
        return "task.complete", payload
    if action == "block":
        payload: dict[str, Any] = {
            "task_id": required_str_option(options, "task_id"),
            "reason_code": required_str_option(options, "reason_code"),
            "reason": required_str_option(options, "reason"),
        }
        optional_dry_run(options, payload)
        return "task.block", payload
    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": "task", "action": action},
    )
