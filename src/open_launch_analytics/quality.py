from __future__ import annotations

from typing import Any

from .events import normalize_event, validate_event


TRACKED_UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign")


def build_data_quality_report(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Build MVP data-quality stats used by observability checks.

    Report fields:
    - total_events
    - invalid_events + invalid_payload_rate
    - missing_utm_events + missing_utm_rate

    ``missing_utm_events`` only counts events that are otherwise valid payloads.
    """

    total_events = len(events)
    invalid_events = 0
    missing_utm_events = 0

    for event in events:
        errors = validate_event(event)
        if errors:
            invalid_events += 1
            continue

        normalized = normalize_event(event)
        if any(normalized[field] in {"direct", "unknown"} for field in TRACKED_UTM_FIELDS):
            missing_utm_events += 1

    invalid_payload_rate = (invalid_events / total_events) if total_events else 0.0
    missing_utm_rate = (missing_utm_events / total_events) if total_events else 0.0

    return {
        "total_events": total_events,
        "invalid_events": invalid_events,
        "invalid_payload_rate": invalid_payload_rate,
        "missing_utm_events": missing_utm_events,
        "missing_utm_rate": missing_utm_rate,
    }


def build_health_status(events: list[dict[str, Any]], *, max_invalid_payload_rate: float = 0.01) -> dict[str, Any]:
    """Return a lightweight health summary envelope for MVP dashboards/APIs."""

    quality = build_data_quality_report(events)
    healthy = quality["invalid_payload_rate"] <= max_invalid_payload_rate

    return {
        "ok": healthy,
        "status": "healthy" if healthy else "degraded",
        "thresholds": {
            "max_invalid_payload_rate": max_invalid_payload_rate,
        },
        "quality": quality,
    }
