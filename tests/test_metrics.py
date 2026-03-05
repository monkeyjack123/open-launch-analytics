import unittest

from open_launch_analytics.metrics import (
    aggregate_conversion_metrics,
    backfill_conversion_metrics,
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


if __name__ == "__main__":
    unittest.main()
