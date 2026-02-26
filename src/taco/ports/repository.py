from __future__ import annotations

from typing import Protocol


class RepositoryPort(Protocol):
    def changed_paths(self) -> list[str]:
        ...

    def current_branch(self) -> str:
        ...
