from __future__ import annotations

import json
from pathlib import Path

import yaml

from taco.main import main


def _write_fixture_repo(root: Path) -> None:
    (root / "docs" / "dev" / "tasks").mkdir(parents=True)
    (root / "docs" / "dev").mkdir(exist_ok=True)
    (root / "docs" / "intent.md").write_text("# Intent\n", encoding="utf-8")
    (root / "docs" / "architecture.md").write_text(
        "\n".join(
            [
                "# Architecture",
                "## System",
                "<!-- taco:pack=arch.snippets -->",
                "system detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (root / "docs" / "glossary.md").write_text(
        "\n".join(
            [
                "# Glossary",
                "## Terms",
                "<!-- taco:pack=glossary.terms -->",
                "term detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "principles.md").write_text(
        "\n".join(
            [
                "# Principles",
                "## Rules",
                "<!-- taco:pack=principles.snippets -->",
                "rules detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (root / "docs" / "dev" / "git.md").write_text("# Git Rules\n", encoding="utf-8")
    (root / "docs" / "dev" / "tasks" / "T-008-cli-entrypoint.md").write_text(
        "\n".join(
            [
                "# Task: T-008-cli-entrypoint",
                "## Intent",
                "<!-- taco:pack=task.core -->",
                "intent",
                "## Goal",
                "<!-- taco:pack=task.core -->",
                "goal",
                "## Scope",
                "<!-- taco:pack=task.core,pack.next_actions -->",
                "- run cli task list",
                "scope",
                "## Implementation Approach",
                "<!-- taco:pack=task.plans,pack.next_actions -->",
                "1. wire argparse",
                "impl",
                "## Verification Approach",
                "<!-- taco:pack=task.plans,pack.acceptance_checks,"
                "pack.verification_commands -->",
                "- verify cli json output",
                "- uv run --extra dev pytest -q",
                "verify",
                "## Implementation Result",
                "Pending",
                "## Verification Result",
                "Pending",
            ]
        ),
        encoding="utf-8",
    )
    config = {
        "docs": {
            "intent": "docs/intent.md",
            "architecture": "docs/architecture.md",
            "plan": "docs/plan.md",
            "glossary": "docs/glossary.md",
            "principles": ["docs/dev/principles.md"],
            "todo": ["docs/dev/todo.md"],
            "tasks_glob": "docs/dev/tasks/T-*.md",
        },
        "budget": {
            "default_tokens": 100,
            "priority_order": [
                "task.core",
                "task.plans",
                "arch.snippets",
                "principles.snippets",
                "glossary.terms",
            ],
            "required_groups": [
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ],
        },
        "modules": {"git": {"path": "docs/dev/git.md"}},
    }
    (root / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")


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


def test_cli_main_returns_error_code_for_invalid_input(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["task", "pack", "--task-id", ""], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 1
    assert output["ok"] is False
    assert output["error"]["code"] in {"invalid_option", "invalid_input"}
