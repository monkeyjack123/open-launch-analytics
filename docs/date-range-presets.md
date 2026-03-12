# Dashboard Date Presets (`resolve_date_range`)

`resolve_date_range(preset, *, today=None, start_date=None, end_date=None)` resolves inclusive date bounds for dashboard filter controls.

## Supported presets

- `7d` — returns last 7 days ending on `today`
- `30d` — returns last 30 days ending on `today`
- `custom` — requires explicit `start_date` and `end_date` in `YYYY-MM-DD`

## Return shape

A tuple of `(start_date, end_date)` as ISO date strings.

## Behavior details

- For `7d` / `30d`, both endpoints are inclusive.
  - Example with `today=2026-03-09`:
    - `7d` => `("2026-03-03", "2026-03-09")`
    - `30d` => `("2026-02-08", "2026-03-09")`
- For `custom`, dates must:
  - both be provided
  - both match strict `YYYY-MM-DD`
  - satisfy `start_date <= end_date`

## Errors

Raises `ValueError` when:

- preset is unsupported
- custom dates are missing
- custom dates are malformed
- custom start is after custom end
