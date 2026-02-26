from __future__ import annotations

from pathlib import Path

import yaml

from taco.apps.composition import build_repo_state as load_repo_state
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
    assert "task_blueprint_not_authored" in issue_codes
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


def test_task_pack_auto_selects_active_task(tmp_path: Path) -> None:
    state = _state(tmp_path)
    plan_path = state.config_raw["docs"]["plan"]
    current = state.index.document_texts[plan_path]
    state.index.document_texts[plan_path] = current.replace(
        "active_tasks: []",
        "active_tasks:\n  - T-005",
    )

    packed = call_tool(state, "task.pack", {})
    assert packed["ok"] is True
    assert packed["data"]["task_id"] == "T-005"


def test_task_pack_auto_selects_next_task(tmp_path: Path) -> None:
    state = _state(tmp_path)
    plan_path = state.config_raw["docs"]["plan"]
    current = state.index.document_texts[plan_path]
    state.index.document_texts[plan_path] = current.replace(
        "next_tasks: []",
        "next_tasks:\n  - T-005",
    )

    packed = call_tool(state, "task.pack", {})
    assert packed["ok"] is True
    assert packed["data"]["task_id"] == "T-005"


def test_task_pack_auto_select_fails_when_no_task_available(tmp_path: Path) -> None:
    state = _state(tmp_path)
    packed = call_tool(state, "task.pack", {})
    assert packed["ok"] is False
    assert packed["error"]["code"] == "no_task_available"


def test_task_pack_auto_select_fails_when_active_is_ambiguous(tmp_path: Path) -> None:
    state = _state(tmp_path)
    plan_path = state.config_raw["docs"]["plan"]
    current = state.index.document_texts[plan_path]
    state.index.document_texts[plan_path] = current.replace(
        "active_tasks: []",
        "active_tasks:\n  - T-005\n  - T-006",
    )

    packed = call_tool(state, "task.pack", {})
    assert packed["ok"] is False
    assert packed["error"]["code"] == "ambiguous_active_tasks"


def test_task_pack_fails_when_readiness_requirements_missing(tmp_path: Path) -> None:
    (tmp_path / "docs" / "dev" / "tasks").mkdir(parents=True)
    (tmp_path / "docs" / "dev").mkdir(exist_ok=True)
    (tmp_path / "docs" / "intent.md").write_text("# Intent\n", encoding="utf-8")
    (tmp_path / "docs" / "architecture.md").write_text(
        "# Architecture\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (tmp_path / "docs" / "glossary.md").write_text("# Glossary\n", encoding="utf-8")
    (tmp_path / "docs" / "dev" / "principles.md").write_text(
        "# Principles\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "dev" / "doc-index.md").write_text(
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
    (tmp_path / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (tmp_path / "docs" / "dev" / "tasks" / "T-099-not-ready.md").write_text(
        "\n".join(
            [
                "---",
                "id: T-099",
                "type: task",
                "title: T-099-not-ready",
                "status: todo",
                "plan_ref: PLAN-MAIN",
                "scope:",
                "  in: []",
                "references:",
                "  modules: []",
                "  flows: []",
                "  schemas: []",
                "---",
                "",
                "# Task: T-099-not-ready",
                "## Intent",
                "intent",
                "## Goal",
                "goal",
                "## Scope",
                "scope",
                "## Implementation Approach",
                "plan",
                "## Verification Approach",
                "Pending definition.",
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
            "doc_map": "docs/dev/doc-index.md",
            "glossary": "docs/glossary.md",
            "principles": ["docs/dev/principles.md"],
            "todo": ["docs/dev/todo.md"],
            "tasks_glob": "docs/dev/tasks/T-*.md",
        },
        "budget": {
            "default_tokens": 50,
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
        "pack": {
            "required_refs_by_tool": {
                "plan_pack": ["ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"],
                "task_pack": ["GOV-CODE-PRINCIPLES"],
            }
        },
    }
    (tmp_path / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    state = load_repo_state(tmp_path)
    packed = call_tool(state, "task.pack", {"task_id": "T-099"})
    assert packed["ok"] is False
    assert packed["error"]["code"] == "placeholder_detected"
