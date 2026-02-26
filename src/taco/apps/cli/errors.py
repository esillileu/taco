from __future__ import annotations

from typing import Any


class CliError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)

def _required_str(options: dict[str, Any], key: str) -> str:
    value = options.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CliError(
            "invalid_option",
            f"{key} must be a non-empty string",
            {"key": key},
        )
    return value.strip()

