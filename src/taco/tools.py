from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from posixpath import dirname, relpath
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
    common_required_refs: tuple[str, ...]
    task_required_headings: tuple[str, ...] = ()


BLOCK_REASON_CODES = (
    "architecture_change_required",
    "scope_split_required",
    "verification_ambiguous",
    "dependency_out_of_scope",
)


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
    prefixes = _collect_doc_prefixes(raw)
    rel_paths = [
        path.relative_to(root).as_posix()
        for path in markdown_paths
        if _should_include_path(path.relative_to(root).as_posix(), prefixes)
    ]
    documents = load_documents(root, rel_paths)
    index = build_index(documents, index_config)

    return RepoState(
        root=root,
        config_raw=raw,
        index=index,
        budget_config=budget_config,
        router_config=router_config,
        common_required_refs=_load_common_required_refs(raw),
        task_required_headings=_load_task_required_headings(raw),
    )


def call_tool(state: RepoState, name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "task.list": _task_list,
        "task.pack": _task_pack,
        "task.targets": _task_targets,
        "task.record": _task_record,
        "task.complete": _task_complete,
        "task.block": _task_block,
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
    _ensure_task_readiness_for_pack(state, task_id)
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
            required_groups=state.budget_config.required_groups,
        )
    result = build_task_pack(
        task_id,
        state.index,
        budget_config,
        common_required_refs=state.common_required_refs,
    )
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


def _task_complete(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    implementation = _required_str(args, "implementation")
    verification = _required_str(args, "verification")
    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})

    task_path = state.index.task_index.get(task_id)
    if not task_path:
        raise ToolError(
            "task_not_found",
            "task id not found in index",
            {"task_id": task_id},
        )

    task_file = state.root / task_path
    task_text = task_file.read_text(encoding="utf-8")
    task_meta, _ = _split_front_matter(task_text)
    status = task_meta.get("status")
    if isinstance(status, str) and status.strip() == "done":
        raise ToolError(
            "task_already_done",
            "task is already marked done",
            {"task_id": task_id},
        )

    implementation_target = resolve_write_target(
        task_id, "implementation", state.index, state.router_config
    )
    verification_target = resolve_write_target(
        task_id, "verification", state.index, state.router_config
    )

    updated_task = _append_under_heading(
        task_text, implementation_target.heading, f"- {implementation}"
    )
    updated_task = _append_under_heading(
        updated_task, verification_target.heading, f"- {verification}"
    )
    updated_task = _set_front_matter_key(updated_task, "status", "done")

    plan_path = _plan_path_from_config(state.config_raw)
    plan_file = state.root / plan_path
    plan_text = plan_file.read_text(encoding="utf-8")
    updated_plan, promoted = _advance_plan_for_completed_task(
        plan_text,
        completed_task_id=task_id,
        task_index=state.index.task_index,
        plan_path=plan_path,
    )

    if dry_run:
        return {
            "task_id": task_id,
            "applied": False,
            "status_from": status if isinstance(status, str) else "unknown",
            "status_to": "done",
            "next_active_task": promoted,
            "task_target": task_path,
            "plan_target": plan_path,
            "task_preview": _preview_change(task_text, updated_task),
            "plan_preview": _preview_change(plan_text, updated_plan),
            "targets": {
                "implementation": implementation_target.to_dict(),
                "verification": verification_target.to_dict(),
            },
        }

    task_file.write_text(updated_task, encoding="utf-8")
    plan_file.write_text(updated_plan, encoding="utf-8")
    return {
        "task_id": task_id,
        "applied": True,
        "status_from": status if isinstance(status, str) else "unknown",
        "status_to": "done",
        "next_active_task": promoted,
        "task_target": task_path,
        "plan_target": plan_path,
        "targets": {
            "implementation": implementation_target.to_dict(),
            "verification": verification_target.to_dict(),
        },
    }


