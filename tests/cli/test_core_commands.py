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


def test_cli_main_plan_intent_propose_from_natural_language(
    tmp_path: Path, capsys
) -> None:
    _write_fixture_repo(tmp_path)
    code = main(
        [
            "plan",
            "intent",
            "propose",
            "--intent-text",
            "Add a first-class natural language intake for plan mode.",
            "--title",
            "Natural Language Intake",
        ],
        cwd=tmp_path,
    )
    output = json.loads(capsys.readouterr().out)
    assert code == 0
    assert output["ok"] is True
    assert output["data"]["created_intent"] is True
    assert output["data"]["intent"]["id"] == "I-002"
    assert output["data"]["proposal_fingerprint"]
    assert output["data"]["deprecation"]["code"] == "intent_text_propose_deprecated"
    intent_path = tmp_path / "docs" / "intents" / "I-002-natural-language-intake.md"
    assert intent_path.exists()


def test_cli_main_plan_intent_template_and_create_many(
    tmp_path: Path, capsys
) -> None:
    _write_fixture_repo(tmp_path)

    code_template = main(["plan", "intent", "template"], cwd=tmp_path)
    template_output = json.loads(capsys.readouterr().out)
    assert code_template == 0
    assert template_output["ok"] is True
    assert "front_matter_required" in template_output["data"]

    payload = json.dumps(
        [
            {
                "title": "Split Planner Intake",
                "intent": "Split natural language into decomposition-ready intents.",
                "scope_in": ["plan mode intake", "intent mapping"],
                "scope_out": ["implementation coding"],
            },
            {
                "title": "Strengthen Review Gate",
                "intent": "Require richer design reasoning before apply.",
                "scope_in": ["review gate policy"],
                "scope_out": ["runtime execution"],
            },
        ]
    )
    code_create = main(
        ["plan", "intent", "create-many", "--intents-json", payload],
        cwd=tmp_path,
    )
    create_output = json.loads(capsys.readouterr().out)
    assert code_create == 0
    assert create_output["ok"] is True
    assert create_output["data"]["count"] == 2
    assert create_output["data"]["created"][0]["intent_id"] == "I-002"
    assert create_output["data"]["created"][1]["intent_id"] == "I-003"


def test_cli_main_plan_mode_design_task_submit_flow(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)

    code_guide_1 = main(["plan", "mode", "guide"], cwd=tmp_path)
    guide_1 = json.loads(capsys.readouterr().out)
    assert code_guide_1 == 0
    assert guide_1["ok"] is True
    assert guide_1["data"]["current_stage"] == "intent_decomposition"

    intents_payload = json.dumps(
        [
            {
                "title": "Intent A",
                "intent": "Decompose first planning objective.",
                "scope_in": ["plan intake"],
                "scope_out": ["implementation code"],
            },
            {
                "title": "Intent B",
                "intent": "Decompose second planning objective.",
                "scope_in": ["design sync"],
                "scope_out": ["runtime wiring"],
            },
        ]
    )
    code_submit_intents = main(
        ["plan", "intent", "submit-many", "--intents-json", intents_payload],
        cwd=tmp_path,
    )
    submit_intents = json.loads(capsys.readouterr().out)
    assert code_submit_intents == 0
    assert submit_intents["ok"] is True
    assert submit_intents["data"]["stage_transition"] == "design_change"
    assert submit_intents["data"]["count"] == 2

    section_get = main(
        [
            "doc",
            "section",
            "get",
            "--path",
            "docs/architecture.md",
            "--section-id",
            "system",
        ],
        cwd=tmp_path,
    )
    section_output = json.loads(capsys.readouterr().out)
    assert section_get == 0
    base_fp = section_output["data"]["fingerprint"]
    design_payload = json.dumps(
        [
            {
                "path": "docs/architecture.md",
                "section_id": "system",
                "content": "system detail\\n- boundary rationale documented",
                "base_fingerprint": base_fp,
            }
        ]
    )
    code_design = main(
        ["plan", "design", "submit-changes", "--changes-json", design_payload],
        cwd=tmp_path,
    )
    design_output = json.loads(capsys.readouterr().out)
    assert code_design == 0
    assert design_output["ok"] is True
    assert design_output["data"]["stage_transition"] == "task_authoring"

    task_payload = json.dumps(
        [
            {
                "intent_id": "I-002",
                "front_matter": {
                    "id": "T-900",
                    "type": "task",
                    "title": "T-900-authored-task",
                    "status": "active",
                    "plan_ref": "PLAN-MAIN",
                    "scope": {"in": ["src/taco"], "out": ["non-goal"]},
                    "references": {
                        "modules": ["ARCH-INDEX"],
                        "flows": ["PLAN-MAIN"],
                        "schemas": ["GOV-CODE-PRINCIPLES"],
                    },
                    "links": ["PLAN-MAIN", "ARCH-INDEX", "GOV-CODE-PRINCIPLES"],
                },
                "sections": {
                    "Intent": "Task intent line.",
                    "Goal": "Deliver first reconstruction-ready task.",
                    "Scope": (
                        "In Scope: starter implementation.\\n"
                        "Out of Scope: unrelated runtime."
                    ),
                    "Implementation Approach": (
                        "1. define boundary contract.\\n"
                        "2. apply blueprint constraints."
                    ),
                    "Verification Approach": (
                        "1. run uv run pytest -q\\n"
                        "2. verify review gate passes."
                    ),
                    "Implementation Result": "pending",
                    "Verification Result": "pending",
                },
            }
        ]
    )
    code_task = main(
        ["plan", "task", "submit-many", "--tasks-json", task_payload],
        cwd=tmp_path,
    )
    task_output = json.loads(capsys.readouterr().out)
    assert code_task == 0
    assert task_output["ok"] is True
    assert task_output["data"]["applied_tasks"][0]["task_id"] == "T-900"


