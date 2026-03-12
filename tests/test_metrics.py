import unittest

from datetime import date

from open_launch_analytics.metrics import (
    aggregate_conversion_metrics,
    backfill_conversion_metrics,
    build_dashboard_filter_options,
    build_funnel_breakdown,
    resolve_date_range,
    summarize_funnel,
    summarize_source_engagement,
)


class ConversionMetricsTests(unittest.TestCase):
    def test_aggregate_conversion_metrics_groups_and_computes_rates(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_3",
                "event_name": "activation",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_4",
                "event_name": "visit",
                "timestamp": "2026-03-05T11:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_5",
                "event_name": "purchase",
                "timestamp": "2026-03-05T12:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "spring",
            },
        ]

        rows = aggregate_conversion_metrics(events)

        linkedin_row = rows[0]
        self.assertEqual(linkedin_row["utm_source"], "linkedin")
        self.assertEqual(linkedin_row["utm_campaign"], "spring")
        self.assertEqual(linkedin_row["visits"], 1)
        self.assertEqual(linkedin_row["signups"], 1)
        self.assertEqual(linkedin_row["activations"], 1)
        self.assertEqual(linkedin_row["signup_rate"], 1.0)
        self.assertEqual(linkedin_row["activation_rate"], 1.0)

        reddit_row = rows[1]
        self.assertEqual(reddit_row["utm_source"], "reddit")
        self.assertEqual(reddit_row["signups"], 0)
        self.assertEqual(reddit_row["signup_rate"], 0.0)
        self.assertIsNone(reddit_row["activation_rate"])

    def test_backfill_conversion_metrics_filters_by_date_range(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-01T08:00:00Z",
                "user_id": "u1",
                "utm_source": "x",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "x",
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-06T08:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
            },
        ]

        rows = backfill_conversion_metrics(events, "2026-03-05", "2026-03-05")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2026-03-05")
        self.assertEqual(rows[0]["signups"], 1)

    def test_aggregate_and_backfill_skip_invalid_timestamps(self):
        events = [
            {
                "event_id": "evt_bad",
                "event_name": "visit",
                "timestamp": "not-a-timestamp",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_good",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u2",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
        ]

        rows = aggregate_conversion_metrics(events)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["visits"], 1)

        backfill_rows = backfill_conversion_metrics(events, "2026-03-05", "2026-03-05")
        self.assertEqual(len(backfill_rows), 1)
        self.assertEqual(backfill_rows[0]["visits"], 1)

    def test_backfill_conversion_metrics_validates_date_inputs(self):
        events = []

        with self.assertRaises(ValueError):
            backfill_conversion_metrics(events, "2026/03/05", "2026-03-06")

        with self.assertRaises(ValueError):
            backfill_conversion_metrics(events, "2026-03-07", "2026-03-06")

    def test_summarize_funnel_supports_date_and_utm_filters(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
                "utm_campaign": "Spring Launch",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring launch",
            },
            {
                "event_id": "evt_3",
                "event_name": "activation",
                "timestamp": "2026-03-06T10:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring launch",
            },
            {
                "event_id": "evt_4",
                "event_name": "visit",
                "timestamp": "2026-03-05T11:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "spring launch",
            },
        ]

        summary = summarize_funnel(
            events,
            start_date="2026-03-05",
            end_date="2026-03-05",
            utm_source=" linkedin ",
            utm_campaign="SPRING LAUNCH",
        )

        self.assertEqual(summary["visits"], 1)
        self.assertEqual(summary["signups"], 1)
        self.assertEqual(summary["activations"], 0)
        self.assertEqual(summary["signup_rate"], 1.0)
        self.assertEqual(summary["activation_rate"], 0.0)

    def test_summarize_funnel_returns_none_rates_when_denominators_missing(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "signup",
                "timestamp": "2026-03-07T08:00:00Z",
                "user_id": "u1",
            }
        ]

        summary = summarize_funnel(events)
        self.assertEqual(summary["visits"], 0)
        self.assertEqual(summary["signups"], 1)
        self.assertEqual(summary["activations"], 0)
        self.assertIsNone(summary["signup_rate"])
        self.assertEqual(summary["activation_rate"], 0.0)

    def test_build_funnel_breakdown_supports_filters_sort_and_limit(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
                "utm_campaign": "Spring",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_4",
                "event_name": "visit",
                "timestamp": "2026-03-06T08:00:00Z",
                "user_id": "u3",
                "utm_source": "reddit",
                "utm_campaign": "retargeting",
            },
        ]

        rows = build_funnel_breakdown(
            events,
            start_date="2026-03-05",
            end_date="2026-03-05",
            sort_by="signups",
            descending=True,
            limit=1,
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["utm_source"], "linkedin")
        self.assertEqual(rows[0]["utm_campaign"], "spring")
        self.assertEqual(rows[0]["visits"], 1)
        self.assertEqual(rows[0]["signups"], 1)
        self.assertEqual(rows[0]["activation_rate"], 0.0)

    def test_build_funnel_breakdown_falls_back_to_default_sort_field(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "a",
                "utm_campaign": "x",
            },
            {
                "event_id": "evt_2",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u2",
                "utm_source": "a",
                "utm_campaign": "x",
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u3",
                "utm_source": "b",
                "utm_campaign": "y",
            },
        ]

        rows = build_funnel_breakdown(events, sort_by="not_a_field")
        self.assertEqual(rows[0]["utm_source"], "a")
        self.assertEqual(rows[0]["visits"], 2)

    def test_build_dashboard_filter_options_counts_and_sorts(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
                "utm_campaign": "Spring",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T08:30:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "Retargeting",
            },
            {
                "event_id": "evt_4",
                "event_name": "activation",
                "timestamp": "2026-03-06T09:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "retargeting",
            },
        ]

        options = build_dashboard_filter_options(
            events,
            start_date="2026-03-05",
            end_date="2026-03-05",
        )

        self.assertEqual(options["utm_source"][0], {"value": "linkedin", "label": "linkedin", "events": 2})
        self.assertEqual(options["utm_source"][1], {"value": "reddit", "label": "reddit", "events": 1})
        self.assertEqual(options["utm_campaign"][0], {"value": "spring", "label": "spring", "events": 2})
        self.assertEqual(options["utm_campaign"][1], {"value": "retargeting", "label": "retargeting", "events": 1})

    def test_build_dashboard_filter_options_validates_dates(self):
        with self.assertRaises(ValueError):
            build_dashboard_filter_options([], start_date="2026/03/05", end_date="2026-03-06")

    def test_funnel_helpers_validate_optional_date_filters(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            }
        ]

        with self.assertRaises(ValueError):
            summarize_funnel(events, start_date="2026/03/05")

        with self.assertRaises(ValueError):
            build_funnel_breakdown(events, end_date="03-05-2026")

        with self.assertRaises(ValueError):
            summarize_funnel(events, start_date="2026-03-06", end_date="2026-03-05")

    def test_resolve_date_range_supports_7d_and_30d(self):
        start_7d, end_7d = resolve_date_range("7d", today=date(2026, 3, 9))
        self.assertEqual(start_7d, "2026-03-03")
        self.assertEqual(end_7d, "2026-03-09")

        start_30d, end_30d = resolve_date_range("30d", today=date(2026, 3, 9))
        self.assertEqual(start_30d, "2026-02-08")
        self.assertEqual(end_30d, "2026-03-09")

    def test_resolve_date_range_validates_custom_and_errors(self):
        start_custom, end_custom = resolve_date_range(
            "custom",
            start_date="2026-03-01",
            end_date="2026-03-09",
        )
        self.assertEqual(start_custom, "2026-03-01")
        self.assertEqual(end_custom, "2026-03-09")

        with self.assertRaises(ValueError):
            resolve_date_range("custom", start_date="2026-03-10", end_date="2026-03-09")

        with self.assertRaises(ValueError):
            resolve_date_range("90d")


    def test_summarize_source_engagement_groups_unique_visitors(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
            },
            {
                "event_id": "evt_2",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:10:00Z",
                "user_id": "u2",
                "utm_source": "linkedin",
            },
            {
                "event_id": "evt_3",
                "event_name": "signup",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
            },
            {
                "event_id": "evt_4",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:30:00Z",
                "user_id": "u3",
                "utm_source": "reddit",
            },
            {
                "event_id": "evt_5",
                "event_name": "activation",
                "timestamp": "2026-03-06T09:30:00Z",
                "user_id": "u3",
                "utm_source": "reddit",
            },
        ]

        rows = summarize_source_engagement(events, start_date="2026-03-05", end_date="2026-03-05")

        self.assertEqual(len(rows), 2)

        linkedin = next(row for row in rows if row["utm_source"] == "linkedin")
        self.assertEqual(linkedin["visitors"], 2)
        self.assertEqual(linkedin["engaged_visitors"], 1)
        self.assertEqual(linkedin["engagement_rate"], 0.5)
        self.assertEqual(linkedin["bounce_rate"], 0.5)

        reddit = next(row for row in rows if row["utm_source"] == "reddit")
        self.assertEqual(reddit["visitors"], 1)
        self.assertEqual(reddit["engaged_visitors"], 0)
        self.assertEqual(reddit["engagement_rate"], 0.0)
        self.assertEqual(reddit["bounce_rate"], 1.0)

    def test_summarize_source_engagement_skips_missing_user_id(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "utm_source": "linkedin",
            }
        ]

        rows = summarize_source_engagement(events)
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
