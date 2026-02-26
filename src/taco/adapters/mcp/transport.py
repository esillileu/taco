from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class McpTransportAdapter:
    """JSON-RPC line protocol adapter for MCP stdio runtime."""

    def decode(self, payload: str) -> dict[str, Any]:
        data = json.loads(payload)
        if not isinstance(data, dict):
            raise ValueError("request must be an object")
        return data

    def encode(self, payload: dict[str, Any]) -> str:
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    def success(self, request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    def error(
        self,
        request_id: Any,
        code: int,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }
        if data is not None:
            payload["error"]["data"] = data
        return payload
