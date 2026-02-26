from __future__ import annotations

import json
from pathlib import Path

_TEMPLATES_PATH = (
    Path(__file__).resolve().parents[3]
    / "resources"
    / "templates"
    / "project_init_templates.json"
)


def _init_template_files() -> dict[str, str]:
    loaded = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    return {str(key): str(value) for key, value in loaded.items()}
