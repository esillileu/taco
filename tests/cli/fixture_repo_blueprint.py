from __future__ import annotations

from pathlib import Path

from taco.core.plan import _compose_front_matter


def author_task_from_blueprint(root: Path, blueprint: dict[str, object]) -> None:
    task_path = str(blueprint.get("path", "")).strip()
    assert task_path
    fm = blueprint.get("front_matter_requirements")
    assert isinstance(fm, dict)
    scope = fm.get("scope")
    if isinstance(scope, dict):
        scope["out"] = ["non-goal: unrelated runtime behavior"]
        fm["scope"] = scope
    body = "\n".join(
        [
            f"# Task: {fm.get('title', '')}",
            "",
            "## Intent",
            "- authored from blueprint for review gate pass.",
            "",
            "## Goal",
            "- make review and apply pass with authored task content.",
            "",
            "## Scope",
            "- keep change boundary inside task blueprint constraints.",
            "- Out of Scope: unrelated runtime behavior.",
            "",
            "## Implementation Approach",
            "1. use blueprint front matter exactly.",
            "2. author required sections with actionable lines.",
            "",
            "## Verification Approach",
            "- run review bundle and expect pass.",
            "- run apply and expect success.",
            "",
            "## Implementation Result",
            "- pending",
            "",
            "## Verification Result",
            "- pending",
        ]
    )
    text = _compose_front_matter(fm, body)
    target = root / task_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
