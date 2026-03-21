from __future__ import annotations

from pathlib import Path
from typing import Any

from taco.core.plan import (
    RepoState,
    ToolError,
    _collect_string_list,
    _split_front_matter,
)
from taco.core.usecases.io import read_text

from .task_contract import (
    BOUNDARY_TERMS,
    REQUIRED_HEADINGS,
    VERIFICATION_TERMS,
    non_empty_lines,
    section_body,
)


def _validate_front_matter(
    meta: dict[str, Any], intent_id: str | None
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ("id", "type", "title", "status", "plan_ref"):
        value = meta.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"front_matter_missing:{key}")

    scope = meta.get("scope")
    if not isinstance(scope, dict):
        errors.append("front_matter_missing:scope")
    else:
        scope_in = _collect_string_list(scope.get("in"))
        scope_out = _collect_string_list(scope.get("out"))
        if not scope_in:
            errors.append("scope_in_missing")
        if not scope_out:
            errors.append("scope_out_missing")

    refs = meta.get("references")
    if not isinstance(refs, dict):
        errors.append("front_matter_missing:references")
    else:
        for key in ("modules", "flows", "schemas"):
            if not _collect_string_list(refs.get(key)):
                errors.append(f"references_missing:{key}")

    links = _collect_string_list(meta.get("links"))
    if not links:
        errors.append("links_missing")
    if intent_id and intent_id not in links:
        warnings.append("intent_link_missing")

    return errors, warnings


def _validate_sections(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if not section_body(text, heading):
            errors.append(f"missing_section:{heading}")

    scope = section_body(text, "Scope").lower()
    if scope and "out of scope" not in scope:
        errors.append("scope_out_clause_missing")

    impl = section_body(text, "Implementation Approach")
    verify = section_body(text, "Verification Approach")

    if impl and non_empty_lines(impl) < 2:
        errors.append("implementation_approach_too_thin")
    if impl and not any(term in impl.lower() for term in BOUNDARY_TERMS):
        warnings.append("boundary_rationale_weak")

    if verify and non_empty_lines(verify) < 2:
        errors.append("verification_approach_too_thin")
    if verify and not any(term in verify.lower() for term in VERIFICATION_TERMS):
        errors.append("verification_command_or_condition_missing")

    return errors, warnings


def _fix_hints(errors: list[str], warnings: list[str]) -> list[str]:
    hints: list[str] = []
    if any(code.startswith("front_matter_missing") for code in errors):
        hints.append("run plan.task.frontmatter.sync after authoring body")
    if "scope_out_missing" in errors or "scope_out_clause_missing" in errors:
        hints.append(
            "add concrete non-goals in front matter scope.out and Scope section"
        )
    if "verification_command_or_condition_missing" in errors:
        hints.append("add executable commands or assertions in Verification Approach")
    if "boundary_rationale_weak" in warnings:
        hints.append(
            "mention hexagonal boundary/port/adapter rationale in "
            "Implementation Approach"
        )
    return hints


def plan_task_lint(state: RepoState, args: dict[str, Any]) -> dict[str, Any]:
    path = str(args.get("path", "")).strip()
    if not path:
        raise ToolError("invalid_input", "path is required", {"key": "path"})

    intent_raw = args.get("intent_id")
    intent_id = str(intent_raw).strip() if isinstance(intent_raw, str) else None

    target = Path(path)
    if state.storage is None or not state.storage.exists(target):
        errors = ["task_document_missing"]
        return {
            "path": path,
            "intent_id": intent_id or "",
            "valid": False,
            "errors": errors,
            "warnings": [],
            "fix_hints": _fix_hints(errors, []),
        }

    text = read_text(state, path)
    meta, _body = _split_front_matter(text)
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(meta, dict) or not meta:
        errors.append("front_matter_missing")
    else:
        fm_errors, fm_warnings = _validate_front_matter(meta, intent_id)
        errors.extend(fm_errors)
        warnings.extend(fm_warnings)

    section_errors, section_warnings = _validate_sections(text)
    errors.extend(section_errors)
    warnings.extend(section_warnings)

    dedup_errors = list(dict.fromkeys(errors))
    dedup_warnings = list(dict.fromkeys(warnings))
    return {
        "path": path,
        "intent_id": intent_id or "",
        "valid": not dedup_errors,
        "errors": dedup_errors,
        "warnings": dedup_warnings,
        "fix_hints": _fix_hints(dedup_errors, dedup_warnings),
    }
