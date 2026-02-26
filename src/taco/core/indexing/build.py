from __future__ import annotations

from pathlib import Path

from taco.core.indexing.extract import (
    _classify_doc_type,
    _extract_front_matter,
    _extract_local_links,
    _extract_task_id,
    _validate_required_docs,
)
from taco.core.indexing.models import (
    DocumentInput,
    HeadingRef,
    IndexConfig,
    IndexedDocument,
    IndexerError,
    IndexGraph,
)


def scan_markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if path.is_file())

def load_documents(root: Path, paths: list[str]) -> list[DocumentInput]:
    docs: list[DocumentInput] = []
    for rel_path in sorted(paths):
        text = (root / rel_path).read_text(encoding="utf-8")
        docs.append(DocumentInput.from_text(path=rel_path, text=text))
    return docs

def build_index(documents: list[DocumentInput], config: IndexConfig) -> IndexGraph:
    sorted_docs = sorted(documents, key=lambda doc: doc.path)
    by_path = {doc.path: doc for doc in sorted_docs}
    _validate_required_docs(by_path, config)

    indexed_docs: list[IndexedDocument] = []
    task_index: dict[str, str] = {}
    node_index: dict[str, str] = {}
    link_graph: dict[str, tuple[str, ...]] = {}
    heading_lookup: dict[str, HeadingRef] = {}
    reference_lookup: dict[str, str] = {}

    for doc in sorted_docs:
        doc_type = _classify_doc_type(doc.path, config)
        metadata = _extract_front_matter(doc.text)
        node_id = metadata.get("id") if isinstance(metadata.get("id"), str) else None
        node_type = (
            metadata.get("type") if isinstance(metadata.get("type"), str) else None
        )
        if node_type:
            doc_type = node_type
        task_id = _extract_task_id(doc.path)
        if task_id:
            task_index[task_id] = doc.path
        if node_id:
            existing = node_index.get(node_id)
            if existing:
                raise IndexerError(
                    code="duplicate_node_id",
                    message="document id must be unique",
                    details={"id": node_id, "first": existing, "second": doc.path},
                )
            node_index[node_id] = doc.path

        headings = tuple(
            HeadingRef(
                level=section.level,
                heading=section.heading,
                anchor_id=section.anchor_id,
                pack_groups=section.pack_groups,
                ref_ids=section.ref_ids,
                start_line=section.start_line,
                end_line=section.end_line,
            )
            for section in doc.sections
        )
        links = tuple(_extract_local_links(doc.text))
        link_graph[doc.path] = links
        for heading in headings:
            key = f"{doc.path}#{heading.anchor_id}"
            heading_lookup[key] = heading
            for ref_id in heading.ref_ids:
                existing = reference_lookup.get(ref_id)
                if existing:
                    raise IndexerError(
                        code="duplicate_reference_id",
                        message="reference id must be unique",
                        details={"ref_id": ref_id, "first": existing, "second": key},
                    )
                reference_lookup[ref_id] = key

        indexed_docs.append(
            IndexedDocument(
                path=doc.path,
                doc_type=doc_type,
                task_id=task_id,
                node_id=node_id,
                node_type=node_type,
                metadata=metadata,
                headings=headings,
                links=links,
            )
        )

    return IndexGraph(
        documents=tuple(indexed_docs),
        task_index=task_index,
        node_index=node_index,
        link_graph=link_graph,
        heading_lookup=heading_lookup,
        reference_lookup=reference_lookup,
        document_texts={doc.path: doc.text for doc in sorted_docs},
    )