def _task_block(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    reason_code = _required_str(args, "reason_code")
    reason = _required_str(args, "reason")
    dry_run = args.get("dry_run", True)
    if not isinstance(dry_run, bool):
        raise ToolError("invalid_input", "dry_run must be boolean", {"key": "dry_run"})
    if reason_code not in BLOCK_REASON_CODES:
        raise ToolError(
            "invalid_reason_code",
            "reason_code is not supported",
            {"reason_code": reason_code},
        )

    task_path = state.index.task_index.get(task_id)
    if not task_path:
        raise ToolError(
            "task_not_found",
            "task id not found in index",
            {"task_id": task_id},
        )

    task_file = state.root / task_path
    task_text = task_file.read_text(encoding="utf-8")
    task_meta, _ = _split_front_matter(task_text)
    status = task_meta.get("status")
    if isinstance(status, str) and status.strip() == "done":
        raise ToolError(
            "task_state_conflict",
            "done task cannot be blocked",
            {"task_id": task_id, "status": "done"},
        )
    if isinstance(status, str) and status.strip() == "blocked":
        raise ToolError(
            "task_already_blocked",
            "task is already marked blocked",
            {"task_id": task_id},
        )

    implementation_target = resolve_write_target(
        task_id, "implementation", state.index, state.router_config
    )
    updated_task = _append_under_heading(
        task_text,
        implementation_target.heading,
        f"- blocked: [{reason_code}] {reason}",
    )
    updated_task = _set_front_matter_key(updated_task, "status", "blocked")

    plan_path = _plan_path_from_config(state.config_raw)
    plan_file = state.root / plan_path
    plan_text = plan_file.read_text(encoding="utf-8")
    updated_plan, promoted = _advance_plan_for_blocked_task(
        plan_text,
        blocked_task_id=task_id,
        task_index=state.index.task_index,
        plan_path=plan_path,
    )

    if dry_run:
        return {
            "task_id": task_id,
            "applied": False,
            "reason_code": reason_code,
            "reason": reason,
            "status_from": status if isinstance(status, str) else "unknown",
            "status_to": "blocked",
            "next_active_task": promoted,
            "task_target": task_path,
            "plan_target": plan_path,
            "task_preview": _preview_change(task_text, updated_task),
            "plan_preview": _preview_change(plan_text, updated_plan),
        }

    task_file.write_text(updated_task, encoding="utf-8")
    plan_file.write_text(updated_plan, encoding="utf-8")
    return {
        "task_id": task_id,
        "applied": True,
        "reason_code": reason_code,
        "reason": reason,
        "status_from": status if isinstance(status, str) else "unknown",
        "status_to": "blocked",
        "next_active_task": promoted,
        "task_target": task_path,
        "plan_target": plan_path,
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
        git_path = git_cfg.get("path", ".context/governance/git/index.md")
    else:
        git_path = ".context/governance/git/index.md"
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


def _load_common_required_refs(raw: dict[str, Any]) -> tuple[str, ...]:
    pack = raw.get("pack", {})
    if not isinstance(pack, dict):
        return ()
    values = pack.get("common_required_refs", [])
    if not isinstance(values, list):
        return ()
    ref_ids: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if value and value not in ref_ids:
            ref_ids.append(value)
    return tuple(ref_ids)


def _load_task_required_headings(raw: dict[str, Any]) -> tuple[str, ...]:
    defaults = (
        "Intent",
        "Goal",
        "Scope",
        "Implementation Approach",
        "Verification Approach",
        "Implementation Result",
        "Verification Result",
    )
    parsing = raw.get("parsing", {})
    if not isinstance(parsing, dict):
        return defaults
    values = parsing.get("task_required_headings")
    if not isinstance(values, list):
        return defaults
    headings: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        heading = item.strip()
        if heading and heading not in headings:
            headings.append(heading)
    if not headings:
        return defaults
    return tuple(headings)


def _ensure_task_readiness_for_pack(state: RepoState, task_id: str) -> None:
    task_path = state.index.task_index.get(task_id)
    if not task_path:
        raise ToolError(
            "task_not_found",
            "task id not found in index",
            {"task_id": task_id},
        )
    task_doc = next(
        (doc for doc in state.index.documents if doc.path == task_path), None
    )
    if task_doc is None:
        raise ToolError(
            "task_doc_missing",
            "task document missing from indexed docs",
            {"task_id": task_id, "path": task_path},
        )
    text = state.index.document_texts.get(task_path, "")
    meta, _ = _split_front_matter(text)

    missing: list[str] = []
    if not meta:
        missing.append("front_matter")
    else:
        scope = meta.get("scope")
        if not isinstance(scope, dict):
            missing.append("scope")
        else:
            for key in ("in", "out"):
                value = scope.get(key)
                if not isinstance(value, list):
                    missing.append(f"scope.{key}")

        references = meta.get("references")
        if not isinstance(references, dict):
            missing.append("references")
        else:
            for key in ("modules", "flows", "schemas"):
                value = references.get(key)
                if not isinstance(value, list):
                    missing.append(f"references.{key}")
                    continue
                values = [item.strip() for item in value if isinstance(item, str)]
                if not values:
                    missing.append(f"references.{key}")

    required = state.task_required_headings
    seen_headings = {heading.heading for heading in task_doc.headings}
    for heading in required:
        if heading not in seen_headings:
            missing.append(f"heading:{heading}")

    if (
        "heading:Verification Approach" not in missing
        and not _has_verification_criteria(task_doc, text)
    ):
        missing.append("verification.criteria")

    if missing:
        deduped = list(dict.fromkeys(missing))
        raise ToolError(
            "task_not_ready",
            "task is not ready for pack execution",
            {
                "task_id": task_id,
                "missing_requirements": ",".join(deduped),
            },
        )


def _has_verification_criteria(doc: Any, text: str) -> bool:
    heading = next(
        (item for item in doc.headings if item.heading == "Verification Approach"),
        None,
    )
    if heading is None:
        return False
    lines = text.splitlines()
    start = max(heading.start_line, 0)
    end = min(heading.end_line, len(lines))
    body = lines[start:end]
    for raw in body:
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            continue
        if stripped.lower() in {"pending", "pending definition.", "tbd"}:
            continue
        if stripped.startswith("- "):
            return True
        if re.match(r"^\d+\.\s+\S", stripped):
            return True
        if "`" in stripped:
            return True
    return False


def _collect_doc_prefixes(raw: dict[str, Any]) -> tuple[str, ...]:
    docs = raw.get("docs", {})
    if not isinstance(docs, dict):
        return (".context/",)

    raw_paths: list[str] = []
    for key in ("intent", "architecture", "plan", "glossary", "doc_map", "tasks_glob"):
        value = docs.get(key)
        if isinstance(value, str):
            raw_paths.append(value)
    for key in ("principles", "todo"):
        value = docs.get(key, [])
        if isinstance(value, list):
            raw_paths.extend(item for item in value if isinstance(item, str))

    prefixes: list[str] = []
    for item in raw_paths:
        cleaned = item.split("*", 1)[0].strip("/")
        if not cleaned:
            continue
        if "." in cleaned.split("/")[-1]:
            cleaned = "/".join(cleaned.split("/")[:-1])
        if not cleaned:
            continue
        prefix = f"{cleaned}/"
        if prefix not in prefixes:
            prefixes.append(prefix)

    if not prefixes:
        return (".context/",)
    return tuple(prefixes)


def _should_include_path(path: str, prefixes: tuple[str, ...]) -> bool:
    if path.startswith(".git/"):
        return False
    return any(path.startswith(prefix) for prefix in prefixes)


def _split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end < 0:
        return {}, text
    raw = "\n".join(lines[1:end]).strip()
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    meta = yaml.safe_load(raw) if raw else {}
    if not isinstance(meta, dict):
        return {}, text
    return meta, body


def _compose_front_matter(meta: dict[str, Any], body: str) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False).strip()
    body_text = body.rstrip()
    return f"---\n{fm}\n---\n\n{body_text}\n"


def _set_front_matter_key(text: str, key: str, value: Any) -> str:
    meta, body = _split_front_matter(text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "front matter is required for this operation",
            {"key": key},
        )
    meta[key] = value
    return _compose_front_matter(meta, body)


def _plan_path_from_config(raw: dict[str, Any]) -> str:
    docs = raw.get("docs", {})
    if not isinstance(docs, dict):
        raise ToolError("invalid_config", "docs config must be object", {})
    plan = docs.get("plan")
    if not isinstance(plan, str) or not plan.strip():
        raise ToolError("invalid_config", "docs.plan must be non-empty string", {})
    return plan.strip()


def _advance_plan_for_completed_task(
    plan_text: str,
    completed_task_id: str,
    task_index: dict[str, str],
    plan_path: str,
) -> tuple[str, str | None]:
    meta, body = _split_front_matter(plan_text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"document": "plan"},
        )
    active = meta.get("active_tasks", [])
    blocked = meta.get("blocked_tasks", [])
    next_tasks = meta.get("next_tasks", [])
    if not isinstance(active, list) or not isinstance(blocked, list) or not isinstance(
        next_tasks, list
    ):
        raise ToolError(
            "invalid_plan_meta",
            "active_tasks, blocked_tasks, and next_tasks must be arrays",
            {"document": "plan"},
        )

    active_clean = [item for item in active if isinstance(item, str)]
    blocked_clean = [item for item in blocked if isinstance(item, str)]
    next_clean = [item for item in next_tasks if isinstance(item, str)]

    active_clean = [item for item in active_clean if item != completed_task_id]
    promoted: str | None = None
    remaining_next: list[str] = []
    for item in next_clean:
        if promoted is None and item in task_index and item not in active_clean:
            promoted = item
            continue
        remaining_next.append(item)
    if promoted and promoted not in active_clean:
        active_clean.append(promoted)

    meta["active_tasks"] = active_clean
    meta["blocked_tasks"] = blocked_clean
    meta["next_tasks"] = remaining_next
    next_body = _sync_plan_task_sections(
        body=body,
        plan_path=plan_path,
        task_index=task_index,
        active_tasks=active_clean,
        blocked_tasks=blocked_clean,
        next_tasks=remaining_next,
    )
    return _compose_front_matter(meta, next_body), promoted


