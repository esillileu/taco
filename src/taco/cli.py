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
        return "task.pack", {"task_id": _required_str(options, "task_id")}
    if domain == "task" and action == "targets":
        return "task.targets", {
            "task_id": _required_str(options, "task_id"),
            "route_type": _required_str(options, "route_type"),
        }
    if domain == "task" and action == "record":
        payload: dict[str, Any] = {
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
            payload["dry_run"] = dry_run
        return "task.record", payload
    if domain == "doc" and action == "snippet":
        return "doc.snippet", {
            "path": _required_str(options, "path"),
            "anchor_id": _required_str(options, "anchor_id"),
        }
    if domain == "issue" and action == "triage":
        return "issue.triage", {"title": _required_str(options, "title")}
    if domain == "convention" and action == "get":
        return "convention.get", {"topic": _required_str(options, "topic")}

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
