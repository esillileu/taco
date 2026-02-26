from __future__ import annotations

from pathlib import Path

from taco.core.plan import RepoState, ToolError


def read_text(state: RepoState, path: str) -> str:
    if state.storage is None:
        raise ToolError(
            "storage_unavailable",
            "storage adapter is required",
            {"path": path},
        )
    return state.storage.read_text(Path(path))


def write_text(state: RepoState, path: str, content: str) -> None:
    if state.storage is None:
        raise ToolError(
            "storage_unavailable",
            "storage adapter is required",
            {"path": path},
        )
    state.storage.write_text(Path(path), content)
