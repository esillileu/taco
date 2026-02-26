from __future__ import annotations

from pathlib import Path
from typing import Any

from taco.core.packing import PackError
from taco.core.plan import RepoState, ToolError, _error, _ok
from taco.core.routing.router import RouterError
from taco.core.usecases.bootstrap import _project_init
from taco.core.usecases.build import (
    _build_postcheck,
    _build_precheck,
    _convention_get,
    _issue_triage,
)
from taco.core.usecases.doc import _doc_section_get, _doc_section_patch, _doc_snippet
from taco.core.usecases.plan import (
    _plan_intent_apply,
    _plan_intent_autodesign,
    _plan_intent_generate_tasks,
    _plan_intent_index,
    _plan_intent_list,
    _plan_intent_propose,
    _plan_intent_review_bundle,
    _plan_intent_validate,
    _plan_intent_view,
    _plan_locate,
    _plan_validate,
    _plan_view,
)
from taco.core.usecases.task import (
    _plan_pack,
    _task_block,
    _task_complete,
    _task_list,
    _task_pack,
    _task_record,
    _task_targets,
)


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


def call_tool(state: RepoState, name: str, args: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "task.list": _task_list,
        "task.pack": _task_pack,
        "plan.pack": _plan_pack,
        "plan.intent.list": _plan_intent_list,
        "plan.intent.view": _plan_intent_view,
        "plan.intent.index": _plan_intent_index,
        "plan.intent.propose": _plan_intent_propose,
        "plan.intent.autodesign": _plan_intent_autodesign,
        "plan.intent.generate_tasks": _plan_intent_generate_tasks,
        "plan.intent.review_bundle": _plan_intent_review_bundle,
        "plan.intent.apply": _plan_intent_apply,
        "plan.intent.validate": _plan_intent_validate,
        "task.targets": _task_targets,
        "task.record": _task_record,
        "task.complete": _task_complete,
        "task.block": _task_block,
        "doc.snippet": _doc_snippet,
        "doc.section.get": _doc_section_get,
        "doc.section.patch": _doc_section_patch,
        "build.precheck": _build_precheck,
        "build.postcheck": _build_postcheck,
        "issue.triage": _issue_triage,
        "convention.get": _convention_get,
        "plan.view": _plan_view,
        "plan.locate": _plan_locate,
        "plan.validate": _plan_validate,
    }
    handler = handlers.get(name)
    if handler is None:
        return _error("unknown_tool", "tool is not supported", {"tool": name})

    try:
        return _ok(handler(state, args))
    except (ToolError, PackError, RouterError) as exc:
        return _error(exc.code, str(exc), exc.details)
