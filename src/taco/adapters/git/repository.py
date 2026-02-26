from __future__ import annotations

import subprocess
from pathlib import Path

from taco.ports import RepositoryPort


class GitRepositoryAdapter(RepositoryPort):
    def __init__(self, root: Path) -> None:
        self._root = root

    def changed_paths(self) -> list[str]:
        result = self._run("git", "status", "--short")
        paths: list[str] = []
        for raw in result.splitlines():
            line = raw.strip()
            if not line:
                continue
            if len(line) >= 4:
                path = line[3:].strip()
                if path and path not in paths:
                    paths.append(path)
        return paths

    def current_branch(self) -> str:
        return self._run("git", "branch", "--show-current").strip()

    def _run(self, *args: str) -> str:
        completed = subprocess.run(
            args,
            cwd=self._root,
            text=True,
            check=False,
            capture_output=True,
        )
        if completed.returncode != 0:
            return ""
        return completed.stdout
