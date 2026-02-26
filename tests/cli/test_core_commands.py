from __future__ import annotations

import json
from pathlib import Path

from taco.apps.main import main

from .fixture_repo import _write_fixture_repo


def test_cli_main_task_list_json_output(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["task", "list"], cwd=tmp_path)
    captured = capsys.readouterr().out

    assert code == 0
    payload = json.loads(captured)
    assert payload["ok"] is True
    assert payload["data"]["tasks"][0]["task_id"] == "T-008"


def test_cli_main_task_pack_and_doc_snippet(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code_pack = main(["task", "pack", "--task-id", "T-008"], cwd=tmp_path)
    pack_output = json.loads(capsys.readouterr().out)

    code_snip = main(
        ["doc", "snippet", "--path", "docs/architecture.md", "--anchor-id", "system"],
        cwd=tmp_path,
    )
    snip_output = json.loads(capsys.readouterr().out)

    assert code_pack == 0
    assert pack_output["ok"] is True
    assert pack_output["data"]["task_id"] == "T-008"
    assert code_snip == 0
    assert snip_output["ok"] is True


def test_cli_main_task_pack_auto_pick_from_active(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["task", "pack"], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["ok"] is True
    assert output["data"]["task_id"] == "T-008"


def test_cli_main_human_context_for_pack_and_snippet(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code_pack = main(
        ["--human-context", "task", "pack", "--task-id", "T-008"],
        cwd=tmp_path,
    )
    pack_output = capsys.readouterr().out
    assert code_pack == 0
    assert "[task.core]" in pack_output
    assert "docs/dev/tasks/T-008-cli-entrypoint.md" in pack_output

    code_snip = main(
        [
            "--human-context",
            "doc",
            "snippet",
            "--path",
            "docs/architecture.md",
            "--anchor-id",
            "system",
        ],
        cwd=tmp_path,
    )
    snip_output = capsys.readouterr().out
    assert code_snip == 0
    assert "System (docs/architecture.md#system)" in snip_output
    assert "system detail" in snip_output


def test_cli_main_human_context_rejects_unsupported_command(
    tmp_path: Path, capsys
) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["--human-context", "task", "list"], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 1
    assert output["ok"] is False
    assert output["error"]["code"] == "invalid_mode"


def test_cli_main_plan_view(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["plan", "view"], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["ok"] is True
    assert "plan" in output["data"]


def test_cli_main_plan_pack(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["plan", "pack", "--task-id", "T-008"], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["ok"] is True
    assert output["data"]["task_id"] == "T-008"


def test_cli_main_plan_intent_list_view_index(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)

    code_list = main(["plan", "intent", "list"], cwd=tmp_path)
    list_output = json.loads(capsys.readouterr().out)
    assert code_list == 0
    assert list_output["ok"] is True
    assert list_output["data"]["count"] == 1
    assert list_output["data"]["intents"][0]["id"] == "I-001"

    code_view = main(["plan", "intent", "view", "--intent-id", "I-001"], cwd=tmp_path)
    view_output = json.loads(capsys.readouterr().out)
    assert code_view == 0
    assert view_output["ok"] is True
    assert view_output["data"]["intent"]["plan_ref"] == "PLAN-MAIN"

    code_index = main(["plan", "intent", "index", "--intent-id", "I-001"], cwd=tmp_path)
    index_output = json.loads(capsys.readouterr().out)
    assert code_index == 0
    assert index_output["ok"] is True
    assert index_output["data"]["intent"]["id"] == "I-001"
    assert index_output["data"]["candidate_tasks"][0]["task_id"] == "T-008"
