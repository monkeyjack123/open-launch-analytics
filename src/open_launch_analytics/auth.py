from __future__ import annotations


def validate_api_key(api_key: str | None, valid_api_keys: set[str]) -> dict[str, object]:
    """Validate ingestion API key against a configured allowlist."""

    if api_key is None or not api_key.strip():
        return {
            "ok": False,
            "status": 401,
            "errors": [
                {
                    "field": "api_key",
                    "error": "missing_api_key",
                    "message": "API key is required",
                }
            ],
        }

    candidate = api_key.strip()
    if candidate not in valid_api_keys:
        return {
            "ok": False,
            "status": 403,
            "errors": [
                {
                    "field": "api_key",
                    "error": "invalid_api_key",
                    "message": "API key is invalid",
                }
            ],
        }

    return {"ok": True, "status": 200, "errors": []}
