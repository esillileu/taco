from __future__ import annotations

from typing import Any

from taco.apps.cli.errors import CliError

from .common import (
    optional_budget_tokens,
    optional_dry_run,
    require_bool,
    required_str_option,
)


def _map_plan_intent_action(
    action: str, options: dict[str, Any]
) -> tuple[str, dict[str, Any]]:
    if action == "intent.list":
        return "plan.intent.list", {}
    if action == "intent.template":
        return "plan.intent.template", {}
    if action in {"intent.create-many", "intent.submit-many"}:
        intents = options.get("intents")
        if not isinstance(intents, list):
            raise CliError(
                "invalid_option",
                "intents_json must be a json array or a path to one",
                {"key": "intents_json"},
            )
        payload: dict[str, Any] = {"intents": intents}
        plan_ref = options.get("plan_ref")
        if plan_ref is not None:
            if not isinstance(plan_ref, str) or not plan_ref.strip():
                raise CliError(
                    "invalid_option",
                    "plan_ref must be a non-empty string",
                    {"key": "plan_ref"},
                )
            payload["plan_ref"] = plan_ref.strip()
        if action == "intent.submit-many":
            return "plan.intent.submit_many", payload
        return "plan.intent.create_many", payload
    if action == "intent.view":
        return "plan.intent.view", {
            "intent_id": required_str_option(options, "intent_id")
        }
    if action == "intent.index":
        payload = {"intent_id": required_str_option(options, "intent_id")}
        optional_budget_tokens(options, payload)
        return "plan.intent.index", payload
    if action == "intent.validate":
        return "plan.intent.validate", {
            "intent_id": required_str_option(options, "intent_id")
        }
    if action == "intent.propose":
        intent_id = options.get("intent_id")
        if isinstance(intent_id, str) and intent_id.strip():
            return "plan.intent.propose", {"intent_id": intent_id.strip()}
        intent_text = options.get("intent_text")
        if isinstance(intent_text, str) and intent_text.strip():
            payload = {"intent_text": intent_text.strip()}
            title = options.get("title")
            if title is not None:
                if not isinstance(title, str) or not title.strip():
                    raise CliError(
                        "invalid_option",
                        "title must be a non-empty string when provided",
                        {"key": "title"},
                    )
                payload["title"] = title.strip()
            return "plan.intent.propose", payload
        raise CliError(
            "invalid_option",
            "intent.propose requires --intent-id or --intent-text",
            {"keys": ["intent_id", "intent_text"]},
        )
    if action == "intent.autodesign":
        return "plan.intent.autodesign", {
            "intent_id": required_str_option(options, "intent_id"),
            "proposal_fingerprint": required_str_option(
                options, "proposal_fingerprint"
            ),
        }
    if action == "intent.generate-tasks":
        return "plan.intent.generate_tasks", {
            "intent_id": required_str_option(options, "intent_id"),
            "design_fingerprint": required_str_option(options, "design_fingerprint"),
        }
    if action == "intent.review-bundle":
        payload = {
            "intent_id": required_str_option(options, "intent_id"),
            "proposal_fingerprint": required_str_option(
                options, "proposal_fingerprint"
            ),
            "design_fingerprint": required_str_option(options, "design_fingerprint"),
            "taskset_fingerprint": required_str_option(options, "taskset_fingerprint"),
        }
        retry_on_fail = options.get("retry_on_fail")
        if retry_on_fail is not None:
            if not isinstance(retry_on_fail, int):
                raise CliError(
                    "invalid_option",
                    "retry_on_fail must be integer",
                    {"key": "retry_on_fail"},
                )
            payload["retry_on_fail"] = retry_on_fail
        return "plan.intent.review_bundle", payload
    if action == "intent.apply":
        payload = {
            "intent_id": required_str_option(options, "intent_id"),
            "decision_fingerprint": required_str_option(
                options, "decision_fingerprint"
            ),
        }
        approve = options.get("approve")
        if approve is not None:
            payload["approve"] = require_bool(approve, key="approve", label="approve")
        optional_dry_run(options, payload)
        return "plan.intent.apply", payload
    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": "plan", "action": action},
    )


def map_plan_action(action: str, options: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if action.startswith("intent."):
        return _map_plan_intent_action(action, options)
    if action == "mode.guide":
        stage = options.get("stage")
        if stage is None:
            return "plan.mode.guide", {}
        if not isinstance(stage, str) or not stage.strip():
            raise CliError(
                "invalid_option",
                "stage must be a non-empty string",
                {"key": "stage"},
            )
        return "plan.mode.guide", {"stage": stage.strip()}
    if action == "design.submit-changes":
        changes = options.get("changes")
        if not isinstance(changes, list):
            raise CliError(
                "invalid_option",
                "changes_json must be a json array or a path to one",
                {"key": "changes_json"},
            )
        return "plan.design.submit_changes", {"changes": changes}
    if action == "task.submit-many":
        tasks = options.get("tasks")
        if not isinstance(tasks, list):
            raise CliError(
                "invalid_option",
                "tasks_json must be a json array or a path to one",
                {"key": "tasks_json"},
            )
        return "plan.task.submit_many", {"tasks": tasks}
    if action == "task.template":
        payload: dict[str, Any] = {
            "intent_id": required_str_option(options, "intent_id")
        }
        task_id = options.get("task_id")
        if task_id is not None:
            if not isinstance(task_id, str) or not task_id.strip():
                raise CliError(
                    "invalid_option",
                    "task_id must be a non-empty string",
                    {"key": "task_id"},
                )
            payload["task_id"] = task_id.strip()
        return "plan.task.template", payload
    if action == "task.sync-frontmatter":
        payload = {
            "intent_id": required_str_option(options, "intent_id"),
            "path": required_str_option(options, "path"),
        }
        front_matter = options.get("front_matter")
        if front_matter is not None:
            if not isinstance(front_matter, dict):
                raise CliError(
                    "invalid_option",
                    "front_matter_json must be a json object or a path to one",
                    {"key": "front_matter_json"},
                )
            payload["front_matter"] = front_matter
        return "plan.task.frontmatter.sync", payload
    if action == "task.lint":
        payload = {"path": required_str_option(options, "path")}
        intent_id = options.get("intent_id")
        if intent_id is not None:
            if not isinstance(intent_id, str) or not intent_id.strip():
                raise CliError(
                    "invalid_option",
                    "intent_id must be a non-empty string",
                    {"key": "intent_id"},
                )
            payload["intent_id"] = intent_id.strip()
        return "plan.task.lint", payload
    if action == "view":
        return "plan.view", {}
    if action == "pack":
        payload = {"task_id": required_str_option(options, "task_id")}
        optional_budget_tokens(options, payload)
        return "plan.pack", payload
    if action == "locate":
        payload: dict[str, Any] = {
            "change_type": required_str_option(options, "change_type")
        }
        target = options.get("target")
        if target is not None:
            if not isinstance(target, str):
                raise CliError(
                    "invalid_option",
                    "target must be a string",
                    {"key": "target"},
                )
            payload["target"] = target.strip()
        return "plan.locate", payload
    if action == "validate":
        return "plan.validate", {}
    raise CliError(
        "unknown_command",
        "unsupported cli command",
        {"domain": "plan", "action": action},
    )
