from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


DEFAULT_FUNNEL = ("visit", "signup", "activation")


def build_sample_events(
    users: int = 3,
    start_at: datetime | None = None,
) -> list[dict[str, Any]]:
    """Build deterministic sample launch events for quick local trials.

    Produces a small funnel dataset with one event per funnel step per user.
    """

    if users <= 0:
        return []

    base = start_at or datetime.now(timezone.utc).replace(microsecond=0)
    events: list[dict[str, Any]] = []

    for user_index in range(1, users + 1):
        source = "twitter" if user_index % 2 else "newsletter"
        campaign = "spring-launch"

        for step_index, event_name in enumerate(DEFAULT_FUNNEL):
            ts = base + timedelta(minutes=(user_index * 10 + step_index))
            events.append(
                {
                    "event_id": f"sample-{user_index}-{event_name}",
                    "user_id": f"user-{user_index}",
                    "event_name": event_name,
                    "timestamp": ts.isoformat().replace("+00:00", "Z"),
                    "utm_source": source,
                    "utm_medium": "social",
                    "utm_campaign": campaign,
                }
            )

    return events


def sample_events_to_ndjson(events: list[dict[str, Any]]) -> str:
    """Serialize event dicts to line-delimited JSON for curl/httpie pipelines."""

    import json

    return "\n".join(json.dumps(event, separators=(",", ":")) for event in events)
