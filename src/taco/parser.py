from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
EXPLICIT_ANCHOR_RE = re.compile(r"^(.*?)\s*\{#([A-Za-z0-9_-]+)\}\s*$")


@dataclass(frozen=True)
class SectionSlice:
    document_path: str
    level: int
    heading: str
    anchor_id: str
    start_line: int
    end_line: int

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True)
class ParseConfig:
    prefer_anchors: bool = True


class ParserError(ValueError):
    def __init__(
        self, code: str, message: str, details: dict[str, str | int] | None = None
    ) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def parse_markdown_sections(
    document_path: str, markdown_text: str, config: ParseConfig | None = None
) -> list[SectionSlice]:
    active_config = config or ParseConfig()
    lines = markdown_text.splitlines()
    anchors_seen: dict[str, int] = {}

    rows: list[tuple[int, int, str, str]] = []
    for idx, raw_line in enumerate(lines, start=1):
        match = HEADING_RE.match(raw_line)
        if not match:
            continue

        level = len(match.group(1))
        heading_raw = match.group(2).strip()
        heading_text, explicit_anchor = _split_explicit_anchor(heading_raw)

        if not heading_text:
            raise ParserError(
                code="invalid_heading",
                message="heading text cannot be empty",
                details={"path": document_path, "line": idx},
            )

        base_anchor = _resolve_anchor(
            heading_text=heading_text,
            explicit_anchor=explicit_anchor,
            prefer_anchors=active_config.prefer_anchors,
        )
        anchor_id = _dedupe_anchor(base_anchor, anchors_seen)
        rows.append((idx, level, heading_text, anchor_id))

    sections: list[SectionSlice] = []
    for pos, (start_line, level, heading, anchor_id) in enumerate(rows):
        next_start = rows[pos + 1][0] if pos + 1 < len(rows) else len(lines) + 1
        sections.append(
            SectionSlice(
                document_path=document_path,
                level=level,
                heading=heading,
                anchor_id=anchor_id,
                start_line=start_line,
                end_line=next_start - 1,
            )
        )
    return sections


def _split_explicit_anchor(heading_text: str) -> tuple[str, str | None]:
    match = EXPLICIT_ANCHOR_RE.match(heading_text)
    if not match:
        return heading_text, None
    return match.group(1).strip(), match.group(2).strip()


def _resolve_anchor(
    heading_text: str, explicit_anchor: str | None, prefer_anchors: bool
) -> str:
    if explicit_anchor and prefer_anchors:
        return explicit_anchor
    if explicit_anchor and not prefer_anchors:
        return _slugify(heading_text)
    return _slugify(heading_text)


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    kept = re.sub(r"[^a-z0-9\s-]", "", lowered)
    compact = re.sub(r"[\s-]+", "-", kept).strip("-")
    return compact or "section"


def _dedupe_anchor(base_anchor: str, anchors_seen: dict[str, int]) -> str:
    current = anchors_seen.get(base_anchor, 0) + 1
    anchors_seen[base_anchor] = current
    if current == 1:
        return base_anchor
    return f"{base_anchor}-{current}"
