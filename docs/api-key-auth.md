# API key auth contract (MVP)

`ingest_event(payload, api_key=..., valid_api_keys=...)` supports minimal ingestion auth for backlog Issue #8.

## Behavior

- If `valid_api_keys` is omitted (`None`), auth is bypassed for local/dev flows.
- If `valid_api_keys` is provided:
  - missing/blank `api_key` returns `401` with `missing_api_key`
  - unknown key returns `403` with `invalid_api_key`
  - valid key proceeds to payload validation + normalization and returns `202` on success

## Example response envelopes

```json
{
  "ok": false,
  "status": 401,
  "errors": [
    {
      "field": "api_key",
      "error": "missing_api_key",
      "message": "API key is required"
    }
  ],
  "event": null
}
```

```json
{
  "ok": false,
  "status": 403,
  "errors": [
    {
      "field": "api_key",
      "error": "invalid_api_key",
      "message": "API key is invalid"
    }
  ],
  "event": null
}
```
