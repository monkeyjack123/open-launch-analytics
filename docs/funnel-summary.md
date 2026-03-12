# Funnel Summary Contract

`open_launch_analytics.metrics.summarize_funnel(...)` provides dashboard-ready top-card totals and rates from raw events.

## Function

```python
summarize_funnel(
    events,
    start_date=None,
    end_date=None,
    utm_source=None,
    utm_campaign=None,
)
```

## Inputs

- `events`: list of raw event payloads
- `start_date`: optional inclusive lower bound (`YYYY-MM-DD`)
- `end_date`: optional inclusive upper bound (`YYYY-MM-DD`)
  - when provided, both fields are validated strictly as `YYYY-MM-DD`
  - if both are set, `start_date` must be `<= end_date`
- `utm_source`: optional source filter (normalized to lowercase/trimmed)
- `utm_campaign`: optional campaign filter (normalized to lowercase/trimmed)

## Behavior

- Uses existing normalization rules (`normalize_event`) for UTM handling.
- Counts only conversion events: `visit`, `signup`, `activation`.
- Ignores events with invalid/missing timestamps.
- Applies date and UTM filters before counting.

## Output

```json
{
  "visits": 120,
  "signups": 34,
  "activations": 12,
  "signup_rate": 0.2833,
  "activation_rate": 0.3529
}
```

Rates follow existing metric semantics:

- `signup_rate = signups / visits` (or `null` when visits is 0)
- `activation_rate = activations / signups` (or `null` when signups is 0)

## Example

```python
from open_launch_analytics.metrics import summarize_funnel

summary = summarize_funnel(
    events,
    start_date="2026-03-01",
    end_date="2026-03-07",
    utm_source="linkedin",
)
```
