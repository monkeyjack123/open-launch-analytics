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

## Validation response shape (planned API)

Invalid payloads should return a structured 400 body:

```json
{
  "error": "invalid_payload",
  "errors": [
    {
      "field": "timestamp",
      "error": "invalid_format",
      "message": "timestamp must be ISO-8601"
    }
  ]
}
```
