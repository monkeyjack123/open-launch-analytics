# Conversion Metrics Aggregation (MVP)

Implements backlog **Issue #5** (conversion metrics aggregation pipeline) with a pure-Python MVP aggregation utility.

## API

### `aggregate_conversion_metrics(events)`

Input: raw events list (same shape as ingest payloads).  
Output: list of metric rows grouped by:

- `date` (UTC date from `timestamp`)
- `utm_source` (normalized)
- `utm_campaign` (normalized)

Each row includes:

- `visits`
- `signups`
- `activations`
- `signup_rate = signups / visits` (or `None` if `visits == 0`)
- `activation_rate = activations / signups` (or `None` if `signups == 0`)

Only `visit`, `signup`, and `activation` events are counted.

### `backfill_conversion_metrics(events, start_date, end_date)`

Recomputes conversion metrics for an inclusive date range (`YYYY-MM-DD`), then delegates to `aggregate_conversion_metrics`.

## Determinism

Rows are sorted by `(date, utm_source, utm_campaign)` for stable output.

## Notes

- Uses the existing event normalization logic to ensure consistent UTM bucketing.
- Events with malformed ISO-8601 timestamps are skipped instead of failing the full aggregation/backfill run.
- Intended for MVP data pipeline and testability before wiring to database/materialized views.
