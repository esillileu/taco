from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from taco.core.indexing import HeadingRef


@dataclass(frozen=True)
class BudgetConfig:
    default_tokens: int
    priority_order: tuple[str, ...]
    required_groups: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> BudgetConfig:
        budget = raw.get("budget")
        if not isinstance(budget, dict):
            raise PackError("invalid_config", "budget config must be an object", {})
        default_tokens = budget.get("default_tokens")
        priority_order = budget.get("priority_order")
        required_groups = budget.get(
            "required_groups",
            [
                "task.core",
                "task.plans",
                "pack.next_actions",
                "pack.acceptance_checks",
                "pack.verification_commands",
            ],
        )
        if not isinstance(default_tokens, int):
            raise PackError(
                "invalid_config",
                "budget.default_tokens must be an integer",
                {"key": "default_tokens"},
            )
        if not isinstance(priority_order, list) or not all(
            isinstance(item, str) for item in priority_order
        ):
            raise PackError(
                "invalid_config",
                "budget.priority_order must be a list of strings",
                {"key": "priority_order"},
            )
        if not isinstance(required_groups, list) or not all(
            isinstance(item, str) for item in required_groups
        ):
            raise PackError(
                "invalid_config",
                "budget.required_groups must be a list of strings",
                {"key": "required_groups"},
            )
        return cls(
            default_tokens=default_tokens,
            priority_order=tuple(priority_order),
            required_groups=tuple(required_groups),
        )

@dataclass(frozen=True)
class PackSnippet:
    group: str
    path: str
    heading: str
    anchor_id: str
    content: str
    estimated_tokens: int
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(frozen=True)
class DroppedSnippet:
    group: str
    path: str
    heading: str
    estimated_tokens: int
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(frozen=True)
class PackResult:
    pack_version: str
    task_id: str
    execution_intent: str
    budget_tokens: int
    used_tokens: int
    scope_boundary: dict[str, tuple[str, ...]]
    reference_slices: tuple[dict[str, str], ...]
    verification_criteria: tuple[str, ...]
    required_outputs: tuple[str, ...]
    next_actions: tuple[str, ...]
    acceptance_checks: tuple[str, ...]
    verification_commands: tuple[str, ...]
    write_targets: tuple[dict[str, str | int], ...]
    context_snippets: tuple[PackSnippet, ...]
    unknowns: tuple[str, ...]
    coverage: dict[str, list[str]]
    dropped: tuple[DroppedSnippet, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "pack_version": self.pack_version,
            "task_id": self.task_id,
            "execution_intent": self.execution_intent,
            "budget_tokens": self.budget_tokens,
            "used_tokens": self.used_tokens,
            "scope_boundary": {
                "allowed_paths": list(self.scope_boundary["allowed_paths"]),
                "forbidden_paths": list(self.scope_boundary["forbidden_paths"]),
            },
            "reference_slices": [dict(item) for item in self.reference_slices],
            "verification_criteria": list(self.verification_criteria),
            "required_outputs": list(self.required_outputs),
            "next_actions": list(self.next_actions),
            "acceptance_checks": list(self.acceptance_checks),
            "verification_commands": list(self.verification_commands),
            "write_targets": list(self.write_targets),
            "context_snippets": [
                snippet.to_dict() for snippet in self.context_snippets
            ],
            "unknowns": list(self.unknowns),
            "coverage": self.coverage,
            "dropped": [item.to_dict() for item in self.dropped],
        }

class PackError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)

def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"\S+", text)))

@dataclass(frozen=True)
class _CandidateSnippet:
    group: str
    path: str
    heading_ref: HeadingRef
    content: str
    estimated_tokens: int
    reason: str
    required: bool
