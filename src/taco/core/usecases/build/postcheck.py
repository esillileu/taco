from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from taco.core.plan import RepoState, ToolError, _required_str, _validate_pack_v3
from taco.core.usecases.build.diagnostics import build_drift_details


def _build_postcheck(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    pack = args.get("pack")
    if not isinstance(pack, dict):
        raise ToolError("invalid_input", "pack must be an object", {"key": "pack"})
    _validate_pack_v3(pack)
    task_id = _required_str(pack, "task_id")

    changed_paths = _read_changed_paths(state, args)
    produced_outputs = _read_path_list(args.get("produced_outputs"), "produced_outputs")
    check_results = args.get("check_results", {})

    required_outputs = _pack_required_outputs(pack)
    missing_required_outputs = sorted(set(required_outputs) - set(produced_outputs))
    if missing_required_outputs:
        raise ToolError(
            "missing_required_fields",
            "required outputs are missing from produced_outputs",
            build_drift_details(
                task_id=task_id,
                failed_rule="missing_required_outputs",
                changed_paths=changed_paths,
                extra={"missing_required_outputs": missing_required_outputs},
            ),
        )

    ignored_declared_outputs = sorted(
        path for path in changed_paths if path in set(required_outputs)
    )
    boundary_violations = _scope_boundary_violations(
        changed_paths=changed_paths,
        pack=pack,
        ignored_paths=set(ignored_declared_outputs),
    )
    if boundary_violations:
        raise ToolError(
            "mode_transition_blocked",
            "changed paths exceed task scope boundary",
            build_drift_details(
                task_id=task_id,
                failed_rule="task_scope_violation",
                changed_paths=changed_paths,
                extra={"violations": boundary_violations},
            ),
        )

    failed_checks = _failed_checks(check_results)
    if failed_checks:
        raise ToolError(
            "mode_transition_blocked",
            "verification checks failed",
            build_drift_details(
                task_id=task_id,
                failed_rule="verification_failed",
                changed_paths=changed_paths,
                extra={"failed_checks": failed_checks},
            ),
        )

    return {
        "task_id": task_id,
        "status": "ok",
        "changed_paths": changed_paths,
        "produced_outputs": produced_outputs,
        "ignored_declared_outputs": ignored_declared_outputs,
    }


def _read_changed_paths(state: RepoState, args: dict[str, Any]) -> list[str]:
    raw = args.get("changed_paths")
    if raw is None:
        if state.repository is None:
            return []
        raw = state.repository.changed_paths()
    return _read_path_list(raw, "changed_paths")


def _read_path_list(value: Any, key: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ToolError("invalid_input", f"{key} must be a list", {"key": key})
    items: list[str] = []
    for idx, row in enumerate(value):
        if not isinstance(row, str):
            raise ToolError(
                "invalid_input",
                f"{key} items must be strings",
                {"key": key, "index": idx},
            )
        text = row.strip()
        if text:
            items.append(text)
    return items


def _pack_required_outputs(pack: dict[str, Any]) -> list[str]:
    raw = pack.get("required_outputs")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ToolError(
            "invalid_input",
            "required_outputs must be a list in pack payload",
            {"key": "required_outputs"},
        )
    items: list[str] = []
    for idx, row in enumerate(raw):
        if not isinstance(row, str):
            raise ToolError(
                "invalid_input",
                "required_outputs items must be strings",
                {"key": "required_outputs", "index": idx},
            )
        text = row.strip()
        if text:
            items.append(text)
    return items


def _scope_boundary_violations(
    *,
    changed_paths: list[str],
    pack: dict[str, Any],
    ignored_paths: set[str],
) -> list[str]:
    scope = pack.get("scope_boundary")
    if not isinstance(scope, dict):
        return []

    allowed = _read_path_list(
        scope.get("allowed_paths"), "scope_boundary.allowed_paths"
    )
    forbidden = _read_path_list(
        scope.get("forbidden_paths"), "scope_boundary.forbidden_paths"
    )

    violations: list[str] = []
    for path in changed_paths:
        if path in ignored_paths:
            continue
        if _matches_any(path, forbidden):
            violations.append(path)
            continue
        if allowed and not _matches_any(path, allowed):
            violations.append(path)
    return sorted(dict.fromkeys(violations))


def _matches_any(path: str, boundaries: list[str]) -> bool:
    return any(_path_within(path, boundary) for boundary in boundaries)


def _path_within(path: str, boundary: str) -> bool:
    clean_path = str(PurePosixPath(path.strip()))
    clean_boundary = str(PurePosixPath(boundary.strip()))
    if clean_boundary in {"", "."}:
        return True
    if clean_path == clean_boundary:
        return True
    return clean_path.startswith(f"{clean_boundary}/")


def _failed_checks(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        failed = [name for name, passed in raw.items() if passed is False]
        return sorted(name for name in failed if isinstance(name, str))
    if isinstance(raw, list):
        failed: list[str] = []
        for idx, row in enumerate(raw):
            if not isinstance(row, dict):
                raise ToolError(
                    "invalid_input",
                    "check_results list items must be objects",
                    {"key": "check_results", "index": idx},
                )
            command = row.get("command")
            passed = row.get("passed")
            if not isinstance(command, str):
                raise ToolError(
                    "invalid_input",
                    "check_results item command must be string",
                    {"key": "check_results", "index": idx, "field": "command"},
                )
            if not isinstance(passed, bool):
                raise ToolError(
                    "invalid_input",
                    "check_results item passed must be boolean",
                    {"key": "check_results", "index": idx, "field": "passed"},
                )
            if not passed:
                failed.append(command)
        return failed
    raise ToolError(
        "invalid_input",
        "check_results must be an object or list",
        {"key": "check_results"},
    )
