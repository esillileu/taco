from __future__ import annotations

import importlib.util
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
    required_refs_by_tool: dict[str, tuple[str, ...]]
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


def call_bootstrap_tool(root: Path, name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "project.init": _project_init,
    }
    handler = handlers.get(name)
    if handler is None:
        return _error("unknown_tool", "tool is not supported", {"tool": name})
    try:
        return _ok(handler(root, args))
    except ToolError as exc:
        return _error(exc.code, str(exc), exc.details)


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
        required_refs_by_tool=_load_required_refs_by_tool(raw),
        task_required_headings=_load_task_required_headings(raw),
    )


def call_tool(state: RepoState, name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "task.list": _task_list,
        "task.pack": _task_pack,
        "plan.pack": _plan_pack,
        "plan.intent.list": _plan_intent_list,
        "plan.intent.view": _plan_intent_view,
        "plan.intent.index": _plan_intent_index,
        "task.targets": _task_targets,
        "task.record": _task_record,
        "task.complete": _task_complete,
        "task.block": _task_block,
        "doc.snippet": _doc_snippet,
        "issue.triage": _issue_triage,
        "convention.get": _convention_get,
        "plan.view": _plan_view,
        "plan.locate": _plan_locate,
        "plan.validate": _plan_validate,
    }
    if name == "plan.intent.pack":
        return _error(
            "deprecated_tool",
            "plan.intent.pack was replaced by plan.intent.index",
            {"tool": "plan.intent.pack", "replacement": "plan.intent.index"},
        )
    handler = handlers.get(name)
    if handler is None:
        return _error("unknown_tool", "tool is not supported", {"tool": name})

    try:
        return _ok(handler(state, args))
    except (ToolError, PackError, RouterError) as exc:
        return _error(exc.code, str(exc), exc.details)


def _project_init(root: Path, _args: dict[str, Any]) -> dict[str, Any]:
    directories = (
        ".context/project/intents",
        ".context/project/architecture/modules",
        ".context/project/architecture/flows",
        ".context/project/architecture/schemas",
        ".context/project/tasks",
        ".context/governance/git",
        ".context/governance/doc",
    )
    files = _init_template_files()

    existing = [path for path in files if (root / path).exists()]
    if existing:
        raise ToolError(
            "init_target_exists",
            "init targets already exist",
            {"policy": "fail_on_existing", "paths": ",".join(sorted(existing))},
        )

    created_dirs: list[str] = []
    for rel in directories:
        target = root / rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created_dirs.append(rel)
        else:
            target.mkdir(parents=True, exist_ok=True)

    created_files: list[str] = []
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created_files.append(rel)

    return {
        "policy": "fail_on_existing",
        "created_directories": sorted(created_dirs),
        "created_files": sorted(created_files),
        "created_count": len(created_files),
    }


