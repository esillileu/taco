from __future__ import annotations

from typing import Any

from taco.core.plan import RepoState, ToolError
from taco.core.task.pack import _task_pack_readiness_missing

from .intent_pipeline import build_intent_pipeline_bundle


def review_issues(
    state: RepoState,
    bundle: dict[str, Any],
    *,
    proposal_fingerprint: str,
    design_fingerprint: str,
    taskset_fingerprint: str,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if proposal_fingerprint != str(bundle.get("proposal_fingerprint", "")):
        issues.append({"code": "proposal_fingerprint_mismatch"})
    if design_fingerprint != str(bundle.get("design_fingerprint", "")):
        issues.append({"code": "design_fingerprint_mismatch"})
    if taskset_fingerprint != str(bundle.get("taskset_fingerprint", "")):
        issues.append({"code": "taskset_fingerprint_mismatch"})

    generated = bundle.get("generated_tasks", [])
    if isinstance(generated, list):
        for row in generated:
            if not isinstance(row, dict):
                continue
            task_id = str(row.get("task_id", "")).strip()
            task_path = str(row.get("path", "")).strip()
            indexed_path = state.index.task_index.get(task_id, "")
            if not indexed_path:
                issues.append(
                    {
                        "code": "task_blueprint_not_authored",
                        "task_id": task_id,
                        "path": task_path,
                    }
                )
                continue
            if task_path and indexed_path != task_path:
                issues.append(
                    {
                        "code": "task_blueprint_path_mismatch",
                        "task_id": task_id,
                        "expected_path": task_path,
                        "actual_path": indexed_path,
                    }
                )
                continue
            missing = _task_pack_readiness_missing(state, task_id)
            filtered = [
                item
                for item in missing
                if item not in {"task_not_found", "task_doc_missing"}
            ]
            if filtered:
                issues.append(
                    {
                        "code": "task_not_ready_for_build",
                        "task_id": task_id,
                        "missing_requirements": filtered,
                    }
                )

    if not generated and not bundle.get("task_refs", []):
        issues.append({"code": "no_executable_tasks"})
    return issues


def plan_intent_review_bundle(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    intent_id = str(args["intent_id"])
    proposal_fingerprint = str(args["proposal_fingerprint"])
    design_fingerprint = str(args["design_fingerprint"])
    taskset_fingerprint = str(args["taskset_fingerprint"])
    retry_on_fail = args.get("retry_on_fail", 0)
    if not isinstance(retry_on_fail, int):
        raise ToolError(
            "invalid_input", "retry_on_fail must be integer", {"key": "retry_on_fail"}
        )

    bundle = build_intent_pipeline_bundle(state, intent_id)
    issues = review_issues(
        state,
        bundle,
        proposal_fingerprint=proposal_fingerprint,
        design_fingerprint=design_fingerprint,
        taskset_fingerprint=taskset_fingerprint,
    )

    attempted_retry = False
    retry_result: dict[str, Any] | None = None
    if issues and retry_on_fail == 1:
        attempted_retry = True
        retry_bundle = build_intent_pipeline_bundle(state, intent_id)
        retry_issues = review_issues(
            state,
            retry_bundle,
            proposal_fingerprint=proposal_fingerprint,
            design_fingerprint=design_fingerprint,
            taskset_fingerprint=taskset_fingerprint,
        )
        retry_result = {
            "issues_after_retry": retry_issues,
            "status_after_retry": "pass" if not retry_issues else "fail",
        }
        if not retry_issues:
            bundle = retry_bundle
            issues = []

    return {
        "intent_id": intent_id,
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "decision_fingerprint": bundle["decision_fingerprint"],
        "retry": {
            "attempted": attempted_retry,
            "max_retry": 1 if retry_on_fail == 1 else 0,
            "result": retry_result or {},
        },
    }
