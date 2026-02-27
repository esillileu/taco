from __future__ import annotations

import re
from typing import Any

from taco.core.plan import RepoState, ToolError, _required_str


def _issue_triage(_: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    title = _required_str(args, "title")
    issue_type = _classify_issue_type(title)
    return {
        "title": title,
        "type": issue_type,
    }


def _convention_get(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    topic = _required_str(args, "topic")
    modules = state.config_raw.get("modules")
    if not isinstance(modules, dict):
        raise ToolError(
            "module_not_found",
            "config.modules is missing",
            {"topic": topic},
        )
    entry = modules.get(topic)
    if not isinstance(entry, dict):
        raise ToolError(
            "module_not_found",
            "convention topic is not configured",
            {"topic": topic},
        )
    path = entry.get("path")
    if not isinstance(path, str) or not path.strip():
        raise ToolError(
            "invalid_config",
            "module path must be a non-empty string",
            {"topic": topic},
        )
    return {"topic": topic, "path": path.strip()}


def _classify_issue_type(title: str) -> str:
    normalized = title.strip().lower()
    if re.search(r"\b(fix|bug|error|fail|broken|regression)\b", normalized):
        return "Fix"
    if re.search(r"\b(refactor|cleanup|split|modular|srp)\b", normalized):
        return "Refactor"
    if re.search(r"\b(doc|readme|guide|spec)\b", normalized):
        return "Docs"
    return "Task"

