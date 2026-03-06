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
