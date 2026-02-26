from __future__ import annotations

from pathlib import Path

from taco.apps.composition import call_tool

from .fixture_state import _state, _state_with_refactor_intent


def test_plan_intent_index_reports_refactor_analysis(tmp_path: Path) -> None:
    state = _state_with_refactor_intent(tmp_path)
    indexed = call_tool(state, "plan.intent.index", {"intent_id": "I-020"})
    assert indexed["ok"] is True
    analysis = indexed["data"]["analysis"]
    assert analysis["required"] is True
    assert analysis["completed"] is True
    assert analysis["oversized_file_count"] >= 1
    validated = call_tool(state, "plan.intent.validate", {"intent_id": "I-020"})
    assert validated["ok"] is True


def test_doc_snippet_issue_triage_and_convention(tmp_path: Path) -> None:
    state = _state(tmp_path)
    snippet = call_tool(
        state,
        "doc.snippet",
        {"path": "docs/architecture.md", "anchor_id": "system"},
    )
    assert snippet["ok"] is True
    assert "System" in snippet["data"]["snippet"]

    triage = call_tool(state, "issue.triage", {"title": "fix broken parser"})
    assert triage["ok"] is True
    assert triage["data"]["type"] == "Fix"

    convention = call_tool(state, "convention.get", {"topic": "git"})
    assert convention["ok"] is True
    assert convention["data"]["path"] == "docs/dev/git.md"

    plan_view = call_tool(state, "plan.view", {})
    assert plan_view["ok"] is True
    assert "plan" in plan_view["data"]

    plan_locate = call_tool(
        state,
        "plan.locate",
        {"change_type": "task", "target": "T-005"},
    )
    assert plan_locate["ok"] is True
    assert plan_locate["data"]["count"] >= 1
    plan_locate_intent = call_tool(
        state,
        "plan.locate",
        {"change_type": "intent", "target": "I-001"},
    )
    assert plan_locate_intent["ok"] is True
    assert plan_locate_intent["data"]["count"] >= 1

    plan_validate = call_tool(state, "plan.validate", {})
    assert plan_validate["ok"] is True
    assert "valid" in plan_validate["data"]


def test_doc_section_patch_and_build_checks(tmp_path: Path) -> None:
    state = _state(tmp_path)
    task_path = state.index.task_index["T-005"]
    section = call_tool(
        state,
        "doc.section.get",
        {
            "path": task_path,
            "section_id": "implementation-result",
        },
    )
    assert section["ok"] is True
    patched = call_tool(
        state,
        "doc.section.patch",
        {
            "path": task_path,
            "section_id": "implementation-result",
            "base_fingerprint": section["data"]["fingerprint"],
            "ops": [{"op": "append_list_item", "text": "updated from test"}],
            "dry_run": True,
            "mode": "build",
        },
    )
    assert patched["ok"] is False
    assert patched["error"]["code"] == "storage_unavailable"

    packed = call_tool(state, "task.pack", {"task_id": "T-005"})
    assert packed["ok"] is True
    pre = call_tool(state, "build.precheck", {"pack": packed["data"]})
    assert pre["ok"] is True
    post = call_tool(
        state,
        "build.postcheck",
        {
            "pack": packed["data"],
            "changed_paths": [],
            "produced_outputs": [task_path],
            "check_results": {"tests": True},
        },
    )
    assert post["ok"] is True


def test_build_postcheck_returns_drift_report_details(tmp_path: Path) -> None:
    state = _state(tmp_path)
    packed = call_tool(state, "task.pack", {"task_id": "T-005"})
    assert packed["ok"] is True

    post = call_tool(
        state,
        "build.postcheck",
        {
            "pack": packed["data"],
            "changed_paths": ["src/outside_scope.py"],
            "produced_outputs": [],
            "check_results": {"tests": True},
        },
    )
    assert post["ok"] is False
    assert post["error"]["code"] == "missing_required_fields"
    details = post["error"]["details"]
    assert details["task_id"] == "T-005"
    assert details["failed_rule"] == "missing_required_outputs"
    assert details["changed_paths_snapshot"] == ["src/outside_scope.py"]
    assert "suggested_plan_actions" in details


def test_build_postcheck_allows_declared_outputs_even_if_outside_scope(
    tmp_path: Path,
) -> None:
    state = _state(tmp_path)
    packed = call_tool(state, "task.pack", {"task_id": "T-005"})
    assert packed["ok"] is True
    task_path = state.index.task_index["T-005"]

    post = call_tool(
        state,
        "build.postcheck",
        {
            "pack": packed["data"],
            "changed_paths": [task_path],
            "produced_outputs": [task_path],
            "check_results": [],
        },
    )
    assert post["ok"] is True
    assert task_path in post["data"]["ignored_declared_outputs"]


def test_build_postcheck_supports_list_check_results(tmp_path: Path) -> None:
    state = _state(tmp_path)
    packed = call_tool(state, "task.pack", {"task_id": "T-005"})
    assert packed["ok"] is True
    task_path = state.index.task_index["T-005"]

    post = call_tool(
        state,
        "build.postcheck",
        {
            "pack": packed["data"],
            "changed_paths": [task_path],
            "produced_outputs": [task_path],
            "check_results": [
                {"command": "uv run pytest -q", "passed": True},
                {"command": "uv run ruff check .", "passed": False},
            ],
        },
    )
    assert post["ok"] is False
    assert post["error"]["code"] == "mode_transition_blocked"
    assert post["error"]["details"]["failed_checks"] == ["uv run ruff check ."]


def test_task_record_dry_run_preview(tmp_path: Path) -> None:
    state = _state(tmp_path)
    result = call_tool(
        state,
        "task.record",
        {
            "task_id": "T-005",
            "route_type": "verification_result",
            "content": "validated behavior",
            "dry_run": True,
        },
    )
    assert result["ok"] is True
    assert result["data"]["applied"] is False
    assert result["data"]["preview"] == "- validated behavior"
