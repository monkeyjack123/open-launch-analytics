# Basic Signup Cohorts (D0/D1/D7)

`build_signup_cohorts(events, days=(0, 1, 7), utm_source=None, utm_campaign=None)`
produces daily signup cohorts with activation counts/rates at configurable day offsets.

## Input assumptions

- Events follow the normalized event contract (`normalize_event`)
- Signup events: `event_name == "signup"`
- Activation events: `event_name in {"activation", "activated"}`
- Cohort assignment is based on each user's **earliest signup date**

## Output shape

Each returned row includes:

- `cohort_date` (YYYY-MM-DD)
- `signups`
- Per requested offset (default `0,1,7`):
  - `d{n}_activated`
  - `d{n}_rate`

Example keys for defaults:

- `d0_activated`, `d0_rate`
- `d1_activated`, `d1_rate`
- `d7_activated`, `d7_rate`

## Filtering

Optional `utm_source` and `utm_campaign` filters are applied after normalization:

- leading/trailing whitespace ignored
- case-insensitive matching

This lets dashboard queries segment cohorts by acquisition source/campaign without reworking the source event stream.
