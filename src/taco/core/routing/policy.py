from __future__ import annotations

ROUTE_HEADING_MAP: dict[str, str] = {
    "implementation_result": "Implementation Result",
    "implementation": "Implementation Result",
    "verification_result": "Verification Result",
    "verification": "Verification Result",
    "issue_record": "Verification Result",
}

ROUTE_MODE_MAP: dict[str, str] = {
    "implementation_result": "append_implementation",
    "implementation": "append_implementation",
    "verification_result": "append_verification",
    "verification": "append_verification",
    "issue_record": "append_issue",
}


def mode_for_heading(heading: str) -> str | None:
    for route_type, route_heading in ROUTE_HEADING_MAP.items():
        if route_heading == heading:
            return ROUTE_MODE_MAP.get(route_type)
    return None
