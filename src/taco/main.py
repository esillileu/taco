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
    parser.add_argument(
        "--human-context",
        action="store_true",
        help="render supported context responses as human-readable text",
    )

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
    doc_section = doc_sub.add_parser("section")
    doc_section_sub = doc_section.add_subparsers(dest="doc_action", required=True)
    doc_section_get = doc_section_sub.add_parser("get")
    doc_section_get.add_argument("--path", required=True)
    doc_section_get.add_argument("--section-id", required=True)
    doc_section_patch = doc_section_sub.add_parser("patch")
    doc_section_patch.add_argument("--path", required=True)
    doc_section_patch.add_argument("--section-id", required=True)
    doc_section_patch.add_argument("--base-fingerprint", required=True)
    doc_section_patch.add_argument("--ops-json", required=True)
    doc_section_patch.add_argument("--apply", action="store_true")

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
    plan_pack = plan_sub.add_parser("pack")
    plan_pack.add_argument("--task-id", required=True)
    plan_pack.add_argument("--budget-tokens", type=int, default=None)
    plan_intent = plan_sub.add_parser("intent")
    plan_intent_sub = plan_intent.add_subparsers(dest="intent_action", required=True)
    plan_intent_sub.add_parser("list")
    plan_intent_view = plan_intent_sub.add_parser("view")
    plan_intent_view.add_argument("--intent-id", required=True)
    plan_intent_index = plan_intent_sub.add_parser("index")
    plan_intent_index.add_argument("--intent-id", required=True)
    plan_intent_index.add_argument("--budget-tokens", type=int, default=None)
    plan_intent_validate = plan_intent_sub.add_parser("validate")
    plan_intent_validate.add_argument("--intent-id", required=True)
    plan_sub.add_parser("view")
    plan_locate = plan_sub.add_parser("locate")
    plan_locate.add_argument("--change-type", required=True)
    plan_locate.add_argument("--target", default="")
    plan_sub.add_parser("validate")

    build_parser = domain_subparsers.add_parser("build")
    build_sub = build_parser.add_subparsers(dest="action", required=True)
    build_precheck = build_sub.add_parser("precheck")
    build_precheck.add_argument("--pack-json", required=True)
    build_postcheck = build_sub.add_parser("postcheck")
    build_postcheck.add_argument("--pack-json", required=True)
    build_postcheck.add_argument("--changed-paths-json", default="[]")
    build_postcheck.add_argument("--produced-outputs-json", default="[]")
    build_postcheck.add_argument("--check-results-json", default="{}")

    return parser


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options = _to_options(args)

    human_context = bool(options.get("human_context", False))
    try:
        root = cwd or Path.cwd()
        action = str(getattr(args, "action", "") or "")
        if args.domain == "plan" and action == "intent":
            intent_action = str(getattr(args, "intent_action", "") or "")
            action = f"intent.{intent_action}"
        if args.domain == "doc" and action == "section":
            doc_action = str(getattr(args, "doc_action", "") or "")
            action = f"section.{doc_action}"
        tool_name, payload = map_cli_to_tool(args.domain, action, options)
        if human_context and tool_name not in {"task.pack", "doc.snippet"}:
            response = {
                "ok": False,
                "error": {
                    "code": "invalid_mode",
                    "message": (
                        "human-context mode supports only "
                        "task pack and doc snippet"
                    ),
                    "details": {"tool": tool_name},
                },
            }
            print(json.dumps(response, ensure_ascii=False))
            return 1
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

    if human_context and response.get("ok"):
        print(_render_human_context(tool_name, response.get("data", {})))
    else:
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
    if getattr(args, "section_id", None) is not None:
        options["section_id"] = args.section_id
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
    if getattr(args, "intent_id", None) is not None:
        options["intent_id"] = args.intent_id
    if getattr(args, "intent_text", None) is not None:
        options["intent_text"] = args.intent_text
    if getattr(args, "title", None) is not None:
        options["title"] = args.title
    if getattr(args, "budget_tokens", None) is not None:
        options["budget_tokens"] = args.budget_tokens
    if getattr(args, "fingerprint", None) is not None:
        options["fingerprint"] = args.fingerprint
    if getattr(args, "retry_on_fail", None) is not None:
        options["retry_on_fail"] = args.retry_on_fail
    if getattr(args, "base_fingerprint", None) is not None:
        options["base_fingerprint"] = args.base_fingerprint
    if getattr(args, "ops_json", None) is not None:
        options["ops"] = _parse_json_option(args.ops_json, "ops_json")
    if getattr(args, "pack_json", None) is not None:
        options["pack"] = _parse_json_option(args.pack_json, "pack_json")
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


def _render_human_context(tool_name: str, data: Any) -> str:
    if not isinstance(data, dict):
        return "(no data)"
    if tool_name == "task.pack":
        snippets = data.get("context_snippets", [])
        if not isinstance(snippets, list) or not snippets:
            return "(no context snippets)"
        blocks: list[str] = []
        for row in snippets:
            if not isinstance(row, dict):
                continue
            group = str(row.get("group", "")).strip() or "snippet"
            path = str(row.get("path", "")).strip() or "(unknown)"
            anchor = str(row.get("anchor_id", "")).strip()
            content = str(row.get("content", "")).rstrip()
            target = f"{path}#{anchor}" if anchor else path
            blocks.append(f"[{group}] {target}\n{content}")
        return "\n\n".join(blocks) if blocks else "(no context snippets)"
    if tool_name == "doc.snippet":
        heading = str(data.get("heading", "")).strip() or "Snippet"
        path = str(data.get("path", "")).strip() or "(unknown)"
        anchor = str(data.get("anchor_id", "")).strip()
        target = f"{path}#{anchor}" if anchor else path
        snippet = str(data.get("snippet", "")).rstrip()
        return f"{heading} ({target})\n\n{snippet}"
    return "(unsupported tool)"


def _parse_json_option(raw: str, key: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CliError(
            "invalid_option",
            f"{key} must be valid json",
            {"key": key, "error": str(exc)},
        ) from exc


if __name__ == "__main__":
    raise SystemExit(main())
