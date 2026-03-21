from __future__ import annotations

from typing import Any

REQUIRED_HEADINGS = (
    "Intent",
    "Goal",
    "Scope",
    "Implementation Approach",
    "Verification Approach",
    "Implementation Result",
    "Verification Result",
)

BOUNDARY_TERMS = (
    "boundary",
    "hexagonal",
    "port",
    "adapter",
    "contract",
    "interface",
)

VERIFICATION_TERMS = (
    "uv run",
    "pytest",
    "test",
    "assert",
    "check",
    "verify",
    "expect",
)


def normalize_text(value: Any) -> str:
    text = str(value)
    return text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")


def section_body(text: str, heading: str) -> str:
    marker = f"## {heading}"
    lines = text.splitlines()
    start = -1
    for idx, line in enumerate(lines):
        if line.strip() == marker:
            start = idx + 1
            break
    if start < 0:
        return ""
    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return "\n".join(lines[start:end]).strip()


def non_empty_lines(text: str) -> int:
    return len([line for line in normalize_text(text).splitlines() if line.strip()])
