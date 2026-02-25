from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from taco.indexer import (
    IndexConfig,
    IndexGraph,
    build_index,
    load_documents,
    scan_markdown_files,
)
from taco.pack import BudgetConfig, PackError, build_task_pack
from taco.router import RouterConfig, RouterError, resolve_write_target


@dataclass(frozen=True)
class RepoState:
    root: Path
    config_raw: dict[str, Any]
    index: IndexGraph
    budget_config: BudgetConfig
    router_config: RouterConfig


class ToolError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def load_repo_state(root: Path, config_path: Path | None = None) -> RepoState:
    cfg_path = config_path or (root / "taco.yaml")
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ToolError("invalid_config", "top-level config must be a mapping", {})

    index_config = IndexConfig.from_dict(raw)
    budget_config = BudgetConfig.from_dict(raw)
    router_config = RouterConfig.from_dict(raw)

    markdown_paths = scan_markdown_files(root)
    rel_paths = [
        path.relative_to(root).as_posix()
        for path in markdown_paths
        if path.relative_to(root).as_posix().startswith("docs/")
    ]
    documents = load_documents(root, rel_paths)
    index = build_index(documents, index_config)

    return RepoState(
        root=root,
        config_raw=raw,
        index=index,
        budget_config=budget_config,
        router_config=router_config,
    )


def call_tool(state: RepoState, name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "task.list": _task_list,
        "task.pack": _task_pack,
        "task.targets": _task_targets,
        "task.record": _task_record,
        "doc.snippet": _doc_snippet,
        "issue.triage": _issue_triage,
        "convention.get": _convention_get,
    }
    handler = handlers.get(name)
    if handler is None:
        return _error("unknown_tool", "tool is not supported", {"tool": name})

    try:
        return _ok(handler(state, args))
    except (ToolError, PackError, RouterError) as exc:
        return _error(exc.code, str(exc), exc.details)


def _task_list(state: RepoState, _: dict[str, Any]) -> dict[str, Any]:
    items = [
        {"task_id": task_id, "path": path}
        for task_id, path in sorted(state.index.task_index.items())
    ]
    return {"tasks": items}


def _task_pack(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
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
        )
    result = build_task_pack(task_id, state.index, budget_config)
    return result.to_dict()


def _task_targets(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    route_type = _required_str(args, "route_type")
    target = resolve_write_target(task_id, route_type, state.index, state.router_config)
    return target.to_dict()


def _task_record(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    route_type = _required_str(args, "route_type")
    content = _required_str(args, "content")
    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})

    target = resolve_write_target(task_id, route_type, state.index, state.router_config)
    if dry_run:
        return {
            "target": target.to_dict(),
            "applied": False,
            "preview": f"- {content}",
        }

    path = state.root / target.path
    original = path.read_text(encoding="utf-8")
    updated = _append_under_heading(original, target.heading, f"- {content}")
    path.write_text(updated, encoding="utf-8")
    return {
        "target": target.to_dict(),
        "applied": True,
        "path": target.path,
    }


def _doc_snippet(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    path = _required_str(args, "path")
    anchor_id = _required_str(args, "anchor_id")
    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None:
        raise ToolError("doc_not_found", "document was not found", {"path": path})

    heading = next((item for item in doc.headings if item.anchor_id == anchor_id), None)
    if heading is None:
        raise ToolError(
            "anchor_not_found",
            "anchor was not found in document",
            {"path": path, "anchor_id": anchor_id},
        )

    text = state.index.document_texts[path]
    snippet = _slice_text(text, heading.start_line, heading.end_line)
    return {
        "path": path,
        "anchor_id": anchor_id,
        "heading": heading.heading,
        "snippet": snippet,
    }


def _issue_triage(_: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    title = _required_str(args, "title")
    lowered = title.lower()
    if any(token in lowered for token in ("bug", "fix", "error", "broken")):
        issue_type = "Fix"
    elif any(token in lowered for token in ("docs", "document", "readme")):
        issue_type = "Docs"
    elif any(token in lowered for token in ("test", "coverage")):
        issue_type = "Test"
    else:
        issue_type = "Feat"
    return {"type": issue_type, "normalized_title": f"[{issue_type}] {title.strip()}"}


def _convention_get(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    topic = _required_str(args, "topic")
    if topic != "git":
        raise ToolError(
            "unknown_topic",
            "unsupported convention topic",
            {"topic": topic},
        )
    modules = state.config_raw.get("modules", {})
    if isinstance(modules, dict):
        git_cfg = modules.get("git", {})
    else:
        git_cfg = {}
    if isinstance(git_cfg, dict):
        git_path = git_cfg.get("path", "docs/dev/git.md")
    else:
        git_path = "docs/dev/git.md"
    return {
        "topic": "git",
        "path": git_path,
    }


def _append_under_heading(markdown_text: str, heading: str, line: str) -> str:
    lines = markdown_text.splitlines()
    marker = f"## {heading}"
    heading_idx = -1
    for idx, raw in enumerate(lines):
        if raw.strip() == marker:
            heading_idx = idx
            break
    if heading_idx < 0:
        raise ToolError(
            "target_heading_not_found",
            "target heading missing",
            {"heading": heading},
        )

    insert_idx = len(lines)
    for idx in range(heading_idx + 1, len(lines)):
        if lines[idx].startswith("## "):
            insert_idx = idx
            break
    next_lines = lines[:insert_idx] + [line] + lines[insert_idx:]
    return "\n".join(next_lines) + "\n"


def _slice_text(text: str, start_line: int, end_line: int) -> str:
    lines = text.splitlines()
    start = max(start_line - 1, 0)
    end = min(end_line, len(lines))
    return "\n".join(lines[start:end]).strip()


def _required_str(args: dict[str, Any], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolError(
            "invalid_input",
            f"{key} must be a non-empty string",
            {"key": key},
        )
    return value.strip()


def _ok(data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "data": data}


def _error(code: str, message: str, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
