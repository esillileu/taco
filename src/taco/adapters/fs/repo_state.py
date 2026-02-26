from __future__ import annotations

from pathlib import Path

import yaml

from taco.adapters.fs.storage import FileSystemStorageAdapter
from taco.adapters.git import GitRepositoryAdapter
from taco.core.indexing import (
    IndexConfig,
    build_index,
    load_documents,
    scan_markdown_files,
)
from taco.core.packing import BudgetConfig
from taco.core.plan import (
    RepoState,
    ToolError,
    _collect_doc_prefixes,
    _load_required_refs_by_tool,
    _load_task_required_headings,
    _should_include_path,
)
from taco.core.routing.router import RouterConfig


def load_repo_state(root: Path, config_path: Path | None = None) -> RepoState:
    storage = FileSystemStorageAdapter(root)
    repository = GitRepositoryAdapter(root)
    cfg_path = config_path or (root / "taco.yaml")
    raw = yaml.safe_load(storage.read_text(cfg_path)) or {}
    if not isinstance(raw, dict):
        raise ToolError("invalid_config", "top-level config must be a mapping", {})

    index_config = IndexConfig.from_dict(raw)
    budget_config = BudgetConfig.from_dict(raw)
    router_config = RouterConfig.from_dict(raw)

    markdown_paths = scan_markdown_files(root)
    prefixes = _collect_doc_prefixes(raw)
    rel_paths = [
        path.relative_to(root).as_posix()
        for path in markdown_paths
        if _should_include_path(path.relative_to(root).as_posix(), prefixes)
    ]
    documents = load_documents(root, rel_paths)
    index = build_index(documents, index_config)

    return RepoState(
        root=root,
        config_raw=raw,
        index=index,
        budget_config=budget_config,
        router_config=router_config,
        required_refs_by_tool=_load_required_refs_by_tool(raw),
        task_required_headings=_load_task_required_headings(raw),
        storage=storage,
        repository=repository,
    )
