from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from taco.cli import CliError, map_cli_to_tool
from taco.tools import ToolError, call_bootstrap_tool, call_tool, load_repo_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taco")
    parser.add_argument("--config", default="taco.yaml", help="config file path")

    domain_subparsers = parser.add_subparsers(dest="domain", required=True)
    domain_subparsers.add_parser("init")

    task_parser = domain_subparsers.add_parser("task")
    task_sub = task_parser.add_subparsers(dest="action", required=True)
    task_sub.add_parser("list")
    task_pack = task_sub.add_parser("pack")
    task_pack.add_argument("--task-id", required=True)
    task_pack.add_argument("--budget-tokens", type=int, default=None)

    task_targets = task_sub.add_parser("targets")
    task_targets.add_argument("--task-id", required=True)
    task_targets.add_argument("--route-type", required=True)

    task_record = task_sub.add_parser("record")
    task_record.add_argument("--task-id", required=True)
    task_record.add_argument("--route-type", required=True)
    task_record.add_argument("--content", required=True)
    task_record.add_argument("--apply", action="store_true")

    task_complete = task_sub.add_parser("complete")
    task_complete.add_argument("--task-id", required=True)
    task_complete.add_argument("--implementation", required=True)
    task_complete.add_argument("--verification", required=True)
    task_complete.add_argument("--apply", action="store_true")

    task_block = task_sub.add_parser("block")
    task_block.add_argument("--task-id", required=True)
    task_block.add_argument("--reason-code", required=True)
    task_block.add_argument("--reason", required=True)
    task_block.add_argument("--apply", action="store_true")

    doc_parser = domain_subparsers.add_parser("doc")
    doc_sub = doc_parser.add_subparsers(dest="action", required=True)
    doc_snippet = doc_sub.add_parser("snippet")
    doc_snippet.add_argument("--path", required=True)
    doc_snippet.add_argument("--anchor-id", required=True)

    issue_parser = domain_subparsers.add_parser("issue")
    issue_sub = issue_parser.add_subparsers(dest="action", required=True)
    issue_triage = issue_sub.add_parser("triage")
    issue_triage.add_argument("--title", required=True)

    conv_parser = domain_subparsers.add_parser("convention")
    conv_sub = conv_parser.add_subparsers(dest="action", required=True)
    conv_get = conv_sub.add_parser("get")
    conv_get.add_argument("--topic", default="git")

    plan_parser = domain_subparsers.add_parser("plan")
    plan_sub = plan_parser.add_subparsers(dest="action", required=True)
    plan_sub.add_parser("view")
    plan_locate = plan_sub.add_parser("locate")
    plan_locate.add_argument("--change-type", required=True)
    plan_locate.add_argument("--target", default="")
    plan_sub.add_parser("validate")

    return parser


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = _to_options(args)

    try:
        root = cwd or Path.cwd()
        action = str(getattr(args, "action", "") or "")
        tool_name, payload = map_cli_to_tool(args.domain, action, options)
        if tool_name == "project.init":
            response = call_bootstrap_tool(root, tool_name, payload)
        else:
            config_path = (root / str(args.config)).resolve()
            state = load_repo_state(root, config_path)
            response = call_tool(state, tool_name, payload)
    except (CliError, ToolError, FileNotFoundError) as exc:
        if isinstance(exc, (CliError, ToolError)):
            response = {
                "ok": False,
                "error": {
                    "code": exc.code,
                    "message": str(exc),
                    "details": exc.details,
                },
            }
        else:
            response = {
                "ok": False,
                "error": {
                    "code": "config_not_found",
                    "message": str(exc),
                    "details": {},
                },
            }

    print(json.dumps(response, ensure_ascii=False))
    return 0 if response.get("ok") else 1


def _to_options(args: argparse.Namespace) -> dict[str, Any]:
    options: dict[str, Any] = {}
    if getattr(args, "task_id", None) is not None:
        options["task_id"] = args.task_id
    if getattr(args, "route_type", None) is not None:
        options["route_type"] = args.route_type
    if getattr(args, "content", None) is not None:
        options["content"] = args.content
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
    if getattr(args, "anchor_id", None) is not None:
        options["anchor_id"] = args.anchor_id
    if getattr(args, "title", None) is not None:
        options["title"] = args.title
    if getattr(args, "topic", None) is not None:
        options["topic"] = args.topic
    if getattr(args, "change_type", None) is not None:
        options["change_type"] = args.change_type
    if getattr(args, "target", None) is not None:
        options["target"] = args.target
    if getattr(args, "budget_tokens", None) is not None:
        options["budget_tokens"] = args.budget_tokens
    if hasattr(args, "apply"):
        options["dry_run"] = not bool(args.apply)
    return options


if __name__ == "__main__":
    raise SystemExit(main())
