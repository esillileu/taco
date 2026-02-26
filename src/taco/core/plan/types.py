from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from taco.core.indexing import IndexGraph
from taco.core.packing import BudgetConfig
from taco.core.routing.router import RouterConfig
from taco.ports import RepositoryPort, StoragePort


@dataclass(frozen=True)
class RepoState:
    root: Path
    config_raw: dict[str, Any]
    index: IndexGraph
    budget_config: BudgetConfig
    router_config: RouterConfig
    required_refs_by_tool: dict[str, tuple[str, ...]]
    task_required_headings: tuple[str, ...] = ()
    storage: StoragePort | None = None
    repository: RepositoryPort | None = None

class ToolError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, Any] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)