def _init_template_files() -> dict[str, str]:
    return {
        "taco.yaml": "\n".join(
            [
                "repo:",
                '  root: "."',
                "",
                "docs:",
                '  intent: ".context/project/intents/index.md"',
                '  architecture: ".context/project/architecture/index.md"',
                '  principles: [".context/governance/code-principles.md"]',
                '  plan: ".context/project/plan.md"',
                '  doc_map: ".context/governance/doc/index.md"',
                '  glossary: ".context/project/architecture/schemas/glossary.md"',
                '  todo: [".context/project/plan.md"]',
                '  tasks_glob: ".context/project/tasks/T-*.md"',
                '  intents_glob: ".context/project/intents/I-*.md"',
                "",
                "parsing:",
                "  task_required_headings:",
                '    - "Intent"',
                '    - "Goal"',
                '    - "Scope"',
                '    - "Implementation Approach"',
                '    - "Verification Approach"',
                '    - "Implementation Result"',
                '    - "Verification Result"',
                "  prefer_anchors: true",
                "",
                "budget:",
                "  default_tokens: 1800",
                "  priority_order:",
                '    - "task.core"',
                '    - "task.plans"',
                '    - "arch.snippets"',
                '    - "principles.snippets"',
                '    - "glossary.terms"',
                "",
                "pack:",
                "  required_refs_by_tool:",
                "    plan_pack:",
                '      - "ARCH-INDEX"',
                '      - "PLAN-MAIN"',
                '      - "GOV-DOC-INDEX"',
                "    plan_intent_index:",
                '      - "ARCH-INDEX"',
                '      - "PLAN-MAIN"',
                '      - "GOV-DOC-INDEX"',
                "    task_pack:",
                '      - "GOV-CODE-PRINCIPLES"',
                "",
                "modules:",
                "  git:",
                "    enabled: true",
                '    path: ".context/governance/git/index.md"',
                "",
            ]
        ),
        ".context/project/overview.md": "\n".join(
            [
                "---",
                "id: PROJ-OVERVIEW",
                "type: anchor",
                "title: Project Overview",
                "status: active",
                "links: [ARCH-INDEX, PLAN-MAIN]",
                "---",
                "",
                "# Project Overview",
                "",
                "## Purpose",
                "",
                "- Describe the project objective and execution boundary.",
                "",
                "## Core Objective",
                "",
                "- Keep execution task-first with minimal required context.",
                "",
                "## Non-Goals",
                "",
                "- List concerns intentionally out of scope.",
                "",
            ]
        ),
        ".context/project/intents/index.md": "\n".join(
            [
                "---",
                "id: PROJ-INTENT-INDEX",
                "type: anchor",
                "title: Intent Index",
                "status: active",
                "links: [PLAN-MAIN, ARCH-INDEX]",
                "---",
                "",
                "# Intent Index",
                "",
                "- Store and track plan-level intents under this directory.",
                "- Link each intent to executable tasks via `task_refs`.",
                "",
            ]
        ),
        ".context/project/intents/I-001-bootstrap.md": "\n".join(
            [
                "---",
                "id: I-001",
                "type: intent",
                "title: Bootstrap Initial Intent",
                "status: active",
                "plan_ref: PLAN-MAIN",
                "task_refs: []",
                "links: [PROJ-INTENT-INDEX, PLAN-MAIN, ARCH-INDEX]",
                "---",
                "",
                "# Intent: I-001-bootstrap",
                "",
                "## Intent",
                "",
                "- Capture the first planning goal before creating executable tasks.",
                "",
                "## Scope",
                "",
                "- Keep intent stable while task decomposition evolves.",
                "",
            ]
        ),
        ".context/project/plan.md": "\n".join(
            [
                "---",
                "id: PLAN-MAIN",
                "type: plan",
                "title: Execution Plan",
                "status: active",
                "phase: phase-bootstrap",
                "focus: Initialize task-first documentation baseline",
                "active_intents: []",
                "active_tasks: []",
                "blocked_tasks: []",
                "next_tasks: []",
                "links: [ARCH-INDEX, PROJ-OVERVIEW]",
                "---",
                "",
                "# Plan",
                "",
                "## Planning Boundary",
                "",
                "- Keep plan as sequencing map; avoid architecture duplication.",
                "",
                "## Operational Loop",
                "",
                "1. Select one active intent.",
                "2. Run `plan.intent.index`.",
                "3. Refine architecture/plan/task docs.",
                "4. Hand off to build mode with `task.pack`.",
                "",
                "## Active Tasks",
                "",
                "- None yet.",
                "",
                "## Next Tasks",
                "",
                "- Define the first executable task in `.context/project/tasks/`.",
                "",
            ]
        ),
        ".context/project/architecture/index.md": "\n".join(
            [
                "---",
                "id: ARCH-INDEX",
                "type: anchor",
                "title: Architecture Index",
                "status: active",
                "links: [PROJ-OVERVIEW, PLAN-MAIN]",
                "---",
                "",
                "# Architecture Index",
                "",
                "## Modules",
                "",
                "- Add module nodes under `./modules/`.",
                "",
                "## Flows",
                "",
                "- Add flow nodes under `./flows/`.",
                "",
                "## Schemas",
                "",
                "- Add schema nodes under `./schemas/`.",
                "",
            ]
        ),
        ".context/project/architecture/schemas/glossary.md": "\n".join(
            [
                "---",
                "id: SCH-GLOSSARY",
                "type: schema",
                "title: Glossary",
                "status: active",
                "links: [ARCH-INDEX]",
                "---",
                "",
                "# Glossary",
                "",
                "## Terms",
                "",
                "- Define shared vocabulary used by tasks and architecture.",
                "",
            ]
        ),
        ".context/governance/code-principles.md": "\n".join(
            [
                "---",
                "id: GOV-CODE-PRINCIPLES",
                "type: governance",
                "title: Code Principles",
                "status: active",
                "domain: code",
                "scope: repo",
                "must: []",
                "must_not: []",
                "links: [ARCH-INDEX, PLAN-MAIN]",
                "---",
                "",
                "# Principles",
                "",
                "- Capture code-level rules that apply across all tasks.",
                "",
            ]
        ),
        ".context/governance/git/index.md": "\n".join(
            [
                "---",
                "id: GOV-GIT-INDEX",
                "type: governance",
                "title: Git Conventions",
                "status: active",
                "domain: git",
                "scope: repo",
                "must: []",
                "must_not: []",
                "links: [PLAN-MAIN]",
                "---",
                "",
                "# Git Guide",
                "",
                "- Define branch, commit, and merge conventions.",
                "",
            ]
        ),
        ".context/governance/doc/index.md": "\n".join(
            [
                "---",
                "id: GOV-DOC-INDEX",
                "type: governance",
                "title: Documentation Conventions",
                "status: active",
                "domain: doc",
                "scope: repo",
                "must: []",
                "must_not: []",
                "links: [ARCH-INDEX, PLAN-MAIN]",
                "---",
                "",
                "# Documentation Guide",
                "",
                "## Structure",
                "",
                "- Keep canonical knowledge in `.context/`.",
                "- Keep references `id`-based and maintain front matter integrity.",
                "",
            ]
        ),
    }


