from __future__ import annotations

from typing import Any

from .events import normalize_event, validate_event


def ingest_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a single event payload.

    Returns an API-friendly response envelope that a future HTTP route can
    return directly.
    """

    errors = validate_event(payload)
    if errors:
        return {
            "ok": False,
            "status": 400,
            "errors": errors,
            "event": None,
        }

    normalized = normalize_event(payload)
    return {
        "ok": True,
        "status": 202,
        "errors": [],
        "event": normalized,
    }
