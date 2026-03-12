# Source engagement summary

`summarize_source_engagement(events, start_date=None, end_date=None)`

## Purpose

Provide a lightweight engagement-quality view by UTM source using conversion events.

For each source bucket, the helper tracks unique visitors (`user_id`) and flags visitors as *engaged* when they complete either `signup` or `activation`.

## Output

Returns a list of rows:

- `utm_source` — normalized source value
- `visitors` — unique visitor count with at least one conversion-funnel event
- `engaged_visitors` — unique visitors with at least one `signup`/`activation`
- `engagement_rate` — `engaged_visitors / visitors`
- `bounce_rate` — `1 - engagement_rate`

Rows are sorted by `visitors` descending, then `utm_source` ascending.

## Filters

Optional inclusive date filters:

- `start_date` (`YYYY-MM-DD`)
- `end_date` (`YYYY-MM-DD`)

Date validation follows the same semantics as other dashboard metric helpers and raises `ValueError` for invalid formats/ranges.

## Notes

- Events with missing/blank `user_id` are ignored because unique visitor identity is required.
- Sources with no visitors are not emitted.
