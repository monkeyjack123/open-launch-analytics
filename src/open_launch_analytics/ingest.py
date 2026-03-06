from __future__ import annotations

from typing import Any

from .auth import validate_api_key
from .events import normalize_event, validate_event


def ingest_event(
    payload: dict[str, Any],
    *,
    api_key: str | None = None,
    valid_api_keys: set[str] | None = None,
) -> dict[str, Any]:
    """Validate API key (optional), then validate and normalize event payload.

    When ``valid_api_keys`` is provided, ``api_key`` must be present and valid.
    Returns an API-friendly response envelope that a future HTTP route can
    return directly.
    """

    if valid_api_keys is not None:
        auth_result = validate_api_key(api_key, valid_api_keys)
        if not auth_result["ok"]:
            return {
                "ok": False,
                "status": auth_result["status"],
                "errors": auth_result["errors"],
                "event": None,
            }

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
