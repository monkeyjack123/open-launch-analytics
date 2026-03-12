# Funnel Breakdown (Issue #6 table backend)

`build_funnel_breakdown(...)` powers the source/campaign table rows for the MVP dashboard.

## Function

```python
build_funnel_breakdown(
    events,
    start_date=None,
    end_date=None,
    utm_source=None,
    utm_campaign=None,
    sort_by="visits",
    descending=True,
    limit=None,
)
```

## Behavior

- groups normalized events by `utm_source` + `utm_campaign`
- counts `visits`, `signups`, `activations`
- computes:
  - `signup_rate = signups / visits` (or `None` when `visits == 0`)
  - `activation_rate = activations / signups` (or `None` when `signups == 0`)
- applies optional date/source/campaign filters
- validates optional `start_date`/`end_date` format (`YYYY-MM-DD`) and raises `ValueError` for invalid ranges
- supports deterministic sorting for UI table interactions
- supports optional `limit` for top-N table views

## Sort fields

Supported `sort_by` values:

- `utm_source`
- `utm_campaign`
- `visits`
- `signups`
- `activations`
- `signup_rate`
- `activation_rate`

Unknown sort fields fall back to `visits`.
