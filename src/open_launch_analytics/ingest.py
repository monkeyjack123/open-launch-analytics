from __future__ import annotations

from time import perf_counter
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


def ingest_batch(
    payloads: list[dict[str, Any]],
    *,
    api_key: str | None = None,
    valid_api_keys: set[str] | None = None,
) -> dict[str, Any]:
    """Ingest a batch of events and return per-item results plus summary counts."""

    results = [
        ingest_event(payload, api_key=api_key, valid_api_keys=valid_api_keys)
        for payload in payloads
    ]

    accepted = sum(1 for item in results if item["ok"])
    rejected = len(results) - accepted

    return {
        "ok": rejected == 0,
        "status": 207 if rejected else 202,
        "total": len(results),
        "accepted": accepted,
        "rejected": rejected,
        "results": results,
    }


def measure_ingest_throughput(
    payloads: list[dict[str, Any]],
    *,
    repeats: int = 1,
    api_key: str | None = None,
    valid_api_keys: set[str] | None = None,
) -> dict[str, Any]:
    """Run simple ingestion benchmark and report events/second.

    This is a lightweight developer utility (not a production load test).
    """

    if repeats < 1:
        raise ValueError("repeats must be >= 1")

    start = perf_counter()
    last_result: dict[str, Any] | None = None

    for _ in range(repeats):
        last_result = ingest_batch(
            payloads,
            api_key=api_key,
            valid_api_keys=valid_api_keys,
        )

    elapsed_seconds = perf_counter() - start
    processed_events = len(payloads) * repeats
    events_per_second = processed_events / elapsed_seconds if elapsed_seconds > 0 else None

    return {
        "processed_events": processed_events,
        "elapsed_seconds": elapsed_seconds,
        "events_per_second": events_per_second,
        "last_batch": last_result,
    }
