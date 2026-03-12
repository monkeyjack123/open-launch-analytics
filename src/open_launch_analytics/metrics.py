from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from .events import normalize_event

CONVERSION_EVENT_NAMES = {"visit", "signup", "activation"}
DATE_PRESETS = {"7d": 7, "30d": 30}


def _parse_date(value: str) -> str | None:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.date().isoformat()


def _within_date_range(day: str, start_date: str | None, end_date: str | None) -> bool:
    if start_date is not None and day < start_date:
        return False
    if end_date is not None and day > end_date:
        return False
    return True


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


def resolve_date_range(
    preset: str,
    *,
    today: date | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> tuple[str, str]:
    """Resolve dashboard date filters for `7d`, `30d`, and `custom` presets.

    - `7d` and `30d` are inclusive windows ending at `today`
    - `custom` requires both `start_date` and `end_date` in YYYY-MM-DD format
    """

    normalized_preset = preset.strip().lower()
    resolved_today = today or date.today()

    if normalized_preset in DATE_PRESETS:
        days = DATE_PRESETS[normalized_preset]
        resolved_end = resolved_today
        resolved_start = resolved_today - timedelta(days=days - 1)
        return resolved_start.isoformat(), resolved_end.isoformat()

    if normalized_preset == "custom":
        if not isinstance(start_date, str) or not isinstance(end_date, str):
            raise ValueError("custom preset requires start_date and end_date")
        if _parse_date(start_date) != start_date or _parse_date(end_date) != end_date:
            raise ValueError("custom start_date/end_date must be YYYY-MM-DD")
        if start_date > end_date:
            raise ValueError("custom start_date must be <= end_date")
        return start_date, end_date

    raise ValueError("unsupported preset; expected one of: 7d, 30d, custom")


def summarize_funnel(
    events: list[dict[str, Any]],
    start_date: str | None = None,
    end_date: str | None = None,
    utm_source: str | None = None,
    utm_campaign: str | None = None,
) -> dict[str, Any]:
    """Return top-card funnel totals and rates for dashboard filters.

    Optional filters:
    - start_date / end_date: inclusive YYYY-MM-DD bounds
    - utm_source / utm_campaign: normalized via event normalization rules
    """

    visits = 0
    signups = 0
    activations = 0

    normalized_source = utm_source.strip().lower() if isinstance(utm_source, str) else None
    normalized_campaign = utm_campaign.strip().lower() if isinstance(utm_campaign, str) else None

    for raw_event in events:
        event = normalize_event(raw_event)
        event_name = event.get("event_name")
        timestamp = event.get("timestamp")

        if not isinstance(event_name, str) or event_name not in CONVERSION_EVENT_NAMES:
            continue
        if not isinstance(timestamp, str) or not timestamp.strip():
            continue

        day = _parse_date(timestamp)
        if day is None or not _within_date_range(day, start_date, end_date):
            continue

        if normalized_source is not None and event["utm_source"] != normalized_source:
            continue
        if normalized_campaign is not None and event["utm_campaign"] != normalized_campaign:
            continue

        if event_name == "visit":
            visits += 1
        elif event_name == "signup":
            signups += 1
        elif event_name == "activation":
            activations += 1

    return {
        "visits": visits,
        "signups": signups,
        "activations": activations,
        "signup_rate": (signups / visits) if visits else None,
        "activation_rate": (activations / signups) if signups else None,
    }


def build_funnel_breakdown(
    events: list[dict[str, Any]],
    start_date: str | None = None,
    end_date: str | None = None,
    utm_source: str | None = None,
    utm_campaign: str | None = None,
    sort_by: str = "visits",
    descending: bool = True,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Build source/campaign breakdown rows for dashboard table rendering.

    The output is grouped by normalized `utm_source` + `utm_campaign` and includes
    visits/signups/activations with conversion rates. Supports dashboard-style
    filtering and deterministic sorting for table interactions.
    """

    normalized_source = utm_source.strip().lower() if isinstance(utm_source, str) else None
    normalized_campaign = utm_campaign.strip().lower() if isinstance(utm_campaign, str) else None

    buckets: dict[tuple[str, str], dict[str, Any]] = {}

    for raw_event in events:
        event = normalize_event(raw_event)
        event_name = event.get("event_name")
        timestamp = event.get("timestamp")

        if not isinstance(event_name, str) or event_name not in CONVERSION_EVENT_NAMES:
            continue
        if not isinstance(timestamp, str) or not timestamp.strip():
            continue

        day = _parse_date(timestamp)
        if day is None or not _within_date_range(day, start_date, end_date):
            continue

        source = event["utm_source"]
        campaign = event["utm_campaign"]

        if normalized_source is not None and source != normalized_source:
            continue
        if normalized_campaign is not None and campaign != normalized_campaign:
            continue

        key = (source, campaign)
        if key not in buckets:
            buckets[key] = {
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

    sortable_fields = {"utm_source", "utm_campaign", "visits", "signups", "activations", "signup_rate", "activation_rate"}
    sort_field = sort_by if sort_by in sortable_fields else "visits"

    def _sort_value(row: dict[str, Any]) -> Any:
        value = row[sort_field]
        if value is None:
            return -1 if descending else float("inf")
        return value

    rows.sort(
        key=lambda r: (
            _sort_value(r),
            r["utm_source"],
            r["utm_campaign"],
        ),
        reverse=descending,
    )

    if isinstance(limit, int) and limit >= 0:
        return rows[:limit]
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
