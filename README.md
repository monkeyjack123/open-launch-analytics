# open-launch-analytics

Open source launch attribution and analytics dashboard.

## MVP increment shipped (2026-03-05)

Implemented core event contract utilities for backlog Issues **#1 (schema/validation)**, **#3 (UTM normalization)**, and MVP-ready ingest response envelope for **#2 (ingestion endpoint contract)**:

- `validate_event(payload)` returns field-level validation errors
- `normalize_event(payload)` trims/lowercases UTM values and applies defaults
- `ingest_event(payload)` returns API-ready `{ok,status,errors,event}` response envelopes
- unit tests covering success + failure behavior
- schema contract docs in `docs/event-schema.md`

## Quickstart

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Repo layout

- `src/open_launch_analytics/events.py` — validation + normalization logic
- `tests/test_events.py` — MVP unit tests
- `docs/event-schema.md` — ingestion contract
