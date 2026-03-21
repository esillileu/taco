from __future__ import annotations

from taco.core.indexing import (
    IndexConfig,
    build_index,
    load_documents,
    scan_markdown_files,
)
from taco.core.plan import RepoState, _collect_doc_prefixes, _should_include_path


def rebuild_state_index(state: RepoState) -> RepoState:
    index_config = IndexConfig.from_dict(state.config_raw)
    markdown_paths = scan_markdown_files(state.root)
    prefixes = _collect_doc_prefixes(state.config_raw)
    rel_paths = [
        path.relative_to(state.root).as_posix()
        for path in markdown_paths
        if _should_include_path(path.relative_to(state.root).as_posix(), prefixes)
    ]
    documents = load_documents(state.root, rel_paths)
    index = build_index(documents, index_config)
    return RepoState(
        root=state.root,
        config_raw=state.config_raw,
        index=index,
        budget_config=state.budget_config,
        router_config=state.router_config,
        required_refs_by_tool=state.required_refs_by_tool,
        task_required_headings=state.task_required_headings,
        storage=state.storage,
        repository=state.repository,
    )