def test_cli_main_plan_task_template_sync_and_lint(tmp_path: Path, capsys) -> None:
    _write_fixture_repo(tmp_path)

    code_propose = main(
        ["plan", "intent", "propose", "--intent-id", "I-001"],
        cwd=tmp_path,
    )
    propose = json.loads(capsys.readouterr().out)
    assert code_propose == 0
    proposal_fingerprint = propose["data"]["proposal_fingerprint"]

    code_autodesign = main(
        [
            "plan",
            "intent",
            "autodesign",
            "--intent-id",
            "I-001",
            "--proposal-fingerprint",
            proposal_fingerprint,
        ],
        cwd=tmp_path,
    )
    autodesign = json.loads(capsys.readouterr().out)
    assert code_autodesign == 0
    design_fingerprint = autodesign["data"]["design_fingerprint"]

    code_generate = main(
        [
            "plan",
            "intent",
            "generate-tasks",
            "--intent-id",
            "I-001",
            "--design-fingerprint",
            design_fingerprint,
        ],
        cwd=tmp_path,
    )
    generate = json.loads(capsys.readouterr().out)
    assert code_generate == 0
    path = generate["data"]["generated_tasks"][0]["path"]

    code_template = main(
        ["plan", "task", "template", "--intent-id", "I-001"],
        cwd=tmp_path,
    )
    template = json.loads(capsys.readouterr().out)
    assert code_template == 0
    assert template["ok"] is True
    assert template["data"]["authoring_required"] is True

    authored = "\n".join(
        [
            "# Task: authored",
            "",
            "## Intent",
            "Author task body for lint pass.",
            "",
            "## Goal",
            "Provide first executable task.",
            "",
            "## Scope",
            "In Scope: plan workflow update.",
            "Out of Scope: runtime feature work.",
            "",
            "## Implementation Approach",
            "1. Define hexagonal boundary contract for this task.",
            "2. Keep adapter interface stable and explicit.",
            "",
            "## Verification Approach",
            "1. run uv run pytest -q",
            "2. verify review_bundle status is pass",
            "",
            "## Implementation Result",
            "pending",
            "",
            "## Verification Result",
            "pending",
            "",
        ]
    )
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(authored, encoding="utf-8")

    override = json.dumps({"scope": {"out": ["non-goal: unrelated runtime"]}})
    code_sync = main(
        [
            "plan",
            "task",
            "sync-frontmatter",
            "--intent-id",
            "I-001",
            "--path",
            path,
            "--front-matter-json",
            override,
        ],
        cwd=tmp_path,
    )
    sync_output = json.loads(capsys.readouterr().out)
    assert code_sync == 0
    assert sync_output["ok"] is True

    code_lint = main(
        ["plan", "task", "lint", "--path", path, "--intent-id", "I-001"],
        cwd=tmp_path,
    )
    lint_output = json.loads(capsys.readouterr().out)
    assert code_lint == 0
    assert lint_output["ok"] is True
    assert lint_output["data"]["valid"] is True
