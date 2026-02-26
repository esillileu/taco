from __future__ import annotations

from typing import Any


def is_valid_request_id(value: Any) -> bool:
    return value is None or isinstance(value, (str, int))


def is_notification(request: dict[str, Any]) -> bool:
    return "id" not in request


def normalize_params(request: dict[str, Any]) -> dict[str, Any]:
    params = request.get("params", {})
    if params is None:
        return {}
    if not isinstance(params, dict):
        raise ValueError("params must be object")
    return params
