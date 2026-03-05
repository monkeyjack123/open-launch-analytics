# First-touch attribution contract

`build_first_touch_attribution(events)` creates a per-user attribution table from raw events.

## Rules

1. Each input event is normalized via `normalize_event`.
2. Only UTM-tagged events are eligible:
   - `utm_source != direct` OR
   - `utm_medium != unknown` OR
   - `utm_campaign != unknown`
3. For each `user_id`, choose the earliest event by timestamp.
4. If timestamps tie, select lexicographically smaller `event_id` for deterministic output.

## Output shape

```python
{
  "user_123": {
    "event_id": "evt_1",
    "timestamp": "2026-03-05T08:00:00Z",
    "utm_source": "x",
    "utm_medium": "unknown",
    "utm_campaign": "launch",
    "utm_term": "unknown",
    "utm_content": "unknown",
  }
}
```

This is intended as the MVP in-memory contract before wiring a persistent `user_attribution` table/job.
