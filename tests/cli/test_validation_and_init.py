from __future__ import annotations

import json
from pathlib import Path

from taco.apps.main import main

from .fixture_repo import _write_fixture_repo


def test_cli_main_returns_error_code_for_invalid_input(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["task", "pack", "--task-id", ""], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 1
    assert output["ok"] is False
    assert output["error"]["code"] in {"invalid_option", "invalid_input"}


def test_cli_main_build_precheck_accepts_pack_json_file(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code_pack = main(["task", "pack", "--task-id", "T-008"], cwd=tmp_path)
    pack_output = json.loads(capsys.readouterr().out)
    assert code_pack == 0
    assert pack_output["ok"] is True

    pack_file = tmp_path / "pack.json"
    pack_file.write_text(json.dumps(pack_output["data"]), encoding="utf-8")

    code_precheck = main(
        ["build", "precheck", "--pack-json", str(pack_file)],
        cwd=tmp_path,
    )
    precheck_output = json.loads(capsys.readouterr().out)
    assert code_precheck == 0
    assert precheck_output["ok"] is True


def test_cli_main_build_precheck_invalid_pack_json_error_includes_file_hint(
    tmp_path: Path, capsys
) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["build", "precheck", "--pack-json", "not-json"], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 1
    assert output["ok"] is False
    assert output["error"]["code"] == "invalid_option"
    assert "path to a json file" in output["error"]["message"]


def test_cli_main_task_record_supports_content_file(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    content_file = tmp_path / "record-content.txt"
    content_file.write_text("literal text $(echo should-not-expand)", encoding="utf-8")

    code = main(
        [
            "task",
            "record",
            "--task-id",
            "T-008",
            "--route-type",
            "implementation_result",
            "--content-file",
            str(content_file),
        ],
        cwd=tmp_path,
    )
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["ok"] is True
    assert output["data"]["applied"] is False
    assert "$(echo should-not-expand)" in output["data"]["preview"]


def test_cli_main_task_block_dry_run(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(
        [
            "task",
            "block",
            "--task-id",
            "T-008",
            "--reason-code",
            "scope_split_required",
            "--reason",
            "split task",
        ],
        cwd=tmp_path,
    )
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["ok"] is True
    assert output["data"]["applied"] is False
    assert output["data"]["status_to"] == "blocked"


def test_cli_main_init_bootstraps_context_and_rejects_rerun(
    tmp_path: Path, capsys
) -> None:
    first = main(["init"], cwd=tmp_path)
    first_output = json.loads(capsys.readouterr().out)
    assert first == 0
    assert first_output["ok"] is True
    created_files = first_output["data"]["created_files"]
    assert ".context/project/overview.md" in created_files
    assert ".context/project/intents/index.md" in created_files
    assert ".context/project/intents/I-001-bootstrap.md" in created_files
    assert ".context/project/plan.md" in created_files
    assert ".context/project/architecture/index.md" in created_files
    assert ".context/governance/code-principles.md" in created_files
    assert ".context/governance/git/index.md" in created_files
    assert ".context/governance/doc/index.md" in created_files
    assert (tmp_path / "taco.yaml").exists()

    second = main(["init"], cwd=tmp_path)
    second_output = json.loads(capsys.readouterr().out)
    assert second == 1
    assert second_output["ok"] is False
    assert second_output["error"]["code"] == "init_target_exists"
