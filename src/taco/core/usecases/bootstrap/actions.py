from __future__ import annotations

from pathlib import Path
from typing import Any

from taco.core.plan import ToolError
from taco.core.usecases.bootstrap.templates import _init_template_files


def _project_init(root: Path, _args: dict[str, Any]) -> dict[str, Any]:
    directories = (
        ".context/project/intents",
        ".context/project/architecture/modules",
        ".context/project/architecture/flows",
        ".context/project/architecture/schemas",
        ".context/project/tasks",
        ".context/governance/git",
        ".context/governance/doc",
    )
    files = _init_template_files()

    existing = [path for path in files if (root / path).exists()]
    if existing:
        raise ToolError(
            "init_target_exists",
            "init targets already exist",
            {"policy": "fail_on_existing", "paths": ",".join(sorted(existing))},
        )

    created_dirs: list[str] = []
    for rel in directories:
        target = root / rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created_dirs.append(rel)
        else:
            target.mkdir(parents=True, exist_ok=True)

    created_files: list[str] = []
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created_files.append(rel)

    return {
        "policy": "fail_on_existing",
        "created_directories": sorted(created_dirs),
        "created_files": sorted(created_files),
        "created_count": len(created_files),
    }
