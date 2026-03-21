from __future__ import annotations

import json
from pathlib import Path

_TEMPLATES_PATH = (
    Path(__file__).resolve().parents[3]
    / "resources"
    / "templates"
    / "project_init_templates.json"
)
_GOVERNANCE_TEMPLATES = {
    ".context/governance/code-principles.md": "governance/code-principles.md",
    ".context/governance/git/index.md": "governance/git/index.md",
    ".context/governance/doc/index.md": "governance/doc/index.md",
}


def _init_template_files() -> dict[str, str]:
    loaded = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {}
    templates = {str(key): str(value) for key, value in loaded.items()}
    base_dir = _TEMPLATES_PATH.parent
    for output_path, rel_template in _GOVERNANCE_TEMPLATES.items():
        template_path = base_dir / rel_template
        templates[output_path] = template_path.read_text(encoding="utf-8")
    return templates
