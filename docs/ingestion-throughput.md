# Ingestion Batch + Throughput Contract

This doc defines helper utilities for MVP ingestion load sanity checks.

## `ingest_batch(payloads, *, api_key=None, valid_api_keys=None)`

Ingests a list of event payloads by applying `ingest_event` to each item.

### Response envelope

```json
{
  "ok": false,
  "status": 207,
  "total": 2,
  "accepted": 1,
  "rejected": 1,
  "results": ["... per-item ingest_event envelopes ..."]
}
```

Rules:

- `status = 202` when all payloads are accepted
- `status = 207` (multi-status style) when one or more payloads are rejected
- Per-item `results` preserves `ingest_event` response shape (`ok/status/errors/event`)

## `measure_ingest_throughput(payloads, *, repeats=1, api_key=None, valid_api_keys=None)`

Runs repeated `ingest_batch` loops and returns lightweight benchmark stats.

### Response envelope

```json
{
  "processed_events": 2000,
  "elapsed_seconds": 0.42,
  "events_per_second": 4761.9,
  "last_batch": {
    "ok": true,
    "status": 202,
    "total": 100,
    "accepted": 100,
    "rejected": 0,
    "results": []
  }
}
```

Notes:

- This is a developer utility for MVP load sanity checks, not a production-grade load test.
- `repeats` must be `>= 1` or a `ValueError` is raised.
- Include realistic sample payload mixes for better signal.
