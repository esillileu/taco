from __future__ import annotations

import pytest

from taco.parser import ParseConfig, ParserError, parse_markdown_sections


def test_parse_markdown_sections_builds_expected_slices() -> None:
    text = "\n".join(
        [
            "# Top",
            "intro",
            "## Child",
            "body",
            "### Leaf",
            "tail",
        ]
    )

    sections = parse_markdown_sections("docs/sample.md", text)

    assert len(sections) == 3
    assert sections[0].start_line == 1
    assert sections[0].end_line == 2
    assert sections[1].start_line == 3
    assert sections[1].end_line == 4
    assert sections[2].start_line == 5
    assert sections[2].end_line == 6


def test_parse_markdown_sections_deduplicates_anchors() -> None:
    text = "\n".join(
        [
            "# Repeat",
            "## Repeat",
            "## Repeat",
        ]
    )

    sections = parse_markdown_sections("docs/sample.md", text)
    anchors = [section.anchor_id for section in sections]
    assert anchors == ["repeat", "repeat-2", "repeat-3"]


def test_parse_markdown_sections_prefers_explicit_anchor() -> None:
    text = "# Title {#custom-id}\n"
    sections = parse_markdown_sections(
        "docs/sample.md", text, ParseConfig(prefer_anchors=True)
    )
    assert sections[0].anchor_id == "custom-id"


def test_parse_markdown_sections_can_ignore_explicit_anchor() -> None:
    text = "# Title {#custom-id}\n"
    sections = parse_markdown_sections(
        "docs/sample.md", text, ParseConfig(prefer_anchors=False)
    )
    assert sections[0].anchor_id == "title"


def test_parse_markdown_sections_handles_missing_heading_cases() -> None:
    sections = parse_markdown_sections("docs/sample.md", "no headings here")
    assert sections == []


def test_parse_markdown_sections_rejects_empty_heading_text() -> None:
    with pytest.raises(ParserError) as exc:
        parse_markdown_sections("docs/sample.md", "# {#only-anchor}\n")

    assert exc.value.code == "invalid_heading"


def test_parse_markdown_sections_is_deterministic() -> None:
    text = "# Alpha\n## Beta\n## Beta\n"
    first = parse_markdown_sections("docs/sample.md", text)
    second = parse_markdown_sections("docs/sample.md", text)
    assert first == second


def test_section_slice_to_dict_contract() -> None:
    text = "# Alpha\n"
    section = parse_markdown_sections("docs/sample.md", text)[0]
    assert section.to_dict() == {
        "document_path": "docs/sample.md",
        "level": 1,
        "heading": "Alpha",
        "anchor_id": "alpha",
        "pack_groups": (),
        "start_line": 1,
        "end_line": 1,
    }


def test_parse_markdown_sections_extracts_pack_groups() -> None:
    text = "\n".join(
        [
            "## Scope",
            "<!-- taco:pack=task.core,pack.next_actions -->",
            "content",
        ]
    )
    section = parse_markdown_sections("docs/sample.md", text)[0]
    assert section.pack_groups == ("task.core", "pack.next_actions")
