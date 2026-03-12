# Data Quality + Health (MVP)

Issue #9 adds minimal observability helpers so API/dashboard surfaces can expose payload quality quickly.

## APIs

### `build_data_quality_report(events)`

Returns aggregate quality metrics:

- `total_events`
- `invalid_events`
- `invalid_payload_rate` = invalid / total
- `missing_utm_events` (valid payloads that normalize to `direct` or `unknown` for source/medium/campaign)
- `missing_utm_rate` = missing_utm_events / total

### `build_attribution_completeness_report(events, conversion_events=None)`

Returns conversion attribution coverage metrics (Issue #9 KPI monitoring):

- `conversion_events` (normalized event names being tracked; default: `signup`, `activation`)
- `conversions` (valid conversion events counted)
- `attributed_conversions` (conversion events with non-fallback UTM values)
- `unattributed_conversions` (conversion events that still normalize to `direct/unknown`)
- `attribution_match_rate` = attributed / conversions (or `None` if no conversions)

### `build_ingestion_slo_report(samples, max_error_rate=0.005, max_p95_latency_ms=500.0)`

Returns ingestion reliability + latency SLO posture from request-level samples:

- `samples` total telemetry rows processed
- `errors` and `error_rate` (`ok=False` rows)
- `invalid_samples` (rows with missing/non-numeric/negative latency)
- `latency.p95_ms` (nearest-rank p95 from valid latency samples)
- `thresholds.max_error_rate` and `thresholds.max_p95_latency_ms`
- top-level `ok/status` (`healthy` or `degraded`)

### `build_health_status(events, max_invalid_payload_rate=0.01)`

Returns an envelope suitable for `/health` style endpoints:

- `ok` (boolean)
- `status` (`healthy` or `degraded`)
- `thresholds.max_invalid_payload_rate`
- `quality` (embedded `build_data_quality_report` output)

## Example

```python
from open_launch_analytics.quality import build_health_status

health = build_health_status(events, max_invalid_payload_rate=0.02)
# {'ok': True/False, 'status': 'healthy'/'degraded', ...}
```

## Notes

- Invalid payloads are measured using the existing `validate_event` contract.
- Missing-UTM metrics intentionally track valid events that still normalize to fallback buckets, so teams can monitor attribution completeness.
- `build_attribution_completeness_report(...)` narrows that signal to conversion events so teams can track the MVP KPI "attribution match rate" directly.
- `build_ingestion_slo_report(...)` adds p95 latency + error-rate SLO visibility expected by Issue #9, while surfacing malformed telemetry rows via `invalid_samples`.
