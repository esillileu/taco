from __future__ import annotations

from pathlib import Path

from taco.adapters.fs.repo_state import load_repo_state
from taco.core.plan import RepoState, ToolError
from taco.core.usecases import call_bootstrap_tool, call_tool


def build_repo_state(root: Path, config_path: Path | None = None) -> RepoState:
    return load_repo_state(root, config_path=config_path)


__all__ = [
    "RepoState",
    "ToolError",
    "build_repo_state",
    "call_bootstrap_tool",
    "call_tool",
]
