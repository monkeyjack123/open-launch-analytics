# Sample Events Quickstart Contract

This module provides deterministic sample launch-funnel events for local MVP validation.

## API

### `build_sample_events(users=3, start_at=None)`

- Returns a list of event payload dictionaries
- Generates a 3-step funnel per user: `visit`, `signup`, `activation`
- Uses `start_at` as a deterministic base timestamp when provided
- Returns `[]` when `users <= 0`

### `sample_events_to_ndjson(events)`

- Returns line-delimited JSON (`NDJSON`) from a list of event dictionaries
- Output can be piped into ingestion scripts or HTTP clients

## Example

```bash
PYTHONPATH=src python3 - <<'PY'
from open_launch_analytics.sample_data import build_sample_events, sample_events_to_ndjson

events = build_sample_events(users=2)
print(sample_events_to_ndjson(events))
PY
```

Example output (truncated):

```json
{"event_id":"sample-1-visit","user_id":"user-1","event_name":"visit",...}
{"event_id":"sample-1-signup","user_id":"user-1","event_name":"signup",...}
```
