from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from taco.adapters.mcp import McpTransportAdapter
from taco.apps.composition import build_repo_state, call_tool

from .catalog import tool_catalog
from .protocol import is_notification, is_valid_request_id, normalize_params

SessionState = dict[str, bool]


def handle_request(
    request: dict[str, Any],
    *,
    root: Path,
    config: str,
    transport: McpTransportAdapter,
    session: SessionState,
) -> dict[str, Any] | None:
    if (
        is_notification(request)
        and request.get("method") == "notifications/initialized"
    ):
        session["initialized"] = True
        return None

    request_id = request.get("id")
    if not is_valid_request_id(request_id):
        return transport.error(None, -32600, "invalid request")
    if request.get("jsonrpc") != "2.0":
        return transport.error(request_id, -32600, "invalid request")

    method = request.get("method")
    if not isinstance(method, str) or not method.strip():
        return transport.error(request_id, -32600, "invalid request")

    try:
        params = normalize_params(request)
    except ValueError:
        return transport.error(request_id, -32602, "invalid params")

    if session["shutdown"] and method != "exit":
        if is_notification(request):
            return None
        return transport.error(request_id, -32000, "server is shutting down")

    if method == "initialize":
        session["initialized"] = True
        session["shutdown"] = False
        response = transport.success(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "taco", "version": "0.1.0"},
            },
        )
        return None if is_notification(request) else response

    if method == "ping":
        response = transport.success(request_id, {})
        return None if is_notification(request) else response

    if method == "tools/list":
        if not session["initialized"]:
            return transport.error(request_id, -32002, "server not initialized")
        response = transport.success(request_id, {"tools": tool_catalog()})
        return None if is_notification(request) else response

    if method == "tools/call":
        if not session["initialized"]:
            return transport.error(request_id, -32002, "server not initialized")
        tool_name = params.get("name")
        if not isinstance(tool_name, str) or not tool_name.strip():
            return transport.error(request_id, -32602, "invalid params")
        arguments = params.get("arguments", {})
        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return transport.error(request_id, -32602, "invalid params")

        state = build_repo_state(root, (root / config).resolve())
        envelope = call_tool(state, tool_name.strip(), arguments)
        response = transport.success(
            request_id,
            {
                "content": [
                    {"type": "text", "text": json.dumps(envelope, ensure_ascii=False)}
                ],
                "structuredContent": envelope,
                "isError": not bool(envelope.get("ok")),
            },
        )
        return None if is_notification(request) else response

    if method == "shutdown":
        session["shutdown"] = True
        response = transport.success(request_id, {})
        return None if is_notification(request) else response

    if method == "exit":
        return None

    if is_notification(request):
        return None
    return transport.error(request_id, -32601, "method not found")
