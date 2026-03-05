from __future__ import annotations

from datetime import datetime
from typing import Any

from .events import normalize_event

CONVERSION_EVENT_NAMES = {"visit", "signup", "activation"}


def _parse_date(value: str) -> str | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.date().isoformat()


def aggregate_conversion_metrics(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate visits/signups/activations by date/source/campaign.

    Returns sorted rows with conversion-rate fields:
    - signup_rate = signups / visits
    - activation_rate = activations / signups
    """

    buckets: dict[tuple[str, str, str], dict[str, Any]] = {}

    for raw_event in events:
        event = normalize_event(raw_event)
        event_name = event.get("event_name")
        timestamp = event.get("timestamp")

        if not isinstance(event_name, str) or event_name not in CONVERSION_EVENT_NAMES:
            continue
        if not isinstance(timestamp, str) or not timestamp.strip():
            continue

        day = _parse_date(timestamp)
        if day is None:
            continue

        source = event["utm_source"]
        campaign = event["utm_campaign"]
        key = (day, source, campaign)

        if key not in buckets:
            buckets[key] = {
                "date": day,
                "utm_source": source,
                "utm_campaign": campaign,
                "visits": 0,
                "signups": 0,
                "activations": 0,
            }

        if event_name == "visit":
            buckets[key]["visits"] += 1
        elif event_name == "signup":
            buckets[key]["signups"] += 1
        elif event_name == "activation":
            buckets[key]["activations"] += 1

    rows = list(buckets.values())
    for row in rows:
        visits = row["visits"]
        signups = row["signups"]
        activations = row["activations"]
        row["signup_rate"] = (signups / visits) if visits else None
        row["activation_rate"] = (activations / signups) if signups else None

    rows.sort(key=lambda r: (r["date"], r["utm_source"], r["utm_campaign"]))
    return rows


def backfill_conversion_metrics(
    events: list[dict[str, Any]],
    start_date: str,
    end_date: str,
) -> list[dict[str, Any]]:
    """Recompute conversion metrics for an inclusive date range (YYYY-MM-DD)."""

    filtered: list[dict[str, Any]] = []
    for event in events:
        timestamp = event.get("timestamp")
        if not isinstance(timestamp, str) or not timestamp.strip():
            continue

        day = _parse_date(timestamp)
        if day is None:
            continue
        if start_date <= day <= end_date:
            filtered.append(event)

    return aggregate_conversion_metrics(filtered)
