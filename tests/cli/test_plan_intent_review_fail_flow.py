from __future__ import annotations

import json
from pathlib import Path

from taco.apps.main import main

from .fixture_repo import _write_fixture_repo


def test_cli_main_plan_intent_validate_and_automation_flow(
    tmp_path: Path, capsys
) -> None:
    _write_fixture_repo(tmp_path)

    code_validate = main(
        [
            "plan",
            "intent",
            "validate",
            "--intent-id",
            "I-001",
        ],
        cwd=tmp_path,
    )
    validate_output = json.loads(capsys.readouterr().out)
    assert code_validate == 0
    assert validate_output["ok"] is True
    assert validate_output["data"]["intent_id"] == "I-001"

    code_propose = main(
        ["plan", "intent", "propose", "--intent-id", "I-001"],
        cwd=tmp_path,
    )
    propose_output = json.loads(capsys.readouterr().out)
    assert code_propose == 0
    assert propose_output["ok"] is True
    proposal_fingerprint = propose_output["data"]["proposal_fingerprint"]

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
    autodesign_output = json.loads(capsys.readouterr().out)
    assert code_autodesign == 0
    assert autodesign_output["ok"] is True
    design_fingerprint = autodesign_output["data"]["design_fingerprint"]

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
    generate_output = json.loads(capsys.readouterr().out)
    assert code_generate == 0
    assert generate_output["ok"] is True
    generated_task = generate_output["data"]["generated_tasks"][0]
    assert "content" not in generated_task
    assert "front_matter_requirements" in generated_task
    taskset_fingerprint = generate_output["data"]["taskset_fingerprint"]

    code_review = main(
        [
            "plan",
            "intent",
            "review-bundle",
            "--intent-id",
            "I-001",
            "--proposal-fingerprint",
            proposal_fingerprint,
            "--design-fingerprint",
            design_fingerprint,
            "--taskset-fingerprint",
            taskset_fingerprint,
            "--retry-on-fail",
            "1",
        ],
        cwd=tmp_path,
    )
    review_output = json.loads(capsys.readouterr().out)
    assert code_review == 0
    assert review_output["ok"] is True
    assert review_output["data"]["status"] == "fail"
    issue_codes = {row["code"] for row in review_output["data"]["issues"]}
    assert "task_lint_failed" in issue_codes

    code_apply_missing_approval = main(
        [
            "plan",
            "intent",
            "apply",
            "--intent-id",
            "I-001",
            "--decision-fingerprint",
            review_output["data"]["decision_fingerprint"],
        ],
        cwd=tmp_path,
    )
    apply_missing_approval_output = json.loads(capsys.readouterr().out)
    assert code_apply_missing_approval == 1
    assert apply_missing_approval_output["ok"] is False
    assert apply_missing_approval_output["error"]["code"] == "approval_required"

    code_apply_with_approval = main(
        [
            "plan",
            "intent",
            "apply",
            "--intent-id",
            "I-001",
            "--decision-fingerprint",
            review_output["data"]["decision_fingerprint"],
            "--approve",
        ],
        cwd=tmp_path,
    )
    apply_with_approval_output = json.loads(capsys.readouterr().out)
    assert code_apply_with_approval == 1
    assert apply_with_approval_output["ok"] is False
    assert apply_with_approval_output["error"]["code"] == "plan_review_failed"

    code_section_get = main(
        [
            "doc",
            "section",
            "get",
            "--path",
            "docs/dev/tasks/T-008-cli-entrypoint.md",
            "--section-id",
            "verification-result",
        ],
        cwd=tmp_path,
    )
    section_output = json.loads(capsys.readouterr().out)
    assert code_section_get == 0
    assert section_output["ok"] is True
