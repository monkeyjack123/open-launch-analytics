from __future__ import annotations

from datetime import datetime
from typing import Any

from .events import normalize_event


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _is_utm_tagged(event: dict[str, Any]) -> bool:
    return (
        event.get("utm_source") != "direct"
        or event.get("utm_medium") != "unknown"
        or event.get("utm_campaign") != "unknown"
    )


def build_first_touch_attribution(events: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Build first-touch attribution per user from raw event list.

    Rules:
    - normalize each event before attribution
    - only UTM-tagged events are eligible
    - choose earliest timestamp per user
    - tie-break on event_id for deterministic output
    """

    winners: dict[str, dict[str, Any]] = {}

    for raw_event in events:
        event = normalize_event(raw_event)
        user_id = event.get("user_id")
        timestamp = event.get("timestamp")
        event_id = event.get("event_id")

        if not isinstance(user_id, str) or not user_id.strip():
            continue
        if not isinstance(timestamp, str) or not timestamp.strip():
            continue
        if not isinstance(event_id, str) or not event_id.strip():
            continue
        if not _is_utm_tagged(event):
            continue

        candidate = {
            "event_id": event_id,
            "timestamp": timestamp,
            "utm_source": event["utm_source"],
            "utm_medium": event["utm_medium"],
            "utm_campaign": event["utm_campaign"],
            "utm_term": event["utm_term"],
            "utm_content": event["utm_content"],
        }

        current = winners.get(user_id)
        if current is None:
            winners[user_id] = candidate
            continue

        candidate_ts = _parse_timestamp(candidate["timestamp"])
        current_ts = _parse_timestamp(current["timestamp"])

        if candidate_ts < current_ts:
            winners[user_id] = candidate
        elif candidate_ts == current_ts and candidate["event_id"] < current["event_id"]:
            winners[user_id] = candidate

    return winners
