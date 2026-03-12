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

Added cohort matrix envelope helper for backlog **Issue #7** UI wiring:

- `build_cohort_matrix(...)` returns dashboard-ready `columns`, `legend`, `rows`, and weighted `totals`
- validates/normalizes day offsets for deterministic matrix rendering
- tests for matrix metadata and totals/footer math
- cohort contract docs updated with matrix semantics and day-offset constraints

Added minimal API key auth guardrails for backlog **Issue #8**:

- `validate_api_key(api_key, valid_api_keys)` validates missing/invalid/valid keys with API-ready error envelopes
- `ingest_event(..., api_key=..., valid_api_keys=...)` now enforces auth when key allowlist is provided
- auth failure semantics aligned to `401` (missing key) and `403` (invalid key)
- unit tests for auth helper + ingest auth flows
- auth contract docs in `docs/api-key-auth.md`

Extended API key management for backlog **Issue #8** owner lifecycle flows:

- added `ApiKeyManager` for `create_key`, `rotate_key`, `revoke_key`, and metadata-only `list_keys`
- key validation now supports digest-based checks via `validate_api_key_hash(...)` to avoid plaintext key storage
- added tests confirming rotate invalidates prior keys, revoke blocks access, and list APIs do not leak secrets
- auth docs updated with key lifecycle contract details

Added MVP data-quality + health reporting helpers for backlog **Issue #9**:

- `build_data_quality_report(events)` computes invalid payload and missing-UTM rates
- `build_health_status(events, max_invalid_payload_rate=...)` returns healthy/degraded envelope for `/health`-style APIs
- tests for healthy/degraded thresholds and empty dataset behavior
- observability contract docs in `docs/data-quality-health.md`

Added ingestion batch + throughput utilities for backlog **Issue #2** throughput validation:

- `ingest_batch(payloads, ...)` returns per-event envelopes with aggregate accepted/rejected counts
- `measure_ingest_throughput(payloads, repeats=...)` provides a lightweight events/second benchmark for MVP load sanity checks
- tests for mixed batch status and throughput reporting
- ingestion batch + throughput contract docs in `docs/ingestion-throughput.md`

Added sample event generator docs + helper utilities for backlog **Issue #10**:

- `build_sample_events(users=..., start_at=...)` creates deterministic demo funnel events
- `sample_events_to_ndjson(events)` emits line-delimited JSON for curl/httpie ingestion trials
- tests for deterministic event generation and NDJSON serialization
- quickstart usage contract docs in `docs/sample-events.md`

Added dashboard top-card funnel summary utility for backlog **Issue #6**:

- `summarize_funnel(events, start_date=None, end_date=None, utm_source=None, utm_campaign=None)` computes filter-aware totals for `visits/signups/activations`
- computes dashboard card rates (`signup_rate`, `activation_rate`) from filtered events
- supports date range and normalized UTM source/campaign filters
- validates optional date filters and raises clear `ValueError` messages for invalid date format/ranges
- tests for filtered and edge-case rate behavior
- API contract docs in `docs/funnel-summary.md`

Added dashboard breakdown table backend utility for backlog **Issue #6**:

- `build_funnel_breakdown(...)` returns source/campaign grouped rows for table rendering
- supports date/source/campaign filters and deterministic sorting (`visits/signups/activations/rates/source/campaign`)
- validates optional date filter format/range for safer dashboard query handling
- supports optional `limit` for top-N table interactions
- tests for filter/sort/limit behavior and invalid sort fallback
- API contract docs in `docs/funnel-breakdown.md`

Added dashboard date-preset resolver utility for backlog **Issue #6** filter UX:

- `resolve_date_range(preset, ...)` resolves inclusive date bounds for `7d`, `30d`, and validated `custom` ranges
- deterministic behavior with injectable `today` for testability
- explicit validation for unsupported presets and invalid custom windows
- tests for 7d/30d range math and custom/error paths
- API contract docs in `docs/date-range-presets.md`

