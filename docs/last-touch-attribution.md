# Last-touch attribution contract

`build_last_touch_attribution(events)` creates a per-user attribution table from raw events.

## Rules

1. Each input event is normalized via `normalize_event`.
2. Only UTM-tagged events are eligible:
   - `utm_source != direct` OR
   - `utm_medium != unknown` OR
   - `utm_campaign != unknown`
3. For each `user_id`, choose the latest event by timestamp.
4. If timestamps tie, select lexicographically larger `event_id` for deterministic output.
5. Events with malformed timestamps are ignored (defensive behavior for dirty streams).

## Output shape

```python
{
  "user_123": {
    "event_id": "evt_99",
    "timestamp": "2026-03-05T12:15:00Z",
    "utm_source": "linkedin",
    "utm_medium": "paid-social",
    "utm_campaign": "spring-launch",
    "utm_term": "unknown",
    "utm_content": "creative-a",
  }
}
```

This complements first-touch attribution and can be used for conversion-credit views in the MVP dashboard.
