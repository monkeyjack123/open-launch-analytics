from __future__ import annotations

from datetime import datetime
from typing import Any

from .events import normalize_event

SIGNUP_EVENT_NAMES = {"signup"}
ACTIVATION_EVENT_NAMES = {"activation", "activated"}


def _parse_date(value: str) -> datetime.date | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _normalize_days(days: tuple[int, ...]) -> tuple[int, ...]:
    normalized = sorted({day for day in days if isinstance(day, int) and day >= 0})
    if not normalized:
        raise ValueError("days must contain at least one non-negative integer")
    return tuple(normalized)


def build_signup_cohorts(
    events: list[dict[str, Any]],
    days: tuple[int, ...] = (0, 1, 7),
    utm_source: str | None = None,
    utm_campaign: str | None = None,
) -> list[dict[str, Any]]:
    """Build signup cohorts with activation retention rates for selected day offsets.

    A user is assigned to the earliest signup date found in the input event stream.
    Activation is counted for a day offset when an activation event exists on that
    exact offset from the user's cohort date.
    """

    days = _normalize_days(days)

    normalized_source = utm_source.strip().lower() if isinstance(utm_source, str) else None
    normalized_campaign = (
        utm_campaign.strip().lower() if isinstance(utm_campaign, str) else None
    )

    user_signup_day: dict[str, datetime.date] = {}
    user_activation_days: dict[str, set[int]] = {}

    for raw_event in events:
        event = normalize_event(raw_event)
        event_name = event.get("event_name")
        user_id = event.get("user_id")
        timestamp = event.get("timestamp")

        if not isinstance(user_id, str) or not user_id.strip():
            continue
        if not isinstance(timestamp, str) or not timestamp.strip():
            continue
        if not isinstance(event_name, str):
            continue

        source = event.get("utm_source")
        campaign = event.get("utm_campaign")

        if normalized_source is not None and source != normalized_source:
            continue
        if normalized_campaign is not None and campaign != normalized_campaign:
            continue

        day = _parse_date(timestamp)
        if day is None:
            continue

        if event_name in SIGNUP_EVENT_NAMES:
            previous_signup_day = user_signup_day.get(user_id)
            if previous_signup_day is None or day < previous_signup_day:
                user_signup_day[user_id] = day
        elif event_name in ACTIVATION_EVENT_NAMES:
            # Store absolute activation day; day offsets are computed after
            # we finalize earliest signup dates.
            user_activation_days.setdefault(user_id, set()).add(day.toordinal())

    cohort_users: dict[datetime.date, set[str]] = {}
    for user_id, signup_day in user_signup_day.items():
        cohort_users.setdefault(signup_day, set()).add(user_id)

    rows: list[dict[str, Any]] = []
    for cohort_day, users in sorted(cohort_users.items(), key=lambda item: item[0]):
        row: dict[str, Any] = {
            "cohort_date": cohort_day.isoformat(),
            "signups": len(users),
        }

        for offset in days:
            activated_users = 0
            for user_id in users:
                activation_ordinals = user_activation_days.get(user_id, set())
                target_ordinal = cohort_day.toordinal() + offset
                if target_ordinal in activation_ordinals:
                    activated_users += 1

            row[f"d{offset}_activated"] = activated_users
            row[f"d{offset}_rate"] = (activated_users / len(users)) if users else None

        rows.append(row)

    return rows


def build_cohort_matrix(
    events: list[dict[str, Any]],
    days: tuple[int, ...] = (0, 1, 7),
    utm_source: str | None = None,
    utm_campaign: str | None = None,
) -> dict[str, Any]:
    """Build a dashboard-friendly cohort matrix envelope with column metadata.

    Returns:
      {
        "columns": [...],
        "legend": {...},
        "rows": [...],
        "totals": {...}
      }
    """

    normalized_days = _normalize_days(days)
    rows = build_signup_cohorts(
        events,
        days=normalized_days,
        utm_source=utm_source,
        utm_campaign=utm_campaign,
    )

    columns = [
        {"key": "cohort_date", "label": "Cohort"},
        {"key": "signups", "label": "Signups"},
    ]
    legend: dict[str, str] = {}

    for offset in normalized_days:
        columns.append(
            {
                "key": f"d{offset}_activated",
                "label": f"D{offset} activated",
            }
        )
        columns.append(
            {
                "key": f"d{offset}_rate",
                "label": f"D{offset} activation rate",
            }
        )
        if offset == 0:
            legend[f"d{offset}"] = "Users who activated on the same day as signup"
        else:
            legend[f"d{offset}"] = f"Users who activated exactly {offset} day(s) after signup"

    total_signups = sum(row.get("signups", 0) for row in rows)
    totals: dict[str, Any] = {"cohort_date": "TOTAL", "signups": total_signups}

    for offset in normalized_days:
        activated_key = f"d{offset}_activated"
        rate_key = f"d{offset}_rate"
        total_activated = sum(row.get(activated_key, 0) for row in rows)
        totals[activated_key] = total_activated
        totals[rate_key] = (total_activated / total_signups) if total_signups else None

    return {
        "columns": columns,
        "legend": legend,
        "rows": rows,
        "totals": totals,
    }
