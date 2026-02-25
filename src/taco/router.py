from __future__ import annotations

from dataclasses import asdict, dataclass

from taco.indexer import HeadingRef, IndexGraph


@dataclass(frozen=True)
class RouterConfig:
    heading_map: dict[str, str]
    mode_map: dict[str, str]

    @classmethod
    def default(cls) -> RouterConfig:
        return cls(
            heading_map={
                "implementation_result": "Implementation Result",
                "verification_result": "Verification Result",
                "issue_record": "Verification Result",
            },
            mode_map={
                "implementation_result": "append_implementation",
                "verification_result": "append_verification",
                "issue_record": "append_issue",
            },
        )

    @classmethod
    def from_dict(cls, raw: dict[str, object]) -> RouterConfig:
        base = cls.default()
        router_cfg = raw.get("router")
        if not isinstance(router_cfg, dict):
            return base
        heading_map = dict(base.heading_map)
        mode_map = dict(base.mode_map)

        raw_heading_map = router_cfg.get("heading_map")
        if isinstance(raw_heading_map, dict):
            for key, value in raw_heading_map.items():
                if isinstance(key, str) and isinstance(value, str):
                    heading_map[key] = value

        raw_mode_map = router_cfg.get("mode_map")
        if isinstance(raw_mode_map, dict):
            for key, value in raw_mode_map.items():
                if isinstance(key, str) and isinstance(value, str):
                    mode_map[key] = value

        return cls(heading_map=heading_map, mode_map=mode_map)


@dataclass(frozen=True)
class WriteTarget:
    path: str
    heading: str
    line_hint: int
    mode: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


class RouterError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def resolve_write_target(
    task_id: str,
    route_type: str,
    index: IndexGraph,
    config: RouterConfig | None = None,
) -> WriteTarget:
    active = config or RouterConfig.default()
    target_heading = active.heading_map.get(route_type)
    if not target_heading:
        raise RouterError(
            code="invalid_route_type",
            message="route type is not configured",
            details={"route_type": route_type},
        )

    task_path = index.task_index.get(task_id)
    if not task_path:
        raise RouterError(
            code="task_not_found",
            message="task id not found in index",
            details={"task_id": task_id},
        )

    doc = next((item for item in index.documents if item.path == task_path), None)
    if not doc:
        raise RouterError(
            code="task_doc_missing",
            message="task document is missing from index",
            details={"task_id": task_id, "path": task_path},
        )

    matches = [heading for heading in doc.headings if heading.heading == target_heading]
    if not matches:
        raise RouterError(
            code="target_heading_not_found",
            message="target heading not found in task doc",
            details={"task_id": task_id, "heading": target_heading},
        )
    if len(matches) > 1:
        raise RouterError(
            code="ambiguous_target_heading",
            message="multiple target headings found in task doc",
            details={
                "task_id": task_id,
                "heading": target_heading,
                "count": len(matches),
            },
        )

    match = matches[0]
    mode = active.mode_map.get(route_type, "append")
    return WriteTarget(
        path=task_path,
        heading=match.heading,
        line_hint=_line_hint(match),
        mode=mode,
    )


def _line_hint(heading: HeadingRef) -> int:
    return heading.end_line
