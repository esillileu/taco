from __future__ import annotations

from collections.abc import Callable

from taco.core.indexing import IndexGraph
from taco.core.packing.derive import (
    _collect_action_items,
    _derive_execution_intent,
    _derive_reference_slices,
    _derive_scope_boundary,
    _derive_write_targets,
)
from taco.core.packing.extract import _extract_task_context_requirements
from taco.core.packing.models import (
    BudgetConfig,
    DroppedSnippet,
    PackError,
    PackResult,
    PackSnippet,
    _CandidateSnippet,
    estimate_tokens,
)
from taco.core.packing.select import (
    _build_candidates,
    _build_reference_candidates,
    _find_doc,
)


def build_task_pack(
    task_id: str,
    index: IndexGraph,
    budget: BudgetConfig,
    common_required_refs: tuple[str, ...] = (),
    token_estimator: Callable[[str], int] | None = None,
) -> PackResult:
    estimator = token_estimator or estimate_tokens
    task_path = index.task_index.get(task_id)
    if not task_path:
        raise PackError(
            code="task_not_found",
            message="task id not found in index",
            details={"task_id": task_id},
        )

    task_doc = _find_doc(index.documents, task_path)
    if not task_doc:
        raise PackError(
            code="task_doc_missing",
            message="task document missing from indexed docs",
            details={"task_id": task_id, "path": task_path},
        )

    candidates = _build_candidates(task_id, task_path, index, estimator)
    task_required_refs, task_optional_refs = _extract_task_context_requirements(
        task_doc, index.document_texts
    )
    required_refs = tuple(dict.fromkeys(common_required_refs + task_required_refs))
    ref_candidates, missing_refs = _build_reference_candidates(
        required_refs=required_refs,
        optional_refs=task_optional_refs,
        index=index,
        estimator=estimator,
    )
    candidates.extend(ref_candidates)
    if not candidates:
        raise PackError(
            code="pack_not_ready",
            message="required selector groups are missing",
            details={
                "task_id": task_id,
                "missing_groups": ",".join(sorted(set(budget.required_groups))),
            },
        )

    by_group: dict[str, list[_CandidateSnippet]] = {}
    for item in candidates:
        by_group.setdefault(item.group, []).append(item)

    missing_groups = sorted(set(budget.required_groups) - set(by_group))
    if missing_groups or missing_refs:
        raise PackError(
            code="pack_not_ready",
            message="required pack context is missing",
            details={
                "task_id": task_id,
                "missing_groups": ",".join(missing_groups),
                "missing_refs": ",".join(missing_refs),
            },
        )

    priority_rank = {group: rank for rank, group in enumerate(budget.priority_order)}
    sorted_candidates = sorted(
        candidates,
        key=lambda item: (
            priority_rank.get(item.group, len(priority_rank)),
            item.path,
            item.heading_ref.start_line,
        ),
    )

    used_tokens = 0
    included: list[PackSnippet] = []
    dropped: list[DroppedSnippet] = []
    required_set = set(budget.required_groups)

    for candidate in sorted_candidates:
        is_required = candidate.required or candidate.group in required_set
        next_used = used_tokens + candidate.estimated_tokens
        if is_required or next_used <= budget.default_tokens:
            used_tokens = next_used
            included.append(
                PackSnippet(
                    group=candidate.group,
                    path=candidate.path,
                    heading=candidate.heading_ref.heading,
                    anchor_id=candidate.heading_ref.anchor_id,
                    content=candidate.content,
                    estimated_tokens=candidate.estimated_tokens,
                    reason=candidate.reason,
                )
            )
            continue
        dropped.append(
            DroppedSnippet(
                group=candidate.group,
                path=candidate.path,
                heading=candidate.heading_ref.heading,
                estimated_tokens=candidate.estimated_tokens,
                reason="budget_exceeded",
            )
        )

    next_actions = _collect_action_items(included, "pack.next_actions")
    acceptance_checks = _collect_action_items(included, "pack.acceptance_checks")
    verification_commands = _collect_action_items(
        included, "pack.verification_commands"
    )
    unknowns = tuple(_collect_action_items(included, "pack.unknowns"))
    write_targets = _derive_write_targets(task_doc)
    execution_intent = _derive_execution_intent(task_doc.path, index.document_texts)
    scope_boundary = _derive_scope_boundary(task_doc.path, index.document_texts)
    reference_slices = _derive_reference_slices(included)
    required_outputs = tuple(
        dict.fromkeys(
            [
                str(item.get("path", "")).strip()
                for item in write_targets
                if isinstance(item, dict) and str(item.get("path", "")).strip()
            ]
        )
    )

    return PackResult(
        pack_version="3",
        task_id=task_id,
        execution_intent=execution_intent,
        budget_tokens=budget.default_tokens,
        used_tokens=used_tokens,
        scope_boundary=scope_boundary,
        reference_slices=reference_slices,
        verification_criteria=tuple(acceptance_checks),
        required_outputs=required_outputs,
        next_actions=tuple(next_actions),
        acceptance_checks=tuple(acceptance_checks),
        verification_commands=tuple(verification_commands),
        write_targets=write_targets,
        context_snippets=tuple(included),
        unknowns=unknowns,
        coverage={
            "required_groups": sorted(required_set),
            "missing_groups": missing_groups,
        },
        dropped=tuple(dropped),
    )
