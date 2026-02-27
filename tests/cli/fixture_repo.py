from __future__ import annotations

from pathlib import Path

from .fixture_repo_blueprint import author_task_from_blueprint
from .fixture_repo_builder import write_fixture_repo


def _write_fixture_repo(root: Path) -> None:
    write_fixture_repo(root)


def _author_task_from_blueprint(root: Path, blueprint: dict[str, object]) -> None:
    author_task_from_blueprint(root, blueprint)

