from __future__ import annotations

import json
from pathlib import Path

import yaml

from taco.main import main


def _write_fixture_repo(root: Path) -> None:
    (root / "docs" / "dev" / "tasks").mkdir(parents=True)
    (root / "docs" / "intents").mkdir(parents=True)
    (root / "docs" / "dev").mkdir(exist_ok=True)
    (root / "docs" / "intent.md").write_text(
        "\n".join(
            [
                "---",
                "id: PROJ-INTENT",
                "type: anchor",
                "title: Intent",
                "status: active",
                "links: []",
                "---",
                "",
                "# Intent",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "architecture.md").write_text(
        "\n".join(
            [
                "---",
                "id: ARCH-INDEX",
                "type: anchor",
                "title: Architecture",
                "status: active",
                "links: []",
                "---",
                "",
                "# Architecture",
                "## System",
                "<!-- taco:pack=arch.snippets -->",
                "system detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "plan.md").write_text(
        "\n".join(
            [
                "---",
                "id: PLAN-MAIN",
                "type: plan",
                "title: Plan",
                "status: active",
                "active_tasks: []",
                "blocked_tasks: []",
                "next_tasks: []",
                "links: []",
                "---",
                "",
                "# Plan",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "glossary.md").write_text(
        "\n".join(
            [
                "---",
                "id: SCH-GLOSSARY",
                "type: schema",
                "title: Glossary",
                "status: active",
                "links: []",
                "---",
                "",
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
                "---",
                "id: GOV-CODE-PRINCIPLES",
                "type: governance",
                "title: Principles",
                "status: active",
                "links: []",
                "---",
                "",
                "# Principles",
                "## Rules",
                "<!-- taco:pack=principles.snippets -->",
                "rules detail",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "doc-index.md").write_text(
        "\n".join(
            [
                "---",
                "id: GOV-DOC-INDEX",
                "type: governance",
                "title: Doc Guide",
                "status: active",
                "links: []",
                "---",
                "",
                "# Doc Guide",
            ]
        ),
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (root / "docs" / "dev" / "git.md").write_text("# Git Rules\n", encoding="utf-8")
    (root / "docs" / "dev" / "tasks" / "T-008-cli-entrypoint.md").write_text(
        "\n".join(
            [
                "---",
                "id: T-008",
                "type: task",
                "title: T-008-cli-entrypoint",
                "status: active",
                "plan_ref: PLAN-MAIN",
                "scope:",
                "  in: []",
                "  out: []",
                "references:",
                "  modules: [ARCH-INDEX]",
                "  flows: [PLAN-MAIN]",
                "  schemas: [GOV-CODE-PRINCIPLES]",
                "  governance: [GOV-CODE-PRINCIPLES]",
                "links: [PLAN-MAIN]",
                "---",
                "",
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
    (root / "docs" / "intents" / "I-001-plan-mode.md").write_text(
        "\n".join(
            [
                "---",
                "id: I-001",
                "type: intent",
                "title: plan mode intent",
                "status: active",
                "plan_ref: PLAN-MAIN",
                "task_refs: [T-008]",
                "links: [PLAN-MAIN, T-008, ARCH-INDEX]",
                "---",
                "",
                "# Intent: I-001-plan-mode",
            ]
        ),
        encoding="utf-8",
    )
    config = {
        "docs": {
            "intent": "docs/intent.md",
            "architecture": "docs/architecture.md",
            "plan": "docs/plan.md",
            "doc_map": "docs/dev/doc-index.md",
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

    code_view = main(
        ["plan", "intent", "view", "--intent-id", "I-001"], cwd=tmp_path
    )
    view_output = json.loads(capsys.readouterr().out)
    assert code_view == 0
    assert view_output["ok"] is True
    assert view_output["data"]["intent"]["plan_ref"] == "PLAN-MAIN"

    code_index = main(
        ["plan", "intent", "index", "--intent-id", "I-001"], cwd=tmp_path
    )
    index_output = json.loads(capsys.readouterr().out)
    assert code_index == 0
    assert index_output["ok"] is True
    assert index_output["data"]["intent"]["id"] == "I-001"
    assert index_output["data"]["candidate_tasks"][0]["task_id"] == "T-008"


def test_cli_main_plan_intent_automation_tools(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)

    code_propose = main(
        [
            "plan",
            "intent",
            "propose",
            "--intent-id",
            "I-010",
            "--intent-text",
            "improve planning automation with deterministic task generation",
        ],
        cwd=tmp_path,
    )
    propose_output = json.loads(capsys.readouterr().out)
    assert code_propose == 0
    assert propose_output["ok"] is True
    assert propose_output["data"]["intent"]["id"] == "I-010"

    code_design = main(
        ["plan", "intent", "autodesign", "--intent-id", "I-001"], cwd=tmp_path
    )
    design_output = json.loads(capsys.readouterr().out)
    assert code_design == 0
    assert design_output["ok"] is True
    assert "quality_gate" in design_output["data"]

    code_tasks = main(
        ["plan", "intent", "generate-tasks", "--intent-id", "I-001"], cwd=tmp_path
    )
    tasks_output = json.loads(capsys.readouterr().out)
    assert code_tasks == 0
    assert tasks_output["ok"] is True
    assert "quality_gate" in tasks_output["data"]

    code_bundle = main(
        ["plan", "intent", "review-bundle", "--intent-id", "I-001"], cwd=tmp_path
    )
    bundle_output = json.loads(capsys.readouterr().out)
    assert code_bundle == 0
    assert bundle_output["ok"] is True
    assert bundle_output["data"]["quality_gate"]["approval_required"] is True

    code_bundle_retry = main(
        [
            "plan",
            "intent",
            "review-bundle",
            "--intent-id",
            "I-001",
            "--retry-on-fail",
            "1",
        ],
        cwd=tmp_path,
    )
    bundle_retry_output = json.loads(capsys.readouterr().out)
    assert code_bundle_retry == 0
    assert bundle_retry_output["ok"] is True

    code_apply = main(
        [
            "plan",
            "intent",
            "apply",
            "--intent-id",
            "I-001",
            "--fingerprint",
            bundle_retry_output["data"]["decision_fingerprint"],
            "--retry-on-fail",
            "1",
        ],
        cwd=tmp_path,
    )
    apply_output = json.loads(capsys.readouterr().out)
    assert code_apply == 0
    assert apply_output["ok"] is True
    assert apply_output["data"]["applied"] is False


def test_cli_main_returns_error_code_for_invalid_input(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)
    code = main(["task", "pack", "--task-id", ""], cwd=tmp_path)
    output = json.loads(capsys.readouterr().out)
    assert code == 1
    assert output["ok"] is False
    assert output["error"]["code"] in {"invalid_option", "invalid_input"}


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
