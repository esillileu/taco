from __future__ import annotations

from pathlib import Path
from typing import Any

from taco.core.plan import RepoState


def _build_refactor_analysis(
    state: RepoState,
    intent_id: str,
    intent_path: str,
    kind: str,
    design_impact: str,
) -> dict[str, Any]:
    required = kind == "refactor"
    oversized = _oversized_source_files(state.root, max_lines=250) if required else []
    max_lines = max((item[1] for item in oversized), default=0)
    if max_lines >= 600:
        suggested = "major"
    elif max_lines >= 300:
        suggested = "minor"
    elif required:
        suggested = "none"
    else:
        suggested = "unspecified"
    completed = (state.root / "src").exists() if required else True
    findings = [
        {
            "path": path,
            "line_count": line_count,
            "reason": "exceeds_file_line_budget_250",
        }
        for path, line_count in oversized[:20]
    ]
    return {
        "required": required,
        "completed": completed,
        "intent_id": intent_id,
        "intent_path": intent_path,
        "design_impact": design_impact,
        "suggested_design_impact": suggested,
        "oversized_file_count": len(oversized),
        "max_file_lines": max_lines,
        "findings": findings,
    }

def _oversized_source_files(root: Path, max_lines: int) -> list[tuple[str, int]]:
    candidates: list[tuple[str, int]] = []
    src_root = root / "src"
    if not src_root.exists():
        return candidates
    for path in sorted(src_root.rglob("*.py")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count > max_lines:
            candidates.append((rel, line_count))
    candidates.sort(key=lambda item: (-item[1], item[0]))
    return candidates

