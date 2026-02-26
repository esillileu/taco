from __future__ import annotations

import re
from typing import Any

import yaml

from taco.core.plan.types import ToolError


def _required_str(args: dict[str, Any], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolError(
            "invalid_input",
            f"{key} must be a non-empty string",
            {"key": key},
        )
    return value.strip()

def _ok(data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "data": data}

def _error(code: str, message: str, details: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }

def _placeholder_markers_in_text(text: str) -> list[str]:
    lowered = text.lower()
    patterns = ("todo", "tbd", "placeholder", "auto-generated")
    found: list[str] = []
    for marker in patterns:
        if marker in lowered:
            found.append(marker)
    return found

def _split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end < 0:
        return {}, text
    raw = "\n".join(lines[1:end]).strip()
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    meta = yaml.safe_load(raw) if raw else {}
    if not isinstance(meta, dict):
        return {}, text
    return meta, body

def _compose_front_matter(meta: dict[str, Any], body: str) -> str:
    fm = yaml.safe_dump(meta, sort_keys=False).strip()
    body_text = body.rstrip()
    return f"---\n{fm}\n---\n\n{body_text}\n"

def _set_front_matter_key(text: str, key: str, value: Any) -> str:
    meta, body = _split_front_matter(text)
    if not meta:
        raise ToolError(
            "front_matter_missing",
            "front matter is required for this operation",
            {"key": key},
        )
    meta[key] = value
    return _compose_front_matter(meta, body)

def _collect_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    values: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        parsed = item.strip()
        if parsed and parsed not in values:
            values.append(parsed)
    return values

def _normalize_line(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

