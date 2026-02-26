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
        return "plan.intent.propose", {
            "intent_id": required_str_option(options, "intent_id")
        }
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