def _task_list(state: RepoState, _: dict[str, Any]) -> dict[str, Any]:
    items = [
        {"task_id": task_id, "path": path}
        for task_id, path in sorted(state.index.task_index.items())
    ]
    return {"tasks": items}


def _task_pack(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    _ensure_task_readiness_for_pack(state, task_id)
    return _pack_with_refs(state, args, task_id, "task.pack")


def _plan_pack(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    task_id = _required_str(args, "task_id")
    return _pack_with_refs(state, args, task_id, "plan.pack")


def _plan_intent_list(state: RepoState, _args: dict[str, Any]) -> dict[str, Any]:
    intents = _collect_arch_nodes(state, "intent")
    return {"intents": intents, "count": len(intents)}


def _plan_intent_view(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = _required_str(args, "intent_id")
    path = state.index.node_index.get(intent_id)
    if not path:
        raise ToolError(
            "intent_not_found",
            "intent id not found in index",
            {"intent_id": intent_id},
        )
    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None or doc.doc_type != "intent":
        raise ToolError(
            "intent_not_found",
            "intent id is not mapped to an intent document",
            {"intent_id": intent_id, "path": path},
        )
    meta = doc.metadata if isinstance(doc.metadata, dict) else {}
    task_refs = _collect_string_list(meta.get("task_refs"))
    return {
        "intent": {
            "id": intent_id,
            "path": path,
            "title": str(meta.get("title", "")),
            "status": str(meta.get("status", "")),
            "plan_ref": str(meta.get("plan_ref", "")),
            "task_refs": task_refs,
            "links": _collect_string_list(meta.get("links")),
        }
    }


def _plan_intent_index(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = _required_str(args, "intent_id")
    path = state.index.node_index.get(intent_id)
    if not path:
        raise ToolError(
            "intent_not_found",
            "intent id not found in index",
            {"intent_id": intent_id},
        )
    doc = next((item for item in state.index.documents if item.path == path), None)
    if doc is None or doc.doc_type != "intent":
        raise ToolError(
            "intent_not_found",
            "intent id is not mapped to an intent document",
            {"intent_id": intent_id, "path": path},
        )
    meta = doc.metadata if isinstance(doc.metadata, dict) else {}
    task_refs = _collect_string_list(meta.get("task_refs"))
    existing_refs = [
        task_id for task_id in task_refs if task_id in state.index.task_index
    ]
    candidate_tasks = _intent_candidate_tasks(existing_refs, state)
    coverage = _intent_coverage(existing_refs, state)
    gaps: list[str] = []
    if not task_refs:
        gaps.append("intent.task_refs_missing")
    if task_refs and not existing_refs:
        gaps.append("intent.no_existing_task_refs")
    if existing_refs and not coverage["modules"]:
        gaps.append("coverage.modules_missing")
    if existing_refs and not coverage["flows"]:
        gaps.append("coverage.flows_missing")
    if existing_refs and not coverage["schemas"]:
        gaps.append("coverage.schemas_missing")
    return {
        "intent": {
            "id": intent_id,
            "path": path,
            "title": str(meta.get("title", "")),
            "status": str(meta.get("status", "")),
            "plan_ref": str(meta.get("plan_ref", "")),
            "task_refs": task_refs,
            "links": _collect_string_list(meta.get("links")),
        },
        "coverage": coverage,
        "candidate_tasks": candidate_tasks,
        "gaps": gaps,
        "required_refs_used": list(
            state.required_refs_by_tool.get("plan.intent.index", ())
        ),
    }


def _pack_with_refs(
    state: RepoState,
    args: dict[str, Any],
    task_id: str,
    tool_name: str,
) -> dict[str, Any]:
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
        common_required_refs=state.required_refs_by_tool.get(tool_name, ()),
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
        task_documents=state.index.documents,
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
        task_documents=state.index.documents,
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


def _plan_view(state: RepoState, __args: dict[str, Any]) -> dict[str, Any]:
    plan_path = _plan_path_from_config(state.config_raw)
    plan_text = state.index.document_texts.get(plan_path)
    if plan_text is None:
        plan_text = (state.root / plan_path).read_text(encoding="utf-8")
    plan_meta, _body = _split_front_matter(plan_text)
    if not plan_meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"document": "plan"},
        )

    active_ids = [
        item for item in plan_meta.get("active_tasks", []) if isinstance(item, str)
    ]
    blocked_ids = [
        item for item in plan_meta.get("blocked_tasks", []) if isinstance(item, str)
    ]
    next_ids = [
        item for item in plan_meta.get("next_tasks", []) if isinstance(item, str)
    ]
    active_intents = [
        item for item in plan_meta.get("active_intents", []) if isinstance(item, str)
    ]

    return {
        "plan": {
            "path": plan_path,
            "phase": plan_meta.get("phase", ""),
            "focus": plan_meta.get("focus", ""),
            "active_intents": _intent_summaries(active_intents, state.index),
            "active_tasks": _task_summaries(active_ids, state.index),
            "blocked_tasks": _task_summaries(blocked_ids, state.index),
            "next_tasks": _task_summaries(next_ids, state.index),
        },
        "intents": _collect_arch_nodes(state, "intent"),
        "architecture": {
            "modules": _collect_arch_nodes(state, "module"),
            "flows": _collect_arch_nodes(state, "flow"),
            "schemas": _collect_arch_nodes(state, "schema"),
        },
    }


def _plan_locate(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    change_type = _required_str(args, "change_type").lower()
    target = args.get("target", "")
    if not isinstance(target, str):
        raise ToolError("invalid_input", "target must be a string", {"key": "target"})

    if change_type == "module":
        doc_type = "module"
    elif change_type == "flow":
        doc_type = "flow"
    elif change_type == "schema":
        doc_type = "schema"
    elif change_type == "task":
        doc_type = "task"
    elif change_type == "intent":
        doc_type = "intent"
    elif change_type == "plan":
        doc_type = "plan"
    elif change_type == "governance":
        doc_type = "governance"
    else:
        raise ToolError(
            "invalid_change_type",
            "change_type is not supported",
            {"change_type": change_type},
        )

    candidates: list[dict[str, Any]] = []
    lowered = target.strip().lower()
    for doc in state.index.documents:
        if doc.doc_type != doc_type:
            continue
        title = doc.metadata.get("title", "") if isinstance(doc.metadata, dict) else ""
        node_id = doc.node_id or ""
        text = f"{doc.path} {title} {node_id}".lower()
        if lowered and lowered not in text:
            continue
        candidates.append(
            {
                "path": doc.path,
                "id": node_id,
                "title": title,
                "type": doc.doc_type,
            }
        )

    candidates.sort(key=lambda item: (str(item["path"]), str(item["id"])))
    primary = candidates[0] if candidates else None
    return {
        "change_type": change_type,
        "target": target.strip(),
        "primary": primary,
        "candidates": candidates[:12],
        "count": len(candidates),
    }


def _plan_validate(state: RepoState, _: dict[str, Any]) -> dict[str, Any]:
    script_path = state.root / "scripts" / "validate_docs.py"
    if not script_path.exists():
        errors = _fallback_plan_validation(state)
        return {
            "valid": len(errors) == 0,
            "error_count": len(errors),
            "errors": errors,
        }

    spec = importlib.util.spec_from_file_location("taco_validate_docs", script_path)
    if spec is None or spec.loader is None:
        raise ToolError(
            "validator_load_failed",
            "unable to load validator module",
            {"path": "scripts/validate_docs.py"},
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module_any: Any = module
    module_any.ROOT = state.root
    module_any.CONFIG_PATH = state.root / "taco.yaml"

    config = module.load_config()
    errors = module.validate_config_paths(config)
    files = module.all_context_docs()
    if not files:
        errors.append(".context: no markdown documents found")
    fm_errors, id_to_path, fm_by_path = module.validate_front_matter(files)
    errors.extend(fm_errors)
    if files and not fm_errors:
        errors.extend(module.validate_references(id_to_path, fm_by_path))

    return {
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
    }


def _task_summaries(task_ids: list[str], index: IndexGraph) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        path = index.task_index.get(task_id, "")
        doc = next((item for item in index.documents if item.path == path), None)
        title = ""
        status = ""
        if doc and isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", ""))
            status = str(doc.metadata.get("status", ""))
        rows.append(
            {
                "task_id": task_id,
                "path": path,
                "status": status,
                "title": title,
            }
        )
    return rows


def _intent_summaries(intent_ids: list[str], index: IndexGraph) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for intent_id in intent_ids:
        path = index.node_index.get(intent_id, "")
        doc = next((item for item in index.documents if item.path == path), None)
        if doc is None or doc.doc_type != "intent":
            rows.append({"intent_id": intent_id, "path": "", "title": "", "status": ""})
            continue
        title = ""
        status = ""
        if isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", "") or "")
            status = str(doc.metadata.get("status", "") or "")
        rows.append(
            {
                "intent_id": intent_id,
                "path": path,
                "title": title,
                "status": status,
            }
        )
    return rows


def _intent_candidate_tasks(
    task_ids: list[str], state: RepoState
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_id in task_ids:
        path = state.index.task_index.get(task_id, "")
        if not path:
            continue
        doc = next((item for item in state.index.documents if item.path == path), None)
        title = ""
        status = ""
        if doc and isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", "") or "")
            status = str(doc.metadata.get("status", "") or "")
        missing = _task_pack_readiness_missing(state, task_id)
        rows.append(
            {
                "task_id": task_id,
                "path": path,
                "title": title,
                "status": status,
                "ready_for_build": len(missing) == 0,
                "missing_requirements": missing,
            }
        )
    return rows


def _intent_coverage(
    task_ids: list[str], state: RepoState
) -> dict[str, list[dict[str, str]]]:
    module_ids: list[str] = []
    flow_ids: list[str] = []
    schema_ids: list[str] = []
    for task_id in task_ids:
        task_path = state.index.task_index.get(task_id)
        if not task_path:
            continue
        doc = next(
            (item for item in state.index.documents if item.path == task_path),
            None,
        )
        if doc is None or not isinstance(doc.metadata, dict):
            continue
        refs = doc.metadata.get("references")
        if not isinstance(refs, dict):
            continue
        for value in _collect_string_list(refs.get("modules")):
            if value not in module_ids:
                module_ids.append(value)
        for value in _collect_string_list(refs.get("flows")):
            if value not in flow_ids:
                flow_ids.append(value)
        for value in _collect_string_list(refs.get("schemas")):
            if value not in schema_ids:
                schema_ids.append(value)
    return {
        "modules": _summarize_ref_nodes(module_ids, state),
        "flows": _summarize_ref_nodes(flow_ids, state),
        "schemas": _summarize_ref_nodes(schema_ids, state),
    }


def _summarize_ref_nodes(ref_ids: list[str], state: RepoState) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ref_id in ref_ids:
        path = state.index.node_index.get(ref_id, "")
        doc = next((item for item in state.index.documents if item.path == path), None)
        title = ""
        doc_type = ""
        if doc and isinstance(doc.metadata, dict):
            title = str(doc.metadata.get("title", "") or "")
            doc_type = doc.doc_type
        rows.append(
            {
                "id": ref_id,
                "path": path,
                "title": title,
                "type": doc_type,
            }
        )
    return rows


def _collect_arch_nodes(state: RepoState, doc_type: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in state.index.documents:
        if doc.doc_type != doc_type:
            continue
        title = doc.metadata.get("title", "") if isinstance(doc.metadata, dict) else ""
        rows.append(
            {
                "id": doc.node_id or "",
                "path": doc.path,
                "title": title,
            }
        )
    rows.sort(key=lambda item: (str(item["path"]), str(item["id"])))
    return rows


def _collect_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    values: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        parsed = item.strip()
        if parsed and parsed not in values:
            values.append(parsed)
    return values


def _fallback_plan_validation(state: RepoState) -> list[str]:
    errors: list[str] = []
    if not state.index.documents:
        errors.append(".context: no markdown documents found")
    ids = [doc.node_id for doc in state.index.documents if doc.node_id]
    if len(ids) != len(set(ids)):
        errors.append("duplicate id detected in index")
    return errors


def _is_promotable_task(task_id: str, task_documents: tuple[Any, ...]) -> bool:
    for doc in task_documents:
        if getattr(doc, "task_id", None) != task_id:
            continue
        meta = getattr(doc, "metadata", {})
        if not isinstance(meta, dict):
            return True
        status = meta.get("status")
        if isinstance(status, str) and status.strip() in {"done", "blocked"}:
            return False
        return True
    return True


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


def _load_required_refs_by_tool(raw: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    defaults: dict[str, tuple[str, ...]] = {
        "plan.pack": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
        "plan.intent.index": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
        "task.pack": ("GOV-CODE-PRINCIPLES",),
    }
    pack = raw.get("pack", {})
    if not isinstance(pack, dict):
        return defaults

    by_tool = pack.get("required_refs_by_tool")
    if isinstance(by_tool, dict):
        resolved = dict(defaults)
        plan_pack = _read_ref_list(by_tool, ("plan.pack", "plan_pack"))
        plan_intent_index = _read_ref_list(
            by_tool, ("plan.intent.index", "plan_intent_index")
        )
        task_pack = _read_ref_list(by_tool, ("task.pack", "task_pack"))
        if plan_pack:
            resolved["plan.pack"] = plan_pack
        if plan_intent_index:
            resolved["plan.intent.index"] = plan_intent_index
        if task_pack:
            resolved["task.pack"] = task_pack
        return resolved

    legacy = _load_common_required_refs(raw)
    if legacy:
        return {
            "plan.pack": legacy,
            "plan.intent.index": legacy,
            "task.pack": legacy,
        }
    return defaults


def _read_ref_list(raw: dict[str, Any], keys: tuple[str, ...]) -> tuple[str, ...]:
    for key in keys:
        value = raw.get(key)
        if not isinstance(value, list):
            continue
        refs: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            ref_id = item.strip()
            if ref_id and ref_id not in refs:
                refs.append(ref_id)
        if refs:
            return tuple(refs)
    return ()


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
    missing = _task_pack_readiness_missing(state, task_id)
    if "task_not_found" in missing:
        raise ToolError(
            "task_not_found",
            "task id not found in index",
            {"task_id": task_id},
        )
    if "task_doc_missing" in missing:
        task_path = state.index.task_index.get(task_id, "")
        raise ToolError(
            "task_doc_missing",
            "task document missing from indexed docs",
            {"task_id": task_id, "path": task_path},
        )
    if missing:
        deduped = list(dict.fromkeys(missing))  # preserve first-seen ordering
        raise ToolError(
            "task_not_ready",
            "task is not ready for pack execution",
            {
                "task_id": task_id,
                "missing_requirements": ",".join(deduped),
            },
        )


def _task_pack_readiness_missing(state: RepoState, task_id: str) -> list[str]:
    task_path = state.index.task_index.get(task_id)
    if not task_path:
        return ["task_not_found"]
    task_doc = next(
        (doc for doc in state.index.documents if doc.path == task_path),
        None,
    )
    if task_doc is None:
        return ["task_doc_missing"]
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
    return missing


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
    for key in (
        "intent",
        "architecture",
        "plan",
        "glossary",
        "doc_map",
        "tasks_glob",
        "intents_glob",
    ):
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
    task_documents: tuple[Any, ...],
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
    active_clean = [
        item for item in active_clean if _is_promotable_task(item, task_documents)
    ]
    next_clean = [
        item for item in next_clean if _is_promotable_task(item, task_documents)
    ]

    active_clean = [item for item in active_clean if item != completed_task_id]
    next_clean = [item for item in next_clean if item != completed_task_id]
    promoted: str | None = None
    remaining_next: list[str] = []
    for item in next_clean:
        if (
            promoted is None
            and item in task_index
            and item not in active_clean
            and _is_promotable_task(item, task_documents)
        ):
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
    task_documents: tuple[Any, ...],
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
    active_clean = [
        item for item in active_clean if _is_promotable_task(item, task_documents)
    ]
    next_clean = [
        item for item in next_clean if _is_promotable_task(item, task_documents)
    ]

    active_clean = [item for item in active_clean if item != blocked_task_id]
    next_clean = [item for item in next_clean if item != blocked_task_id]
    if blocked_task_id not in blocked_clean:
        blocked_clean.append(blocked_task_id)

    promoted: str | None = None
    remaining_next: list[str] = []
    for item in next_clean:
        if (
            promoted is None
            and item in task_index
            and item not in blocked_clean
            and _is_promotable_task(item, task_documents)
        ):
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
