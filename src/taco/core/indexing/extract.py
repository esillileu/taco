from __future__ import annotations

import re
from fnmatch import fnmatch
from typing import Any

import yaml

from taco.core.indexing.models import DocumentInput, IndexConfig, IndexerError

TASK_ID_RE = re.compile(r"(T-\d{3})")

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

def _validate_required_docs(
    by_path: dict[str, DocumentInput], config: IndexConfig
) -> None:
    required = {
        config.intent_path,
        config.architecture_path,
        config.plan_path,
        config.glossary_path,
    }
    missing = sorted(required - set(by_path))
    if missing:
        raise IndexerError(
            code="missing_required_docs",
            message="required SSOT docs are missing",
            details={"missing": ", ".join(missing)},
        )

def _classify_doc_type(path: str, config: IndexConfig) -> str:
    if path == config.intent_path:
        return "intent"
    if path == config.architecture_path:
        return "architecture"
    if path == config.plan_path:
        return "plan"
    if path == config.glossary_path:
        return "glossary"
    if path in config.principles_paths:
        return "principles"
    if path in config.todo_paths:
        return "todo"
    if config.git_module_path and path == config.git_module_path:
        return "git"
    if fnmatch(path, config.tasks_glob):
        return "task"
    if path.startswith(".context/governance/git/"):
        return "git-detail"
    return "doc"

def _extract_task_id(path: str) -> str | None:
    match = TASK_ID_RE.search(path)
    if not match:
        return None
    return match.group(1)

def _extract_local_links(text: str) -> list[str]:
    links: list[str] = []
    for link in LINK_RE.findall(text):
        if (
            link.startswith("http://")
            or link.startswith("https://")
            or link.startswith("#")
        ):
            continue
        links.append(link)
    return links

def _extract_front_matter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end = idx
            break
    if end < 0:
        return {}
    raw = "\n".join(lines[1:end]).strip()
    if not raw:
        return {}
    loaded = yaml.safe_load(raw)
    if not isinstance(loaded, dict):
        return {}
    return loaded
