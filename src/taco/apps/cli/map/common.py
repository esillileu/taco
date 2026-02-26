from __future__ import annotations

from typing import Any

from taco.apps.cli.errors import CliError, _required_str


def required_str_option(options: dict[str, Any], key: str) -> str:
    return _required_str(options, key)


def require_bool(value: Any, *, key: str, label: str) -> bool:
    if not isinstance(value, bool):
        raise CliError(
            "invalid_option",
            f"{label} must be boolean",
            {"key": key},
        )
    return value


def optional_dry_run(options: dict[str, Any], payload: dict[str, Any]) -> None:
    dry_run = options.get("dry_run")
    if dry_run is None:
        return
    payload["dry_run"] = require_bool(dry_run, key="dry_run", label="dry_run")


def optional_budget_tokens(options: dict[str, Any], payload: dict[str, Any]) -> None:
    budget_tokens = options.get("budget_tokens")
    if budget_tokens is None:
        return
    if not isinstance(budget_tokens, int):
        raise CliError(
            "invalid_option",
            "budget_tokens must be an integer",
            {"key": "budget_tokens"},
        )
    payload["budget_tokens"] = budget_tokens
