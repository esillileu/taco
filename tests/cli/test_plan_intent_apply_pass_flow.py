from __future__ import annotations

import json
from pathlib import Path

from taco.apps.main import main

from .fixture_repo import _author_task_from_blueprint, _write_fixture_repo


def test_cli_main_plan_intent_review_and_apply_pass_after_authored_task(
    tmp_path: Path, capsys
) -> None:
    _write_fixture_repo(tmp_path)
    plan_path = tmp_path / "docs" / "plan.md"
    plan_text = plan_path.read_text(encoding="utf-8")
    plan_path.write_text(
        plan_text.replace("active_tasks: [T-008]", "active_tasks: []"),
        encoding="utf-8",
    )

    code_propose = main(
        ["plan", "intent", "propose", "--intent-id", "I-001"],
        cwd=tmp_path,
    )
    propose_output = json.loads(capsys.readouterr().out)
    assert code_propose == 0
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
    blueprint = generate_output["data"]["generated_tasks"][0]
    _author_task_from_blueprint(tmp_path, blueprint)

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
            generate_output["data"]["taskset_fingerprint"],
        ],
        cwd=tmp_path,
    )
    review_output = json.loads(capsys.readouterr().out)
    assert code_review == 0
    assert review_output["ok"] is True
    assert review_output["data"]["status"] == "pass"

    code_apply = main(
        [
            "plan",
            "intent",
            "apply",
            "--intent-id",
            "I-001",
            "--decision-fingerprint",
            review_output["data"]["decision_fingerprint"],
            "--approve",
            "--apply",
        ],
        cwd=tmp_path,
    )
    apply_output = json.loads(capsys.readouterr().out)
    assert code_apply == 0
    assert apply_output["ok"] is True
    assert apply_output["data"]["applied"] is True

