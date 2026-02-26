from __future__ import annotations

from typing import Any

from taco.apps.cli.errors import CliError

from .build import map_build_action
from .doc import map_doc_action
from .plan import map_plan_action
from .task import map_task_action


def map_cli_to_tool(
    domain: str, action: str, options: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    if domain == "init":
        return "project.init", {}
    if domain == "task":
        return map_task_action(action, options)
    if domain == "doc":
        return map_doc_action(action, options)
    if domain == "issue" and action == "triage":
        title = options.get("title")
        if not isinstance(title, str) or not title.strip():
            raise CliError(
                "invalid_option", "title must be a non-empty string", {"key": "title"}
            )
        return "issue.triage", {"title": title.strip()}
    if domain == "convention" and action == "get":
        topic = options.get("topic")
        if not isinstance(topic, str) or not topic.strip():
            raise CliError(
                "invalid_option", "topic must be a non-empty string", {"key": "topic"}
            )
        return "convention.get", {"topic": topic.strip()}
    if domain == "plan":
        return map_plan_action(action, options)
    if domain == "build":
        return map_build_action(action, options)
    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": domain, "action": action},
    )
