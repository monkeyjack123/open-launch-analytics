# Basic Signup Cohorts (D0/D1/D7)

`build_signup_cohorts(events, days=(0, 1, 7), utm_source=None, utm_campaign=None)`
produces daily signup cohorts with activation counts/rates at configurable day offsets.

`build_cohort_matrix(events, days=(0, 1, 7), utm_source=None, utm_campaign=None)`
wraps the cohort rows in a dashboard-ready envelope with column metadata, day legends,
and weighted totals for a footer row.

## Input assumptions

- Events follow the normalized event contract (`normalize_event`)
- Signup events: `event_name == "signup"`
- Activation events: `event_name in {"activation", "activated"}`
- Cohort assignment is based on each user's **earliest signup date**

## Day offsets

- `days` accepts non-negative integer offsets only
- duplicates are de-duplicated and sorted (e.g. `(1, 0, 1)` becomes `(0, 1)`)
- invalid inputs (e.g. empty or only negative offsets) raise `ValueError`

## Output shape

Each `build_signup_cohorts` row includes:

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

## Cohort matrix envelope (for UI rendering)

`build_cohort_matrix(...)` returns:

- `columns`: ordered list of table columns for cohort/date + each Dn count/rate pair
- `legend`: human-readable Dn definitions (e.g., D0 = same-day activation)
- `rows`: raw cohort rows from `build_signup_cohorts`
- `totals`: weighted footer row (`TOTAL`) across all cohorts

This keeps frontend rendering logic thin and ensures matrix/table semantics stay aligned with backend cohort math.
