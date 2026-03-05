# Event Schema and Normalization (MVP)

This document defines the canonical ingestion contract for `POST /api/events` (Issue #1 + #3 backlog coverage).

## Required fields

- `event_id` (string, non-empty)
- `event_name` (string, non-empty)
- `timestamp` (ISO-8601 string)
- `user_id` (string, non-empty)

## Optional UTM fields

- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_term`
- `utm_content`

If optional UTM fields are missing or blank, defaults are applied:

- `utm_source` -> `direct`
- all other UTM fields -> `unknown`

All provided UTM values are trimmed and lowercased.

## Ingest response envelope (MVP)

`ingest_event(payload)` now returns a stable API-ready envelope used by the planned `POST /api/events` route.

Accepted payload (`202`):

```json
{
  "ok": true,
  "status": 202,
  "errors": [],
  "event": {
    "event_id": "evt_100",
    "event_name": "signup",
    "timestamp": "2026-03-05T10:00:00Z",
    "user_id": "user_100",
    "utm_source": "producthunt",
    "utm_medium": "unknown",
    "utm_campaign": "unknown",
    "utm_term": "unknown",
    "utm_content": "unknown"
  }
}
```

Invalid payload (`400`):

```json
{
  "ok": false,
  "status": 400,
  "errors": [
    {
      "field": "timestamp",
      "error": "invalid_format",
      "message": "timestamp must be ISO-8601 (e.g., 2026-03-05T09:00:00Z)"
    }
  ],
  "event": null
}
```
