from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from .events import normalize_event, validate_event


TRACKED_UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign")
DEFAULT_CONVERSION_EVENTS = frozenset({"signup", "activation"})


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


def build_attribution_completeness_report(
    events: list[dict[str, Any]],
    *,
    conversion_events: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Measure attribution-tag completeness for conversion events.

    Counts only valid payloads whose ``event_name`` is in ``conversion_events``
    (defaults to signup + activation) and reports how many still land in fallback
    ``direct/unknown`` UTM buckets after normalization.
    """

    allowed_events = {
        str(name).strip().lower()
        for name in (conversion_events if conversion_events is not None else DEFAULT_CONVERSION_EVENTS)
        if str(name).strip()
    }
    if not allowed_events:
        raise ValueError("conversion_events must contain at least one non-empty event name")

    conversions = 0
    unattributed_conversions = 0

    for event in events:
        if validate_event(event):
            continue

        normalized = normalize_event(event)
        if normalized["event_name"] not in allowed_events:
            continue

        conversions += 1
        if any(normalized[field] in {"direct", "unknown"} for field in TRACKED_UTM_FIELDS):
            unattributed_conversions += 1

    attributed_conversions = conversions - unattributed_conversions
    attribution_match_rate = (attributed_conversions / conversions) if conversions else None

    return {
        "conversion_events": sorted(allowed_events),
        "conversions": conversions,
        "attributed_conversions": attributed_conversions,
        "unattributed_conversions": unattributed_conversions,
        "attribution_match_rate": attribution_match_rate,
    }


def build_ingestion_slo_report(
    samples: list[dict[str, Any]],
    *,
    max_error_rate: float = 0.005,
    max_p95_latency_ms: float = 500.0,
) -> dict[str, Any]:
    """Summarize ingestion SLO posture from request-level telemetry samples.

    Expected sample keys:
    - ``ok`` (bool): whether request succeeded
    - ``latency_ms`` (int/float): request latency in milliseconds

    Invalid rows (missing/negative/non-numeric latency) are ignored for latency
    percentile math but still counted under ``invalid_samples`` for visibility.
    """

    total = len(samples)
    errors = 0
    invalid_samples = 0
    latencies: list[float] = []

    for sample in samples:
        if not sample.get("ok", False):
            errors += 1

        latency_raw = sample.get("latency_ms")
        if isinstance(latency_raw, (int, float)) and latency_raw >= 0:
            latencies.append(float(latency_raw))
        else:
            invalid_samples += 1

    error_rate = (errors / total) if total else None

    p95_latency_ms = None
    if latencies:
        sorted_latencies = sorted(latencies)
        # nearest-rank percentile with deterministic index math
        rank = max(1, int((0.95 * len(sorted_latencies)) + 0.999999))
        p95_latency_ms = sorted_latencies[rank - 1]

    slo_ok = True
    if error_rate is not None and error_rate > max_error_rate:
        slo_ok = False
    if p95_latency_ms is not None and p95_latency_ms > max_p95_latency_ms:
        slo_ok = False

    return {
        "ok": slo_ok,
        "status": "healthy" if slo_ok else "degraded",
        "samples": total,
        "invalid_samples": invalid_samples,
        "errors": errors,
        "error_rate": error_rate,
        "latency": {
            "p95_ms": p95_latency_ms,
        },
        "thresholds": {
            "max_error_rate": max_error_rate,
            "max_p95_latency_ms": max_p95_latency_ms,
        },
    }


def build_daily_quality_trend(
    events: list[dict[str, Any]],
    *,
    days: int | None = None,
) -> dict[str, Any]:
    """Build per-day payload quality trend rows for dashboard/reporting use.

    Groups events by UTC calendar day derived from event ``timestamp`` and returns
    per-day invalid payload and missing-UTM rates.

    Invalid payloads missing a parsable timestamp are excluded from day rows and
    counted under ``unassigned_invalid_events``.
    """

    if days is not None and days <= 0:
        raise ValueError("days must be positive when provided")

    buckets: dict[date, dict[str, int]] = {}
    unassigned_invalid_events = 0

    for event in events:
        errors = validate_event(event)
        timestamp_raw = event.get("timestamp")

        day_key: date | None = None
        if isinstance(timestamp_raw, str):
            try:
                day_key = date.fromisoformat(timestamp_raw[:10])
            except ValueError:
                day_key = None

        if day_key is None:
            if errors:
                unassigned_invalid_events += 1
            continue

        bucket = buckets.setdefault(
            day_key,
            {
                "events": 0,
                "invalid_events": 0,
                "missing_utm_events": 0,
            },
        )
        bucket["events"] += 1

        if errors:
            bucket["invalid_events"] += 1
            continue

        normalized = normalize_event(event)
        if any(normalized[field] in {"direct", "unknown"} for field in TRACKED_UTM_FIELDS):
            bucket["missing_utm_events"] += 1

    sorted_days = sorted(buckets)
    if days is not None:
        sorted_days = sorted_days[-days:]

    rows = []
    for day in sorted_days:
        bucket = buckets[day]
        total = bucket["events"]
        rows.append(
            {
                "date": day.isoformat(),
                "events": total,
                "invalid_events": bucket["invalid_events"],
                "invalid_payload_rate": (bucket["invalid_events"] / total) if total else 0.0,
                "missing_utm_events": bucket["missing_utm_events"],
                "missing_utm_rate": (bucket["missing_utm_events"] / total) if total else 0.0,
            }
        )

    return {
        "days": days,
        "rows": rows,
        "unassigned_invalid_events": unassigned_invalid_events,
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
