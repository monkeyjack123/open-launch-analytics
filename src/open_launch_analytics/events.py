from __future__ import annotations

from datetime import datetime
from typing import Any

REQUIRED_FIELDS = {
    "event_id": str,
    "event_name": str,
    "timestamp": str,
    "user_id": str,
}

OPTIONAL_STR_FIELDS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
]


def _is_iso8601(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def normalize_event(payload: dict[str, Any]) -> dict[str, Any]:
    event = dict(payload)
    defaults = {
        "utm_source": "direct",
        "utm_medium": "unknown",
        "utm_campaign": "unknown",
        "utm_term": "unknown",
        "utm_content": "unknown",
    }

    for key, fallback in defaults.items():
        value = event.get(key)
        if value is None:
            event[key] = fallback
            continue

        cleaned = str(value).strip().lower()
        event[key] = cleaned if cleaned else fallback

    return event


def validate_event(payload: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in payload:
            errors.append({"field": field, "error": "missing_required", "message": f"{field} is required"})
            continue

        value = payload[field]
        if not isinstance(value, expected_type) or (isinstance(value, str) and not value.strip()):
            errors.append({
                "field": field,
                "error": "invalid_type",
                "message": f"{field} must be a non-empty {expected_type.__name__}",
            })

    ts = payload.get("timestamp")
    if isinstance(ts, str) and ts.strip() and not _is_iso8601(ts):
        errors.append({
            "field": "timestamp",
            "error": "invalid_format",
            "message": "timestamp must be ISO-8601 (e.g., 2026-03-05T09:00:00Z)",
        })

    for field in OPTIONAL_STR_FIELDS:
        if field in payload and payload[field] is not None and not isinstance(payload[field], str):
            errors.append({
                "field": field,
                "error": "invalid_type",
                "message": f"{field} must be string when provided",
            })

    return errors
