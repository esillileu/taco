from __future__ import annotations

from pathlib import Path

from taco.apps.composition import call_tool

from .fixture_state import _state


def test_call_tool_unknown_returns_error(tmp_path: Path) -> None:
    state = _state(tmp_path)
    response = call_tool(state, "unknown.tool", {})
    assert response["ok"] is False
    assert response["error"]["code"] == "unknown_tool"


def test_task_list_and_pack_and_targets(tmp_path: Path) -> None:
    state = _state(tmp_path)
    listed = call_tool(state, "task.list", {})
    assert listed["ok"] is True
    assert listed["data"]["tasks"][0]["task_id"] == "T-005"

    packed = call_tool(state, "task.pack", {"task_id": "T-005"})
    assert packed["ok"] is True
    assert packed["data"]["task_id"] == "T-005"
    plan_packed = call_tool(state, "plan.pack", {"task_id": "T-005"})
    assert plan_packed["ok"] is True
    assert plan_packed["data"]["task_id"] == "T-005"
    plan_intent_listed = call_tool(state, "plan.intent.list", {})
    assert plan_intent_listed["ok"] is True
    assert plan_intent_listed["data"]["count"] == 1
    mode_guide = call_tool(state, "plan.mode.guide", {})
    assert mode_guide["ok"] is True
    assert mode_guide["data"]["current_stage"] == "intent_decomposition"
    templated = call_tool(state, "plan.intent.template", {})
    assert templated["ok"] is True
    assert "front_matter_required" in templated["data"]
    plan_intent_viewed = call_tool(state, "plan.intent.view", {"intent_id": "I-001"})
    assert plan_intent_viewed["ok"] is True
    assert plan_intent_viewed["data"]["intent"]["task_refs"] == ["T-005"]
    plan_intent_indexed = call_tool(state, "plan.intent.index", {"intent_id": "I-001"})
    assert plan_intent_indexed["ok"] is True
    assert plan_intent_indexed["data"]["intent"]["id"] == "I-001"
    assert plan_intent_indexed["data"]["candidate_tasks"][0]["task_id"] == "T-005"
    proposed = call_tool(state, "plan.intent.propose", {"intent_id": "I-001"})
    assert proposed["ok"] is True
    assert proposed["data"]["proposal_fingerprint"]
    designed = call_tool(
        state,
        "plan.intent.autodesign",
        {
            "intent_id": "I-001",
            "proposal_fingerprint": proposed["data"]["proposal_fingerprint"],
        },
    )
    assert designed["ok"] is True
    generated = call_tool(
        state,
        "plan.intent.generate_tasks",
        {
            "intent_id": "I-001",
            "design_fingerprint": designed["data"]["design_fingerprint"],
        },
    )
    assert generated["ok"] is True
    generated_task = generated["data"]["generated_tasks"][0]
    assert "content" not in generated_task
    assert "front_matter_requirements" in generated_task
    assert "section_requirements" in generated_task
    assert "readiness_requirements" in generated_task
    templated_task = call_tool(state, "plan.task.template", {"intent_id": "I-001"})
    assert templated_task["ok"] is True
    linted_missing = call_tool(
        state,
        "plan.task.lint",
        {"path": generated_task["path"], "intent_id": "I-001"},
    )
    assert linted_missing["ok"] is True
    assert linted_missing["data"]["valid"] is False
    reviewed = call_tool(
        state,
        "plan.intent.review_bundle",
        {
            "intent_id": "I-001",
            "proposal_fingerprint": proposed["data"]["proposal_fingerprint"],
            "design_fingerprint": designed["data"]["design_fingerprint"],
            "taskset_fingerprint": generated["data"]["taskset_fingerprint"],
            "retry_on_fail": 1,
        },
    )
    assert reviewed["ok"] is True
    assert reviewed["data"]["status"] == "fail"
    issue_codes = {row["code"] for row in reviewed["data"]["issues"]}
    assert "task_lint_failed" in issue_codes
    apply_missing_approval = call_tool(
        state,
        "plan.intent.apply",
        {
            "intent_id": "I-001",
            "decision_fingerprint": reviewed["data"]["decision_fingerprint"],
            "dry_run": True,
        },
    )
    assert apply_missing_approval["ok"] is False
    assert apply_missing_approval["error"]["code"] == "approval_required"
    applied_preview = call_tool(
        state,
        "plan.intent.apply",
        {
            "intent_id": "I-001",
            "decision_fingerprint": reviewed["data"]["decision_fingerprint"],
            "approve": True,
            "dry_run": True,
        },
    )
    assert applied_preview["ok"] is False
    assert applied_preview["error"]["code"] == "plan_review_failed"
    validated = call_tool(state, "plan.intent.validate", {"intent_id": "I-001"})
    assert validated["ok"] is True

    target = call_tool(
        state,
        "task.targets",
        {"task_id": "T-005", "route_type": "implementation_result"},
    )
    assert target["ok"] is True
    assert target["data"]["heading"] == "Implementation Result"
