from __future__ import annotations

from pathlib import Path

from taco.apps.composition import RepoState
from taco.core.indexing import build_index
from taco.core.packing import BudgetConfig
from taco.core.routing import RouterConfig

from .fixture_state_docs import build_state_documents, state_index_config


def _state(tmp_path: Path) -> RepoState:
    index = build_index(build_state_documents(), state_index_config())
    return RepoState(
        root=tmp_path,
        config_raw={
            "docs": {"plan": "docs/plan.md", "doc_map": "docs/dev/doc-index.md"},
            "modules": {"git": {"path": "docs/dev/git.md"}},
        },
        index=index,
        budget_config=BudgetConfig(
            default_tokens=200,
            priority_order=(
                "task.core",
                "task.plans",
                "arch.snippets",
                "principles.snippets",
                "glossary.terms",
            ),
            required_groups=(
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ),
        ),
        router_config=RouterConfig.default(),
        required_refs_by_tool={
            "plan.pack": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
            "plan.intent.index": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
            "task.pack": ("GOV-CODE-PRINCIPLES",),
        },
    )