def _sync_plan_task_sections(
    body: str,
    plan_path: str,
    task_index: dict[str, str],
    active_tasks: list[str],
    blocked_tasks: list[str],
    next_tasks: list[str],
) -> str:
    lines = body.splitlines()
    lines = _replace_plan_task_section(
        lines,
        section_heading="Active Tasks",
        entries=_format_plan_task_entries(active_tasks, plan_path, task_index),
    )
    lines = _replace_plan_task_section(
        lines,
        section_heading="Blocked Tasks",
        entries=_format_plan_task_entries(blocked_tasks, plan_path, task_index),
    )
    lines = _replace_plan_task_section(
        lines,
        section_heading="Next Tasks",
        entries=_format_plan_task_entries(next_tasks, plan_path, task_index),
    )
    return "\n".join(lines).rstrip()


def _advance_plan_for_blocked_task(
    plan_text: str,
    blocked_task_id: str,
    task_index: dict[str, str],
    plan_path: str,
) -> tuple[str, str | None]:
    meta, body = _split_front_matter(plan_text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"document": "plan"},
        )

    active = meta.get("active_tasks", [])
    blocked = meta.get("blocked_tasks", [])
    next_tasks = meta.get("next_tasks", [])
    if not isinstance(active, list) or not isinstance(blocked, list) or not isinstance(
        next_tasks, list
    ):
        raise ToolError(
            "invalid_plan_meta",
            "active_tasks, blocked_tasks, and next_tasks must be arrays",
            {"document": "plan"},
        )

    active_clean = [item for item in active if isinstance(item, str)]
    blocked_clean = [item for item in blocked if isinstance(item, str)]
    next_clean = [item for item in next_tasks if isinstance(item, str)]

    active_clean = [item for item in active_clean if item != blocked_task_id]
    next_clean = [item for item in next_clean if item != blocked_task_id]
    if blocked_task_id not in blocked_clean:
        blocked_clean.append(blocked_task_id)

    promoted: str | None = None
    remaining_next: list[str] = []
    for item in next_clean:
        if promoted is None and item in task_index and item not in blocked_clean:
            promoted = item
            continue
        remaining_next.append(item)
    if promoted and promoted not in active_clean:
        active_clean.append(promoted)

    meta["active_tasks"] = active_clean
    meta["blocked_tasks"] = blocked_clean
    meta["next_tasks"] = remaining_next
    next_body = _sync_plan_task_sections(
        body=body,
        plan_path=plan_path,
        task_index=task_index,
        active_tasks=active_clean,
        blocked_tasks=blocked_clean,
        next_tasks=remaining_next,
    )
    return _compose_front_matter(meta, next_body), promoted


