from __future__ import annotations

from typing import Any

from taco.core.plan.types import ToolError


def _plan_path_from_config(raw: dict[str, Any]) -> str:
    docs = raw.get("docs", {})
    if not isinstance(docs, dict):
        raise ToolError("invalid_config", "docs config must be object", {})
    plan = docs.get("plan")
    if not isinstance(plan, str) or not plan.strip():
        raise ToolError("invalid_config", "docs.plan must be non-empty string", {})
    return plan.strip()

def _load_common_required_refs(raw: dict[str, Any]) -> tuple[str, ...]:
    pack = raw.get("pack", {})
    if not isinstance(pack, dict):
        return ()
    values = pack.get("common_required_refs", [])
    if not isinstance(values, list):
        return ()
    ref_ids: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if value and value not in ref_ids:
            ref_ids.append(value)
    return tuple(ref_ids)

def _load_required_refs_by_tool(raw: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    defaults: dict[str, tuple[str, ...]] = {
        "plan.pack": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
        "plan.intent.index": ("ARCH-INDEX", "PLAN-MAIN", "GOV-DOC-INDEX"),
        "task.pack": ("GOV-CODE-PRINCIPLES",),
    }
    pack = raw.get("pack", {})
    if not isinstance(pack, dict):
        return defaults

    by_tool = pack.get("required_refs_by_tool")
    if isinstance(by_tool, dict):
        resolved = dict(defaults)
        plan_pack = _read_ref_list(by_tool, ("plan.pack", "plan_pack"))
        plan_intent_index = _read_ref_list(
            by_tool, ("plan.intent.index", "plan_intent_index")
        )
        task_pack = _read_ref_list(by_tool, ("task.pack", "task_pack"))
        if plan_pack:
            resolved["plan.pack"] = plan_pack
        if plan_intent_index:
            resolved["plan.intent.index"] = plan_intent_index
        if task_pack:
            resolved["task.pack"] = task_pack
        return resolved

    legacy = _load_common_required_refs(raw)
    if legacy:
        return {
            "plan.pack": legacy,
            "plan.intent.index": legacy,
            "task.pack": legacy,
        }
    return defaults

def _read_ref_list(raw: dict[str, Any], keys: tuple[str, ...]) -> tuple[str, ...]:
    for key in keys:
        value = raw.get(key)
        if not isinstance(value, list):
            continue
        refs: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            ref_id = item.strip()
            if ref_id and ref_id not in refs:
                refs.append(ref_id)
        if refs:
            return tuple(refs)
    return ()

def _load_task_required_headings(raw: dict[str, Any]) -> tuple[str, ...]:
    defaults = (
        "Intent",
        "Goal",
        "Scope",
        "Implementation Approach",
        "Verification Approach",
        "Implementation Result",
        "Verification Result",
    )
    parsing = raw.get("parsing", {})
    if not isinstance(parsing, dict):
        return defaults
    values = parsing.get("task_required_headings")
    if not isinstance(values, list):
        return defaults
    headings: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        heading = item.strip()
        if heading and heading not in headings:
            headings.append(heading)
    if not headings:
        return defaults
    return tuple(headings)

def _collect_doc_prefixes(raw: dict[str, Any]) -> tuple[str, ...]:
    docs = raw.get("docs", {})
    if not isinstance(docs, dict):
        return (".context/",)

    raw_paths: list[str] = []
    for key in (
        "intent",
        "architecture",
        "plan",
        "glossary",
        "doc_map",
        "tasks_glob",
        "intents_glob",
    ):
        value = docs.get(key)
        if isinstance(value, str):
            raw_paths.append(value)
    for key in ("principles", "todo"):
        value = docs.get(key, [])
        if isinstance(value, list):
            raw_paths.extend(item for item in value if isinstance(item, str))

    prefixes: list[str] = []
    for item in raw_paths:
        cleaned = item.split("*", 1)[0].strip("/")
        if not cleaned:
            continue
        if "." in cleaned.split("/")[-1]:
            cleaned = "/".join(cleaned.split("/")[:-1])
        if not cleaned:
            continue
        prefix = f"{cleaned}/"
        if prefix not in prefixes:
            prefixes.append(prefix)

    if not prefixes:
        return (".context/",)
    return tuple(prefixes)

def _should_include_path(path: str, prefixes: tuple[str, ...]) -> bool:
    if path.startswith(".git/"):
        return False
    return any(path.startswith(prefix) for prefix in prefixes)

