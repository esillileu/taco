from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "taco.yaml"
ALLOWED_TYPES = {
    "anchor",
    "module",
    "flow",
    "schema",
    "task",
    "plan",
    "intent",
    "governance",
}
COMMON_REQUIRED = ("id", "type", "title", "status")
TASK_STATUS = {"todo", "active", "done", "blocked"}
INTENT_STATUS = {"active", "ready_for_build", "done", "blocked"}


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    loaded = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        return {}
    return loaded


def all_context_docs() -> list[Path]:
    return sorted((ROOT / ".context").rglob("*.md"))


def parse_front_matter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ""
    end = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end < 0:
        return {}, ""
    raw = "\n".join(lines[1:end]).strip()
    body = "\n".join(lines[end + 1 :])
    if not raw:
        return {}, body
    parsed = yaml.safe_load(raw)
    if not isinstance(parsed, dict):
        return {}, body
    return parsed, body


def validate_front_matter(
    files: list[Path],
) -> tuple[list[str], dict[str, Path], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    id_to_path: dict[str, Path] = {}
    fm_by_path: dict[str, dict[str, Any]] = {}

    for path in files:
        fm, _ = parse_front_matter(path)
        rel = path.relative_to(ROOT).as_posix()
        fm_by_path[rel] = fm
        if not fm:
            errors.append(f"{rel}: missing or invalid front matter")
            continue

        missing = [key for key in COMMON_REQUIRED if key not in fm]
        if missing:
            errors.append(f"{rel}: missing required fields {missing}")
            continue

        node_id = fm.get("id")
        node_type = fm.get("type")
        status = fm.get("status")
        if not isinstance(node_id, str) or not node_id.strip():
            errors.append(f"{rel}: id must be non-empty string")
            continue
        if not isinstance(node_type, str) or node_type not in ALLOWED_TYPES:
            errors.append(f"{rel}: type must be one of {sorted(ALLOWED_TYPES)}")
            continue
        if not isinstance(status, str) or not status.strip():
            errors.append(f"{rel}: status must be non-empty string")
            continue
        if node_type == "task" and status not in TASK_STATUS:
            errors.append(f"{rel}: task status must be one of {sorted(TASK_STATUS)}")
        if node_type == "intent" and status not in INTENT_STATUS:
            errors.append(
                f"{rel}: intent status must be one of {sorted(INTENT_STATUS)}"
            )

        existing = id_to_path.get(node_id)
        if existing:
            errors.append(
                "duplicate id "
                f"{node_id}: {existing.relative_to(ROOT).as_posix()} and {rel}"
            )
        else:
            id_to_path[node_id] = path

    return errors, id_to_path, fm_by_path


def _collect_ref_ids(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str) and item.strip():
                refs.append(item.strip())
    return refs


def validate_references(
    id_to_path: dict[str, Path], fm_by_path: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    known = set(id_to_path)
    type_by_id: dict[str, str] = {}
    for _rel, fm in fm_by_path.items():
        node_id = fm.get("id")
        node_type = fm.get("type")
        if isinstance(node_id, str) and isinstance(node_type, str):
            type_by_id[node_id] = node_type

    flow_intent_refs: set[str] = set()
    for _rel, fm in fm_by_path.items():
        if fm.get("type") != "flow":
            continue
        for intent_id in _collect_ref_ids(fm.get("intent_refs")):
            flow_intent_refs.add(intent_id)

    for rel, fm in fm_by_path.items():
        if not fm:
            continue
        refs: list[str] = []
        refs.extend(_collect_ref_ids(fm.get("links")))

        if fm.get("type") == "task":
            plan_ref = fm.get("plan_ref")
            if isinstance(plan_ref, str) and plan_ref.strip():
                refs.append(plan_ref.strip())
            scope = fm.get("scope")
            if not isinstance(scope, dict) or "in" not in scope or "out" not in scope:
                errors.append(f"{rel}: task requires scope.in and scope.out")
            references = fm.get("references")
            if not isinstance(references, dict):
                errors.append(f"{rel}: task requires references object")
            else:
                for key in ("modules", "flows", "schemas", "governance"):
                    refs.extend(_collect_ref_ids(references.get(key)))

        if fm.get("type") == "intent":
            plan_ref = fm.get("plan_ref")
            if isinstance(plan_ref, str) and plan_ref.strip():
                refs.append(plan_ref.strip())
            else:
                errors.append(f"{rel}: intent requires non-empty plan_ref")

            task_refs = fm.get("task_refs")
            if not isinstance(task_refs, list):
                errors.append(f"{rel}: intent requires task_refs list")
            else:
                refs.extend(_collect_ref_ids(task_refs))

        if fm.get("type") == "plan":
            refs.extend(_collect_ref_ids(fm.get("active_tasks")))
            refs.extend(_collect_ref_ids(fm.get("blocked_tasks")))
            refs.extend(_collect_ref_ids(fm.get("next_tasks")))
            active_intents = fm.get("active_intents")
            if active_intents is not None and not isinstance(active_intents, list):
                errors.append(
                    f"{rel}: plan active_intents must be a list when provided"
                )
            else:
                refs.extend(_collect_ref_ids(active_intents))
                for intent_id in _collect_ref_ids(active_intents):
                    if type_by_id.get(intent_id) != "intent":
                        errors.append(
                            f"{rel}: active_intents id must reference intent: "
                            f"{intent_id}"
                        )
                    if intent_id not in flow_intent_refs:
                        errors.append(
                            f"{rel}: active_intents intent must be referenced by "
                            f"flow.intent_refs: "
                            f"{intent_id}"
                        )

        if fm.get("type") == "flow":
            intent_refs = fm.get("intent_refs")
            if intent_refs is not None and not isinstance(intent_refs, list):
                errors.append(f"{rel}: flow intent_refs must be a list when provided")
            else:
                refs.extend(_collect_ref_ids(intent_refs))
                for intent_id in _collect_ref_ids(intent_refs):
                    if type_by_id.get(intent_id) != "intent":
                        errors.append(
                            f"{rel}: intent_refs id must reference intent: {intent_id}"
                        )

        for ref_id in refs:
            if ref_id not in known:
                errors.append(f"{rel}: unresolved reference id {ref_id}")
    return errors


def validate_config_paths(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    docs = config.get("docs", {})
    if not isinstance(docs, dict):
        return ["taco.yaml: docs must be mapping"]

    required = ("intent", "architecture", "plan", "glossary", "tasks_glob")
    for key in required:
        if key not in docs:
            errors.append(f"taco.yaml: docs.{key} is required")

    for key in ("intent", "architecture", "plan", "glossary", "doc_map"):
        value = docs.get(key)
        if isinstance(value, str):
            path = ROOT / value
            if not path.exists():
                errors.append(f"taco.yaml: path not found for docs.{key}: {value}")

    principles = docs.get("principles", [])
    if isinstance(principles, list):
        for rel in principles:
            if isinstance(rel, str) and not (ROOT / rel).exists():
                errors.append(f"taco.yaml: principles path not found: {rel}")

    todo = docs.get("todo", [])
    if isinstance(todo, list):
        for rel in todo:
            if isinstance(rel, str) and not (ROOT / rel).exists():
                errors.append(f"taco.yaml: todo path not found: {rel}")

    return errors


def main() -> int:
    config = load_config()
    errors = validate_config_paths(config)

    files = all_context_docs()
    if not files:
        errors.append(".context: no markdown documents found")

    fm_errors, id_to_path, fm_by_path = validate_front_matter(files)
    errors.extend(fm_errors)
    errors.extend(validate_references(id_to_path, fm_by_path))

    if errors:
        print("DOC VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("DOC VALIDATION OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