def _replace_plan_task_section(
    lines: list[str], section_heading: str, entries: list[str]
) -> list[str]:
    marker = f"## {section_heading}"
    heading_idx = -1
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            heading_idx = idx
            break
    if heading_idx < 0:
        return lines

    start = heading_idx + 1
    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break

    replacement: list[str] = [""]
    replacement.extend(entries)
    replacement.append("")
    return lines[:start] + replacement + lines[end:]


def _format_plan_task_entries(
    task_ids: list[str], plan_path: str, task_index: dict[str, str]
) -> list[str]:
    return [
        _format_plan_task_entry(task_id, plan_path=plan_path, task_index=task_index)
        for task_id in task_ids
    ]


def _format_plan_task_entry(
    task_id: str, plan_path: str, task_index: dict[str, str]
) -> str:
    task_path = task_index.get(task_id)
    if not task_path:
        return f"- `{task_id}`"
    relative = relpath(task_path, start=dirname(plan_path))
    if not relative.startswith("."):
        relative = f"./{relative}"
    return f"- [{task_id}]({relative})"


def _preview_change(before: str, after: str) -> str:
    if before == after:
        return "(no change)"
    before_lines = before.splitlines()
    after_lines = after.splitlines()
    if len(after_lines) >= len(before_lines):
        tail = after_lines[max(0, len(before_lines) - 1) :]
    else:
        tail = after_lines[-8:]
    return "\n".join(tail[-12:])
