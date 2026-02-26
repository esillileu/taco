from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

from taco.apps.mcp.main import main as mcp_main

from .fixture_repo import write_fixture_repo


def test_mcp_main_initialize_and_tools_list(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    in_stream = StringIO(
        "\n".join(
            [
                json.dumps(
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
                ),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {"name": "task.list", "arguments": {}},
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "id": 4, "method": "exit"}),
            ]
        )
        + "\n"
    )
    out_stream = StringIO()

    assert mcp_main(cwd=tmp_path, stdin=in_stream, stdout=out_stream) == 0
    rows = [
        json.loads(line) for line in out_stream.getvalue().splitlines() if line.strip()
    ]
    assert rows[0]["result"]["serverInfo"]["name"] == "taco"
    assert any(item["name"] == "task.pack" for item in rows[1]["result"]["tools"])
    assert rows[2]["result"]["isError"] is False
    assert rows[2]["result"]["structuredContent"]["ok"] is True


def test_mcp_main_reports_parse_and_method_errors(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    in_stream = StringIO(
        "\n".join(
            [
                "{bad-json",
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "unknown/method"}),
            ]
        )
        + "\n"
    )
    out_stream = StringIO()

    assert mcp_main(cwd=tmp_path, stdin=in_stream, stdout=out_stream) == 0
    rows = [
        json.loads(line) for line in out_stream.getvalue().splitlines() if line.strip()
    ]
    assert rows[0]["error"]["code"] == -32700
    assert rows[1]["error"]["code"] == -32601


def test_mcp_main_handles_lifecycle_notifications_without_response(
    tmp_path: Path,
) -> None:
    write_fixture_repo(tmp_path)
    in_stream = StringIO(
        "\n".join(
            [
                json.dumps(
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
                ),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {},
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "method": "ping", "params": {}}),
                json.dumps({"jsonrpc": "2.0", "method": "exit", "params": {}}),
            ]
        )
        + "\n"
    )
    out_stream = StringIO()

    assert mcp_main(cwd=tmp_path, stdin=in_stream, stdout=out_stream) == 0
    rows = [
        json.loads(line) for line in out_stream.getvalue().splitlines() if line.strip()
    ]
    assert len(rows) == 1
    assert rows[0]["id"] == 1
    assert rows[0]["result"]["serverInfo"]["name"] == "taco"


def test_mcp_main_rejects_invalid_request_shape_and_id_type(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    in_stream = StringIO(
        "\n".join(
            [
                json.dumps(["not-an-object"]),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": {"bad": "id"},
                        "method": "initialize",
                        "params": {},
                    }
                ),
            ]
        )
        + "\n"
    )
    out_stream = StringIO()

    assert mcp_main(cwd=tmp_path, stdin=in_stream, stdout=out_stream) == 0
    rows = [
        json.loads(line) for line in out_stream.getvalue().splitlines() if line.strip()
    ]
    assert rows[0]["error"]["code"] == -32600
    assert rows[1]["error"]["code"] == -32600


def test_mcp_main_codex_style_e2e_flow(tmp_path: Path) -> None:
    write_fixture_repo(tmp_path)
    in_stream = StringIO(
        "\n".join(
            [
                json.dumps(
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
                ),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "method": "notifications/initialized",
                        "params": {},
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "task.pack",
                            "arguments": {"task_id": "T-006"},
                        },
                    }
                ),
                json.dumps({"jsonrpc": "2.0", "id": 4, "method": "shutdown"}),
                json.dumps({"jsonrpc": "2.0", "method": "exit"}),
            ]
        )
        + "\n"
    )
    out_stream = StringIO()

    assert mcp_main(cwd=tmp_path, stdin=in_stream, stdout=out_stream) == 0
    rows = [
        json.loads(line) for line in out_stream.getvalue().splitlines() if line.strip()
    ]
    assert [row["id"] for row in rows] == [1, 2, 3, 4]
    assert rows[0]["result"]["protocolVersion"] == "2024-11-05"
    assert any(tool["name"] == "task.pack" for tool in rows[1]["result"]["tools"])
    assert rows[2]["result"]["isError"] is False
    assert rows[2]["result"]["structuredContent"]["ok"] is True
    assert rows[2]["result"]["structuredContent"]["data"]["task_id"] == "T-006"
    assert rows[3]["result"] == {}
