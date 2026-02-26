from __future__ import annotations

from taco.core.indexing.models import HeadingRef, IndexedDocument
from taco.core.packing.derive import _derive_write_targets
from taco.core.routing import ROUTE_HEADING_MAP, ROUTE_MODE_MAP, RouterConfig


def test_router_default_is_policy_ssot() -> None:
    cfg = RouterConfig.default()
    assert cfg.heading_map == ROUTE_HEADING_MAP
    assert cfg.mode_map == ROUTE_MODE_MAP


def test_pack_write_targets_follow_policy_modes() -> None:
    doc = IndexedDocument(
        path=".context/project/tasks/T-000-bootstrap.md",
        doc_type="task",
        task_id="T-000",
        node_id="T-000",
        node_type="task",
        metadata={},
        headings=(
            HeadingRef(2, "Implementation Result", "impl", (), (), 10, 12),
            HeadingRef(2, "Verification Result", "verify", (), (), 13, 15),
        ),
        links=(),
    )

    targets = _derive_write_targets(doc)
    assert targets == (
        {
            "path": doc.path,
            "heading": "Implementation Result",
            "line_hint": 12,
            "mode": "append_implementation",
        },
        {
            "path": doc.path,
            "heading": "Verification Result",
            "line_hint": 15,
            "mode": "append_verification",
        },
    )
