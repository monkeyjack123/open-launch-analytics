# API key auth contract (MVP)

`ingest_event(payload, api_key=..., valid_api_keys=...)` supports minimal ingestion auth for backlog Issue #8.

## Behavior

- If `valid_api_keys` is omitted (`None`), auth is bypassed for local/dev flows.
- If `valid_api_keys` is provided:
  - missing/blank `api_key` returns `401` with `missing_api_key`
  - unknown key returns `403` with `invalid_api_key`
  - valid key proceeds to payload validation + normalization and returns `202` on success

## Key lifecycle helper (owner flows)

`ApiKeyManager` adds an MVP key-management surface for owner-only create/rotate/revoke behavior without exposing plaintext secrets after creation.

- `create_key(name)` returns one-time plaintext `api_key` + metadata (`key_id`, `created_at`)
- `rotate_key(key_id)` issues a fresh plaintext key and invalidates the prior secret
- `revoke_key(key_id)` marks a key inactive
- `list_keys()` returns metadata with redacted `preview` only (never full secret)
- `active_key_hashes()` returns SHA-256 digests for secure runtime validation

Use `validate_api_key_hash(api_key, valid_api_key_hashes)` for ingest auth when keys are stored as digests.

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
