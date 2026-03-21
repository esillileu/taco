from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from taco.apps.cli.errors import CliError


def _to_options(args: argparse.Namespace) -> dict[str, Any]:
    options: dict[str, Any] = {}
    if getattr(args, "task_id", None) is not None:
        options["task_id"] = args.task_id
    if getattr(args, "route_type", None) is not None:
        options["route_type"] = args.route_type
    if getattr(args, "content", None) is not None:
        options["content"] = args.content
    if getattr(args, "content_file", None) is not None:
        options["content"] = _read_content_file_option(
            args.content_file,
            key="content_file",
        )
    if getattr(args, "implementation", None) is not None:
        options["implementation"] = args.implementation
    if getattr(args, "verification", None) is not None:
        options["verification"] = args.verification
    if getattr(args, "reason_code", None) is not None:
        options["reason_code"] = args.reason_code
    if getattr(args, "reason", None) is not None:
        options["reason"] = args.reason
    if getattr(args, "path", None) is not None:
        options["path"] = args.path
    if getattr(args, "section_id", None) is not None:
        options["section_id"] = args.section_id
    if getattr(args, "anchor_id", None) is not None:
        options["anchor_id"] = args.anchor_id
    if getattr(args, "topic", None) is not None:
        options["topic"] = args.topic
    if getattr(args, "change_type", None) is not None:
        options["change_type"] = args.change_type
    if getattr(args, "stage", None) is not None:
        options["stage"] = args.stage
    if getattr(args, "plan_ref", None) is not None:
        options["plan_ref"] = args.plan_ref
    if getattr(args, "target", None) is not None:
        options["target"] = args.target
    if getattr(args, "intent_id", None) is not None:
        options["intent_id"] = args.intent_id
    if getattr(args, "intent_text", None) is not None:
        options["intent_text"] = args.intent_text
    if getattr(args, "proposal_fingerprint", None) is not None:
        options["proposal_fingerprint"] = args.proposal_fingerprint
    if getattr(args, "design_fingerprint", None) is not None:
        options["design_fingerprint"] = args.design_fingerprint
    if getattr(args, "taskset_fingerprint", None) is not None:
        options["taskset_fingerprint"] = args.taskset_fingerprint
    if getattr(args, "decision_fingerprint", None) is not None:
        options["decision_fingerprint"] = args.decision_fingerprint
    if getattr(args, "retry_on_fail", None) is not None:
        options["retry_on_fail"] = args.retry_on_fail
    if getattr(args, "approve", False):
        options["approve"] = True
    if getattr(args, "title", None) is not None:
        options["title"] = args.title
    if getattr(args, "budget_tokens", None) is not None:
        options["budget_tokens"] = args.budget_tokens
    if getattr(args, "base_fingerprint", None) is not None:
        options["base_fingerprint"] = args.base_fingerprint
    if getattr(args, "ops_json", None) is not None:
        options["ops"] = _parse_json_option(args.ops_json, "ops_json")
    if getattr(args, "intents_json", None) is not None:
        options["intents"] = _parse_json_option(
            args.intents_json,
            "intents_json",
            allow_file_path=True,
        )
    if getattr(args, "changes_json", None) is not None:
        options["changes"] = _parse_json_option(
            args.changes_json,
            "changes_json",
            allow_file_path=True,
        )
    if getattr(args, "tasks_json", None) is not None:
        options["tasks"] = _parse_json_option(
            args.tasks_json,
            "tasks_json",
            allow_file_path=True,
        )
    if getattr(args, "front_matter_json", None) is not None:
        options["front_matter"] = _parse_json_option(
            args.front_matter_json,
            "front_matter_json",
            allow_file_path=True,
        )
    if getattr(args, "pack_json", None) is not None:
        options["pack"] = _parse_json_option(
            args.pack_json,
            "pack_json",
            allow_file_path=True,
        )
    if getattr(args, "changed_paths_json", None) is not None:
        options["changed_paths"] = _parse_json_option(
            args.changed_paths_json, "changed_paths_json"
        )
    if getattr(args, "produced_outputs_json", None) is not None:
        options["produced_outputs"] = _parse_json_option(
            args.produced_outputs_json, "produced_outputs_json"
        )
    if getattr(args, "check_results_json", None) is not None:
        options["check_results"] = _parse_json_option(
            args.check_results_json, "check_results_json"
        )
    if hasattr(args, "apply"):
        options["dry_run"] = not bool(args.apply)
    if getattr(args, "human_context", False):
        options["human_context"] = True
    return options

def _parse_json_option(raw: str, key: str, *, allow_file_path: bool = False) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        if allow_file_path:
            path = Path(raw)
            if path.exists() and path.is_file():
                text = path.read_text(encoding="utf-8")
                try:
                    return json.loads(text)
                except json.JSONDecodeError as file_exc:
                    raise CliError(
                        "invalid_option",
                        f"{key} file must contain valid json",
                        {
                            "key": key,
                            "path": str(path),
                            "error": str(file_exc),
                        },
                    ) from file_exc
        raise CliError(
            "invalid_option",
            (
                f"{key} must be valid json"
                if not allow_file_path
                else f"{key} must be valid json or a path to a json file"
            ),
            {"key": key, "error": str(exc)},
        ) from exc


def _read_content_file_option(raw_path: str, *, key: str) -> str:
    path = Path(raw_path)
    if not path.exists() or not path.is_file():
        raise CliError(
            "invalid_option",
            f"{key} must point to an existing file",
            {"key": key, "path": raw_path},
        )
    return path.read_text(encoding="utf-8")
