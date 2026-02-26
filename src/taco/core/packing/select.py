from __future__ import annotations

from collections.abc import Callable

from taco.core.indexing import IndexedDocument, IndexGraph
from taco.core.packing.extract import _infer_task_groups, _to_candidate
from taco.core.packing.models import _CandidateSnippet


def _build_candidates(
    task_id: str,
    task_path: str,
    index: IndexGraph,
    estimator: Callable[[str], int],
) -> list[_CandidateSnippet]:
    candidates: list[_CandidateSnippet] = []
    for doc in index.documents:
        if doc.doc_type == "task" and doc.path != task_path:
            continue
        for heading in doc.headings:
            groups = tuple(heading.pack_groups)
            if not groups and doc.path == task_path:
                groups = _infer_task_groups(heading.heading)
            for group in groups:
                if group.startswith("task.") and doc.path != task_path:
                    continue
                candidates.append(
                    _to_candidate(
                        group=group,
                        path=doc.path,
                        heading=heading,
                        document_texts=index.document_texts,
                        estimator=estimator,
                        reason=(
                            "selector_match"
                            if heading.pack_groups
                            else "task_heading_fallback"
                        ),
                        required=False,
                    )
                )
    return candidates

def _build_reference_candidates(
    required_refs: tuple[str, ...],
    optional_refs: tuple[str, ...],
    index: IndexGraph,
    estimator: Callable[[str], int],
) -> tuple[list[_CandidateSnippet], list[str]]:
    candidates: list[_CandidateSnippet] = []
    missing: list[str] = []
    required_set = set(required_refs)
    for ref_id in required_refs:
        candidate = _candidate_from_ref(ref_id, index, estimator, required=True)
        if candidate is None:
            missing.append(ref_id)
            continue
        candidates.append(candidate)
    for ref_id in optional_refs:
        if ref_id in required_set:
            continue
        candidate = _candidate_from_ref(ref_id, index, estimator, required=False)
        if candidate is not None:
            candidates.append(candidate)
    return candidates, missing

def _candidate_from_ref(
    ref_id: str,
    index: IndexGraph,
    estimator: Callable[[str], int],
    required: bool,
) -> _CandidateSnippet | None:
    heading_key = index.reference_lookup.get(ref_id)
    if heading_key:
        separator = heading_key.rfind("#")
        if separator < 0:
            return None
        path = heading_key[:separator]
        heading = index.heading_lookup.get(heading_key)
        if heading is None:
            return None
    else:
        path = index.node_index.get(ref_id, "")
        if not path:
            return None
        doc = _find_doc(index.documents, path)
        if doc is None or not doc.headings:
            return None
        heading = doc.headings[0]
    return _to_candidate(
        group=f"ref:{ref_id}",
        path=path,
        heading=heading,
        document_texts=index.document_texts,
        estimator=estimator,
        reason="context_requirement",
        required=required,
    )

def _find_doc(
    documents: tuple[IndexedDocument, ...], path: str
) -> IndexedDocument | None:
    for doc in documents:
        if doc.path == path:
            return doc
    return None
