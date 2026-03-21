from __future__ import annotations

from taco.core.plan import (
    RepoState,
    ToolError,
    _compose_front_matter,
    _split_front_matter,
)
from taco.core.usecases.io import read_text, write_text

from .intent_helpers import plan_path_from_state


def current_plan_stage(state: RepoState) -> str:
    plan_path = plan_path_from_state(state)
    text = state.index.document_texts.get(plan_path) or read_text(state, plan_path)
    meta, _ = _split_front_matter(text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"path": plan_path},
        )
    stage = str(meta.get("plan_mode_stage", "")).strip().lower()
    if stage in {"intent_decomposition", "design_change", "task_authoring"}:
        return stage
    return "intent_decomposition"


def set_plan_stage(state: RepoState, stage: str) -> None:
    if stage not in {"intent_decomposition", "design_change", "task_authoring"}:
        raise ToolError("invalid_input", "invalid plan mode stage", {"stage": stage})
    plan_path = plan_path_from_state(state)
    text = state.index.document_texts.get(plan_path) or read_text(state, plan_path)
    meta, body = _split_front_matter(text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "plan front matter is required",
            {"path": plan_path},
        )
    meta["plan_mode_stage"] = stage
    write_text(state, plan_path, _compose_front_matter(meta, body))
