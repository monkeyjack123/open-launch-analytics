# Campaign Efficiency Summary Contract

`summarize_campaign_efficiency` provides campaign-level conversion efficiency rows for dashboard prioritization and budget tuning.

## Function

```python
summarize_campaign_efficiency(
    events,
    start_date=None,
    end_date=None,
    min_visits=1,
)
```

## Behavior

- Reuses normalized funnel grouping by `utm_source` + `utm_campaign`
- Supports optional inclusive date filters (`YYYY-MM-DD`)
- Filters low-volume rows using `min_visits`
- Returns deterministic ordering by:
  1. `activation_per_visit_rate` (desc)
  2. `activations` (desc)
  3. `visits` (desc)
  4. `utm_source` / `utm_campaign` (asc)

## Output row fields

- `utm_source`
- `utm_campaign`
- `visits`
- `signups`
- `activations`
- `signup_rate` (`signups / visits`)
- `activation_per_signup_rate` (`activations / signups`)
- `activation_per_visit_rate` (`activations / visits`)

## Validation

- `min_visits` must be `>= 0` or raises `ValueError`
- Date filters follow the same validation semantics as funnel helpers
