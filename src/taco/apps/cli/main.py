from __future__ import annotations

import json
from pathlib import Path

from taco.apps.cli.errors import CliError
from taco.apps.cli.mapper import map_cli_to_tool
from taco.apps.cli.options import _to_options
from taco.apps.cli.parser import build_parser
from taco.apps.cli.render import _render_human_context
from taco.apps.composition import (
    ToolError,
    build_repo_state,
    call_bootstrap_tool,
    call_tool,
)


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    human_context = False
    try:
        options = _to_options(args)
        human_context = bool(options.get("human_context", False))
        root = cwd or Path.cwd()
        action = str(getattr(args, "action", "") or "")
        if args.domain == "plan" and action == "intent":
            intent_action = str(getattr(args, "intent_action", "") or "")
            action = f"intent.{intent_action}"
        if args.domain == "plan" and action == "mode":
            mode_action = str(getattr(args, "mode_action", "") or "")
            action = f"mode.{mode_action}"
        if args.domain == "plan" and action == "design":
            design_action = str(getattr(args, "design_action", "") or "")
            action = f"design.{design_action}"
        if args.domain == "plan" and action == "task":
            plan_task_action = str(getattr(args, "plan_task_action", "") or "")
            action = f"task.{plan_task_action}"
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
            state = build_repo_state(root, config_path)
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


if __name__ == "__main__":
    raise SystemExit(main())
