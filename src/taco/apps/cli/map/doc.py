from __future__ import annotations

from typing import Any

from taco.apps.cli.errors import CliError

from .common import optional_dry_run, required_str_option


def map_doc_action(action: str, options: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if action == "snippet":
        return "doc.snippet", {
            "path": required_str_option(options, "path"),
            "anchor_id": required_str_option(options, "anchor_id"),
        }
    if action == "section.get":
        return "doc.section.get", {
            "path": required_str_option(options, "path"),
            "section_id": required_str_option(options, "section_id"),
        }
    if action == "section.patch":
        payload: dict[str, Any] = {
            "path": required_str_option(options, "path"),
            "section_id": required_str_option(options, "section_id"),
            "base_fingerprint": required_str_option(options, "base_fingerprint"),
        }
        ops = options.get("ops")
        if not isinstance(ops, list):
            raise CliError(
                "invalid_option",
                "ops must be a list",
                {"key": "ops"},
            )
        payload["ops"] = ops
        optional_dry_run(options, payload)
        return "doc.section.patch", payload
    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": "doc", "action": action},
    )
