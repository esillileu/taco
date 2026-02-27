from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError, _required_str, _validate_pack_v3


def _build_precheck(_: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    pack = args.get("pack")
    if not isinstance(pack, dict):
        raise ToolError("invalid_input", "pack must be an object", {"key": "pack"})
    _validate_pack_v3(pack)
    task_id = _required_str(pack, "task_id")
    return {
        "task_id": task_id,
        "pack_version": "3",
        "ready": True,
    }

