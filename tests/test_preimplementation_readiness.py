from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_no_stale_tool_names_in_active_docs() -> None:
    targets = [
        "README.md",
        "AGENTS.md",
        ".context/project/overview.md",
        ".context/project/architecture/index.md",
        ".context/governance/doc/index.md",
        ".context/project/tasks/T-005-mcp-tools.md",
    ]
    stale_patterns = [
        r"\btasks\.(list|get_pack|write_targets|record)\b",
        r"\bdocs\.(get_snippet)\b",
        r"\bissues\.(triage)\b",
        r"\bconventions\.(get)\b",
    ]
    for path in targets:
        text = _read(path)
        for pattern in stale_patterns:
            assert re.search(pattern, text) is None, f"stale name in {path}: {pattern}"


def test_no_placeholder_markers_in_active_task_plans() -> None:
    for task_id in range(1, 8):
        text = _read(
            f".context/project/tasks/T-{task_id:03d}-" + _task_slug(task_id) + ".md"
        )
        assert "TBD" not in text
        assert "Planning placeholder" not in text


def test_architecture_and_principles_reflect_runtime_strategy() -> None:
    architecture = _read(".context/project/architecture/index.md")
    principles = _read(".context/governance/code-principles.md")

    assert "Python" in architecture
    assert "Rust" in architecture
    assert "Python-first" in principles
    assert "Rust-final" in principles


def test_dogfooding_policy_is_explicitly_documented() -> None:
    architecture = _read(".context/project/architecture/index.md")
    principles = _read(".context/governance/code-principles.md")
    assert "flow" in architecture.lower()
    assert "dogfooding" in principles.lower()


def test_agents_loader_first_names_are_current() -> None:
    agents = _read("AGENTS.md")
    assert "`task.pack`" in agents
    assert "`task.targets`" in agents
    assert "`doc.snippet`" in agents


def _task_slug(task_id: int) -> str:
    slugs = {
        1: "parser-foundation",
        2: "indexer-foundation",
        3: "pack-budget",
        4: "write-target-router",
        5: "mcp-tools",
        6: "integration-tests",
        7: "pre-implementation-readiness",
    }
    return slugs[task_id]
