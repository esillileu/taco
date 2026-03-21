from __future__ import annotations

from typing import Any


def tool_catalog() -> list[dict[str, Any]]:
    names = [
        "task.list",
        "task.pack",
        "plan.pack",
        "plan.intent.list",
        "plan.intent.template",
        "plan.intent.create_many",
        "plan.intent.submit_many",
        "plan.intent.view",
        "plan.intent.index",
        "plan.intent.propose",
        "plan.intent.autodesign",
        "plan.intent.generate_tasks",
        "plan.intent.review_bundle",
        "plan.intent.apply",
        "plan.intent.validate",
        "plan.mode.guide",
        "plan.design.submit_changes",
        "plan.task.submit_many",
        "plan.task.template",
        "plan.task.frontmatter.sync",
        "plan.task.lint",
        "task.targets",
        "task.record",
        "task.complete",
        "task.block",
        "doc.snippet",
        "doc.section.get",
        "doc.section.patch",
        "build.precheck",
        "build.postcheck",
        "issue.triage",
        "convention.get",
        "plan.view",
        "plan.locate",
        "plan.validate",
    ]
    return [
        {
            "name": name,
            "description": f"TACO tool: {name}",
            "inputSchema": {"type": "object", "additionalProperties": True},
        }
        for name in names
    ]
