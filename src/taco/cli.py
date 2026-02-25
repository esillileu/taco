from __future__ import annotations

from typing import Any


class CliError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def map_cli_to_tool(
    domain: str, action: str, options: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    if domain == "task" and action == "list":
        return "task.list", {}
    if domain == "task" and action == "pack":
        payload: dict[str, Any] = {"task_id": _required_str(options, "task_id")}
        budget_tokens = options.get("budget_tokens")
        if budget_tokens is not None:
            if not isinstance(budget_tokens, int):
                raise CliError(
                    "invalid_option",
                    "budget_tokens must be an integer",
                    {"key": "budget_tokens"},
                )
            payload["budget_tokens"] = budget_tokens
        return "task.pack", payload
    if domain == "task" and action == "targets":
        return "task.targets", {
            "task_id": _required_str(options, "task_id"),
            "route_type": _required_str(options, "route_type"),
        }
    if domain == "task" and action == "record":
        record_payload: dict[str, Any] = {
            "task_id": _required_str(options, "task_id"),
            "route_type": _required_str(options, "route_type"),
            "content": _required_str(options, "content"),
        }
        dry_run = options.get("dry_run")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise CliError(
                    "invalid_option",
                    "dry_run must be boolean",
                    {"key": "dry_run"},
                )
            record_payload["dry_run"] = dry_run
        return "task.record", record_payload
    if domain == "task" and action == "complete":
        complete_payload: dict[str, Any] = {
            "task_id": _required_str(options, "task_id"),
            "implementation": _required_str(options, "implementation"),
            "verification": _required_str(options, "verification"),
        }
        dry_run = options.get("dry_run")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise CliError(
                    "invalid_option",
                    "dry_run must be boolean",
                    {"key": "dry_run"},
                )
            complete_payload["dry_run"] = dry_run
        return "task.complete", complete_payload
    if domain == "task" and action == "block":
        block_payload: dict[str, Any] = {
            "task_id": _required_str(options, "task_id"),
            "reason_code": _required_str(options, "reason_code"),
            "reason": _required_str(options, "reason"),
        }
        dry_run = options.get("dry_run")
        if dry_run is not None:
            if not isinstance(dry_run, bool):
                raise CliError(
                    "invalid_option",
                    "dry_run must be boolean",
                    {"key": "dry_run"},
                )
            block_payload["dry_run"] = dry_run
        return "task.block", block_payload
    if domain == "doc" and action == "snippet":
        return "doc.snippet", {
            "path": _required_str(options, "path"),
            "anchor_id": _required_str(options, "anchor_id"),
        }
    if domain == "issue" and action == "triage":
        return "issue.triage", {"title": _required_str(options, "title")}
    if domain == "convention" and action == "get":
        return "convention.get", {"topic": _required_str(options, "topic")}
    if domain == "plan" and action == "view":
        return "plan.view", {}
    if domain == "plan" and action == "locate":
        locate_payload: dict[str, Any] = {
            "change_type": _required_str(options, "change_type"),
        }
        target = options.get("target")
        if target is not None:
            if not isinstance(target, str):
                raise CliError(
                    "invalid_option",
                    "target must be a string",
                    {"key": "target"},
                )
            locate_payload["target"] = target.strip()
        return "plan.locate", locate_payload
    if domain == "plan" and action == "validate":
        return "plan.validate", {}

    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": domain, "action": action},
    )


def _required_str(options: dict[str, Any], key: str) -> str:
    value = options.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CliError(
            "invalid_option",
            f"{key} must be a non-empty string",
            {"key": key},
        )
    return value.strip()
