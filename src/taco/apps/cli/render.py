from __future__ import annotations

from typing import Any


def _render_human_context(tool_name: str, data: Any) -> str:
    if not isinstance(data, dict):
        return "(no data)"
    if tool_name == "task.pack":
        snippets = data.get("context_snippets", [])
        if not isinstance(snippets, list) or not snippets:
            return "(no context snippets)"
        blocks: list[str] = []
        for row in snippets:
            if not isinstance(row, dict):
                continue
            group = str(row.get("group", "")).strip() or "snippet"
            path = str(row.get("path", "")).strip() or "(unknown)"
            anchor = str(row.get("anchor_id", "")).strip()
            content = str(row.get("content", "")).rstrip()
            target = f"{path}#{anchor}" if anchor else path
            blocks.append(f"[{group}] {target}\n{content}")
        return "\n\n".join(blocks) if blocks else "(no context snippets)"
    if tool_name == "doc.snippet":
        heading = str(data.get("heading", "")).strip() or "Snippet"
        path = str(data.get("path", "")).strip() or "(unknown)"
        anchor = str(data.get("anchor_id", "")).strip()
        target = f"{path}#{anchor}" if anchor else path
        snippet = str(data.get("snippet", "")).rstrip()
        return f"{heading} ({target})\n\n{snippet}"
    return "(unsupported tool)"

