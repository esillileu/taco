from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "taco.yaml"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def get_task_files(config: dict[str, Any]) -> list[Path]:
    pattern = config.get("docs", {}).get("tasks_glob", "docs/dev/tasks/T-*.md")
    return sorted(ROOT.glob(pattern))


def get_todo_files(config: dict[str, Any]) -> list[Path]:
    rels = config.get("docs", {}).get("todo", ["docs/dev/todo.md"])
    files: list[Path] = []
    for rel in rels:
        p = ROOT / rel
        if p.exists():
            files.append(p)
    return files


def get_required_headings(config: dict[str, Any]) -> list[str]:
    return config.get("parsing", {}).get(
        "task_required_headings",
        [
            "Intent",
            "Goal",
            "Scope",
            "Implementation Approach",
            "Verification Approach",
            "Implementation Result",
            "Verification Result",
        ],
    )


def validate_task_headings(task_files: list[Path], required: list[str]) -> list[str]:
    errors: list[str] = []
    required_markers = [f"## {h}" for h in required]
    for task_file in task_files:
        text = task_file.read_text(encoding="utf-8")
        missing = [h for h in required_markers if h not in text]
        if missing:
            errors.append(f"{task_file}: missing headings {missing}")
    return errors


def validate_todo_links(todo_files: list[Path]) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    task_links: set[str] = set()
    for todo in todo_files:
        text = todo.read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        for rel in links:
            if rel.startswith("http") or rel.startswith("#"):
                continue
            path = (todo.parent / rel).resolve()
            if not path.exists():
                errors.append(f"todo link path not found: {rel} (from {todo})")
                continue
            try:
                rel_path = path.relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if "/tasks/" in rel_path and rel_path.endswith(".md"):
                task_links.add(rel_path)
    return errors, task_links


def validate_todo_task_coverage(task_files: list[Path], todo_task_links: set[str]) -> list[str]:
    errors: list[str] = []
    expected = {p.relative_to(ROOT).as_posix() for p in task_files}
    missing = sorted(expected - todo_task_links)
    if missing:
        errors.append(f"tasks missing from todo: {missing}")
    return errors


def main() -> int:
    config = load_config()
    task_files = get_task_files(config)
    todo_files = get_todo_files(config)
    required = get_required_headings(config)

    errors = validate_task_headings(task_files, required)
    todo_errors, todo_task_links = validate_todo_links(todo_files)
    errors.extend(todo_errors)
    errors.extend(validate_todo_task_coverage(task_files, todo_task_links))

    if errors:
        print("DOC VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("DOC VALIDATION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
