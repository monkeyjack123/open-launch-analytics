# Funnel Timeseries Contract

`build_funnel_timeseries(events, start_date=None, end_date=None, utm_source=None, utm_campaign=None)`
returns per-day funnel rows for dashboard chart rendering.

## Behavior

- considers normalized conversion events only: `visit`, `signup`, `activation`
- applies optional date/source/campaign filters using the same normalization semantics as other dashboard helpers
- returns rows sorted by ascending `date`
- when both `start_date` and `end_date` are provided, the function fills missing days with zero-count rows

## Row shape

```json
{
  "date": "2026-03-05",
  "visits": 10,
  "signups": 3,
  "activations": 1,
  "signup_rate": 0.3,
  "activation_rate": 0.3333333333
}
```

Rate semantics:

- `signup_rate = signups / visits` (or `null` when visits is zero)
- `activation_rate = activations / signups` (or `null` when signups is zero)
