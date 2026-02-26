from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from taco.adapters.mcp import McpTransportAdapter

from .handlers import SessionState, handle_request


def run_mcp_loop(
    *,
    root: Path,
    config: str,
    stdin: TextIO,
    stdout: TextIO,
    transport: McpTransportAdapter | None = None,
) -> int:
    adapter = transport or McpTransportAdapter()
    session: SessionState = {"initialized": False, "shutdown": False}

    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            request = adapter.decode(line)
        except json.JSONDecodeError:
            stdout.write(
                adapter.encode(adapter.error(None, -32700, "parse error")) + "\n"
            )
            stdout.flush()
            continue
        except ValueError:
            stdout.write(
                adapter.encode(adapter.error(None, -32600, "invalid request")) + "\n"
            )
            stdout.flush()
            continue

        try:
            response = handle_request(
                request,
                root=root,
                config=config,
                transport=adapter,
                session=session,
            )
        except Exception:
            response = adapter.error(request.get("id"), -32603, "internal error")

        if response is not None:
            stdout.write(adapter.encode(response) + "\n")
            stdout.flush()
        if request.get("method") == "exit":
            break

    return 0
