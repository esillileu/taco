from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "taco"


def _python_files(base: Path) -> list[Path]:
    return [
        path
        for path in base.rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def test_core_does_not_import_adapters() -> None:
    forbidden = ("from taco.adapters", "import taco.adapters")
    for path in _python_files(SRC / "core"):
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), path.as_posix()


def test_ports_do_not_import_adapters() -> None:
    forbidden = ("from taco.adapters", "import taco.adapters")
    for path in _python_files(SRC / "ports"):
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), path.as_posix()


def test_apps_cli_does_not_depend_on_adapters_cli() -> None:
    for path in _python_files(SRC / "apps" / "cli"):
        text = path.read_text(encoding="utf-8")
        assert "adapters.cli" not in text, path.as_posix()
