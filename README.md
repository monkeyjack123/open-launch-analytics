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

Added conversion metrics aggregation MVP logic for backlog **Issue #5**:

- `aggregate_conversion_metrics(events)` groups by date/source/campaign with `visits/signups/activations`
- computes `signup_rate` and `activation_rate`
- `backfill_conversion_metrics(events, start_date, end_date)` supports range recomputation
- tests for grouping, rate math, and date-range backfill behavior
- pipeline contract docs in `docs/conversion-metrics.md`

Added basic cohort aggregation backend for backlog **Issue #7**:

- `build_signup_cohorts(events, days=(0,1,7), utm_source=None, utm_campaign=None)` builds daily signup cohorts
- computes D0/D1/D7 activation counts and rates per cohort
- supports normalized source/campaign filters for segmented cohort views
- tests for day-offset math and segmentation filters
- cohort contract docs in `docs/basic-cohorts.md`

## Quickstart

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Repo layout

- `src/open_launch_analytics/events.py` — validation + normalization logic
- `src/open_launch_analytics/attribution.py` — first/last-touch attribution logic
- `src/open_launch_analytics/metrics.py` — conversion metric aggregation + backfill helpers
- `src/open_launch_analytics/cohorts.py` — signup cohort aggregation (D0/D1/D7)
- `tests/test_events.py` — event contract tests
- `tests/test_attribution.py` — attribution tests
- `tests/test_metrics.py` — conversion metric tests
- `tests/test_cohorts.py` — cohort aggregation tests
- `docs/event-schema.md` — ingestion contract
- `docs/first-touch-attribution.md` — first-touch contract
- `docs/last-touch-attribution.md` — last-touch contract
- `docs/conversion-metrics.md` — conversion pipeline contract
- `docs/basic-cohorts.md` — cohort aggregation contract
