from __future__ import annotations

from pathlib import Path

from taco.ports import StoragePort


class FileSystemStorageAdapter(StoragePort):
    def __init__(self, root: Path) -> None:
        self._root = root

    def read_text(self, path: Path) -> str:
        return self._resolve(path).read_text(encoding="utf-8")

    def write_text(self, path: Path, content: str) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def exists(self, path: Path) -> bool:
        return self._resolve(path).exists()

    def _resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self._root / path
