from __future__ import annotations

from typing import Any

from taco.apps.cli.errors import CliError


def map_build_action(
    action: str, options: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    if action == "precheck":
        pack = options.get("pack")
        if not isinstance(pack, dict):
            raise CliError(
                "invalid_option",
                "pack must be an object",
                {"key": "pack"},
            )
        return "build.precheck", {"pack": pack}
    if action == "postcheck":
        pack = options.get("pack")
        if not isinstance(pack, dict):
            raise CliError(
                "invalid_option",
                "pack must be an object",
                {"key": "pack"},
            )
        payload: dict[str, Any] = {"pack": pack}
        for key in ("changed_paths", "produced_outputs", "check_results"):
            value = options.get(key)
            if value is not None:
                payload[key] = value
        return "build.postcheck", payload
    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": "build", "action": action},
    )