Added conversion attribution completeness monitor helper for backlog **Issue #9** KPI visibility:

- `build_attribution_completeness_report(events, conversion_events=None)` measures conversion attribution coverage using normalized UTM fallback detection
- reports `conversions`, `attributed_conversions`, `unattributed_conversions`, and `attribution_match_rate`
- defaults to conversion events `signup` + `activation`, with optional custom conversion event sets
- tests for default behavior, custom conversion events, and validation errors
- docs expanded in `docs/data-quality-health.md`

Added ingestion SLO monitor helper for backlog **Issue #9** observability completeness:

- `build_ingestion_slo_report(samples, max_error_rate=..., max_p95_latency_ms=...)` evaluates request-level error-rate + p95 latency against configurable thresholds
- report includes `samples`, `errors`, `error_rate`, `latency.p95_ms`, and `invalid_samples` for malformed telemetry visibility
- tests cover degraded latency posture, empty sample behavior, and invalid-latency handling
- docs expanded in `docs/data-quality-health.md`

Added source engagement summary helper for funnel quality monitoring:

- `summarize_source_engagement(events, start_date=None, end_date=None)` computes per-source unique visitors, engaged visitors, engagement rate, and bounce rate
- treats `signup` and `activation` as engaged outcomes, with unique-user counting by `user_id`
- validates optional date filters and ignores events without usable `user_id`
- tests cover unique-user grouping and missing-identity edge cases
- API contract docs in `docs/source-engagement.md`

## Quickstart

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v

# generate demo NDJSON payload
PYTHONPATH=src python3 -c "from open_launch_analytics.sample_data import build_sample_events, sample_events_to_ndjson; print(sample_events_to_ndjson(build_sample_events(users=2)))"
```

## Repo layout

- `src/open_launch_analytics/events.py` — validation + normalization logic
- `src/open_launch_analytics/auth.py` — API key validation helper
- `src/open_launch_analytics/attribution.py` — first/last-touch attribution logic
- `src/open_launch_analytics/metrics.py` — conversion metric aggregation, funnel summaries/breakdowns, source engagement summaries, date-preset resolution, and backfill helpers
- `src/open_launch_analytics/cohorts.py` — signup cohort aggregation (D0/D1/D7)
- `src/open_launch_analytics/quality.py` — data-quality, attribution-completeness, and health summaries
- `src/open_launch_analytics/ingest.py` — single-event ingest envelope + batch/throughput helpers
- `src/open_launch_analytics/sample_data.py` — deterministic sample event generation helpers
- `tests/test_events.py` — event contract tests
- `tests/test_auth.py` — API key auth tests
- `tests/test_attribution.py` — attribution tests
- `tests/test_metrics.py` — conversion metric tests
- `tests/test_cohorts.py` — cohort aggregation tests
- `tests/test_quality.py` — quality/health tests
- `tests/test_ingest.py` — ingest envelope + batch/throughput tests
- `tests/test_sample_data.py` — sample data helper tests
- `docs/event-schema.md` — ingestion contract
- `docs/api-key-auth.md` — API key auth contract
- `docs/first-touch-attribution.md` — first-touch contract
- `docs/last-touch-attribution.md` — last-touch contract
- `docs/conversion-metrics.md` — conversion pipeline contract
- `docs/funnel-summary.md` — dashboard funnel card summary contract
- `docs/funnel-breakdown.md` — dashboard source/campaign breakdown table contract
- `docs/date-range-presets.md` — dashboard 7d/30d/custom date-range resolver contract
- `docs/basic-cohorts.md` — cohort aggregation contract
- `docs/data-quality-health.md` — data quality + health contract
- `docs/ingestion-throughput.md` — batch ingest and throughput-check contract
- `docs/sample-events.md` — sample event generation and NDJSON usage
- `docs/source-engagement.md` — source-level engagement and bounce-rate summary contract
