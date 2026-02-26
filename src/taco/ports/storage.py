from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StoragePort(Protocol):
    def read_text(self, path: Path) -> str:
        ...

    def write_text(self, path: Path, content: str) -> None:
        ...

    def exists(self, path: Path) -> bool:
        ...
