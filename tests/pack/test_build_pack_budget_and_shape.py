from __future__ import annotations

from taco.core.packing import build_task_pack

from .fixture_graph import budget, build_graph


def test_build_task_pack_resolves_context_requirement_refs() -> None:
    graph = build_graph()
    result = build_task_pack("T-003", graph, budget(default_tokens=200))
    ref_reasons = [
        item.reason
        for item in result.context_snippets
        if item.reason == "context_requirement"
    ]
    assert len(ref_reasons) >= 3


def test_build_task_pack_respects_budget_boundaries() -> None:
    graph = build_graph()
    high_budget = build_task_pack("T-003", graph, budget(default_tokens=200))
    low_budget = build_task_pack("T-003", graph, budget(default_tokens=5))
    equal_budget = build_task_pack(
        "T-003", graph, budget(default_tokens=low_budget.used_tokens)
    )

    assert len(low_budget.dropped) > 0
    assert low_budget.used_tokens >= 5
    assert equal_budget.used_tokens >= low_budget.used_tokens
    assert len(high_budget.context_snippets) >= len(equal_budget.context_snippets)


def test_build_task_pack_order_is_stable() -> None:
    graph = build_graph()
    first = build_task_pack("T-003", graph, budget(default_tokens=200)).to_dict()
    second = build_task_pack("T-003", graph, budget(default_tokens=200)).to_dict()
    assert first == second


def test_build_task_pack_matches_golden_shape() -> None:
    graph = build_graph()
    result = build_task_pack("T-003", graph, budget(default_tokens=20)).to_dict()
    assert set(result.keys()) == {
        "pack_version",
        "task_id",
        "execution_intent",
        "budget_tokens",
        "used_tokens",
        "scope_boundary",
        "reference_slices",
        "verification_criteria",
        "required_outputs",
        "next_actions",
        "acceptance_checks",
        "verification_commands",
        "write_targets",
        "context_snippets",
        "unknowns",
        "coverage",
        "dropped",
    }
    assert result["task_id"] == "T-003"
    assert isinstance(result["context_snippets"], list)
    assert isinstance(result["dropped"], list)

