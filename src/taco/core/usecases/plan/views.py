from __future__ import annotations

import importlib.util
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _placeholder_markers_in_text,
    _plan_path_from_config,
    _required_str,
    _split_front_matter,
)
from taco.core.usecases.io import read_text
from taco.core.usecases.plan.support import (
    _collect_arch_nodes,
    _fallback_plan_validation,
    _intent_summaries,
    _task_summaries,
)


def _plan_view(state: RepoState, __args: dict[str, Any]) -> dict[str, Any]:
    plan_path = _plan_path_from_config(state.config_raw)
    plan_text = state.index.document_texts.get(plan_path)
    if plan_text is None:
        plan_text = read_text(state, plan_path)
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
    for rel, text in state.index.document_texts.items():
        markers = _placeholder_markers_in_text(text)
        if markers:
            errors.append(f"{rel}: placeholder markers detected {markers}")

    return {
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
    }
