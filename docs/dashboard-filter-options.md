# Dashboard Filter Options (Issue #6 controls backend)

`build_dashboard_filter_options(...)` provides deterministic dropdown options for source/campaign dashboard controls.

## Function

```python
build_dashboard_filter_options(
    events,
    start_date=None,
    end_date=None,
)
```

## Behavior

- processes normalized conversion events (`visit`, `signup`, `activation`)
- applies optional inclusive date bounds (`start_date`, `end_date`)
- returns event-volume counts for each normalized `utm_source` and `utm_campaign`
- sorts options deterministically by descending `events`, then ascending `value`
- validates optional date bounds and raises `ValueError` for invalid dates/ranges

## Output shape

```json
{
  "utm_source": [
    {"value": "linkedin", "label": "linkedin", "events": 24}
  ],
  "utm_campaign": [
    {"value": "spring-launch", "label": "spring-launch", "events": 19}
  ]
}
```

This contract is intended for direct UI wiring in filter dropdowns or command-bar pickers.
