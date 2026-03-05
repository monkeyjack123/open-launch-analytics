# open-launch-analytics

Open source launch attribution and analytics dashboard.

## MVP increment shipped (2026-03-05)

Implemented core event contract utilities for backlog Issues **#1 (schema/validation)**, **#3 (UTM normalization)**, and MVP-ready ingest response envelope for **#2 (ingestion endpoint contract)**:

- `validate_event(payload)` returns field-level validation errors
- `normalize_event(payload)` trims/lowercases UTM values and applies defaults
- `ingest_event(payload)` returns API-ready `{ok,status,errors,event}` response envelopes
- unit tests covering success + failure behavior
- schema contract docs in `docs/event-schema.md`

Added first-touch attribution MVP logic for backlog **Issue #4**:

- `build_first_touch_attribution(events)` returns deterministic per-user first-touch UTM records
- attribution only considers tagged events (not default `direct/unknown` fallbacks)
- deterministic tie-break on equal timestamps using `event_id`
- tests for earliest-touch selection and tie-break behavior
- attribution contract docs in `docs/first-touch-attribution.md`

Added last-touch attribution MVP logic for backlog **Issue #5**:

- `build_last_touch_attribution(events)` returns deterministic per-user last-touch UTM records
- attribution only considers tagged events (not default `direct/unknown` fallbacks)
- deterministic tie-break on equal timestamps using lexicographically larger `event_id`
- tests for latest-touch selection and tie-break behavior
- attribution contract docs in `docs/last-touch-attribution.md`

## Quickstart

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Repo layout

- `src/open_launch_analytics/events.py` — validation + normalization logic
- `src/open_launch_analytics/attribution.py` — first/last-touch attribution logic
- `tests/test_events.py` — event contract tests
- `tests/test_attribution.py` — attribution tests
- `docs/event-schema.md` — ingestion contract
- `docs/first-touch-attribution.md` — first-touch contract
- `docs/last-touch-attribution.md` — last-touch contract
