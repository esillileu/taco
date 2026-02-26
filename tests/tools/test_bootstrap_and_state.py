from __future__ import annotations

from pathlib import Path

import yaml

from taco.apps.composition import build_repo_state as load_repo_state
from taco.apps.composition import call_bootstrap_tool, call_tool


def test_load_repo_state_from_config(tmp_path: Path) -> None:
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
    (tmp_path / "docs" / "dev" / "todo.md").write_text("# Todo\n", encoding="utf-8")
    (tmp_path / "docs" / "dev" / "tasks" / "T-001-sample.md").write_text(
        "# Task: T-001-sample\n", encoding="utf-8"
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
    }
    (tmp_path / "taco.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

    state = load_repo_state(tmp_path)
    assert state.budget_config.default_tokens == 50
    assert state.required_refs_by_tool["plan.pack"] == (
        "ARCH-INDEX",
        "PLAN-MAIN",
        "GOV-DOC-INDEX",
    )
    assert state.required_refs_by_tool["plan.intent.index"] == (
        "ARCH-INDEX",
        "PLAN-MAIN",
        "GOV-DOC-INDEX",
    )
    assert state.required_refs_by_tool["task.pack"] == ("GOV-CODE-PRINCIPLES",)


def test_project_init_bootstrap_generates_minimal_context(tmp_path: Path) -> None:
    response = call_bootstrap_tool(tmp_path, "project.init", {})
    assert response["ok"] is True
    data = response["data"]
    assert data["policy"] == "fail_on_existing"
    assert ".context/project/overview.md" in data["created_files"]
    assert ".context/project/intents/index.md" in data["created_files"]
    assert ".context/project/plan.md" in data["created_files"]
    assert ".context/project/architecture/index.md" in data["created_files"]
    assert ".context/governance/code-principles.md" in data["created_files"]
    assert ".context/governance/git/index.md" in data["created_files"]
    assert ".context/governance/doc/index.md" in data["created_files"]
    assert (tmp_path / "taco.yaml").exists()

    state = load_repo_state(tmp_path)
    validated = call_tool(state, "plan.validate", {})
    assert validated["ok"] is True
    assert validated["data"]["valid"] is True

    second = call_bootstrap_tool(tmp_path, "project.init", {})
    assert second["ok"] is False
    assert second["error"]["code"] == "init_target_exists"
