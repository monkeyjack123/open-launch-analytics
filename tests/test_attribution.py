import unittest

from open_launch_analytics.attribution import (
    build_first_touch_attribution,
    build_last_touch_attribution,
)


class FirstTouchAttributionTests(unittest.TestCase):
    def test_picks_earliest_tagged_event_per_user(self):
        events = [
            {
                "event_id": "evt_2",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
            },
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "X",
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-05T07:00:00Z",
                "user_id": "u2",
            },
        ]

        table = build_first_touch_attribution(events)

        self.assertEqual(table["u1"]["event_id"], "evt_1")
        self.assertEqual(table["u1"]["utm_source"], "x")
        self.assertNotIn("u2", table)

    def test_deterministic_tie_breaker_by_event_id(self):
        events = [
            {
                "event_id": "evt_b",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "google",
            },
            {
                "event_id": "evt_a",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "reddit",
            },
        ]

        table = build_first_touch_attribution(events)
        self.assertEqual(table["u1"]["event_id"], "evt_a")
        self.assertEqual(table["u1"]["utm_source"], "reddit")


class LastTouchAttributionTests(unittest.TestCase):
    def test_picks_latest_tagged_event_per_user(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "X",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T09:30:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u2",
            },
        ]

        table = build_last_touch_attribution(events)

        self.assertEqual(table["u1"]["event_id"], "evt_2")
        self.assertEqual(table["u1"]["utm_source"], "linkedin")
        self.assertNotIn("u2", table)

    def test_deterministic_tie_breaker_prefers_larger_event_id(self):
        events = [
            {
                "event_id": "evt_a",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "google",
            },
            {
                "event_id": "evt_b",
                "event_name": "visit",
                "timestamp": "2026-03-05T08:00:00Z",
                "user_id": "u1",
                "utm_source": "reddit",
            },
        ]

        table = build_last_touch_attribution(events)
        self.assertEqual(table["u1"]["event_id"], "evt_b")
        self.assertEqual(table["u1"]["utm_source"], "reddit")

    def test_attribution_skips_invalid_timestamps(self):
        events = [
            {
                "event_id": "evt_bad",
                "event_name": "visit",
                "timestamp": "invalid",
                "user_id": "u1",
                "utm_source": "reddit",
            },
            {
                "event_id": "evt_good",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
            },
        ]

        first_touch = build_first_touch_attribution(events)
        last_touch = build_last_touch_attribution(events)

        self.assertEqual(first_touch["u1"]["event_id"], "evt_good")
        self.assertEqual(last_touch["u1"]["event_id"], "evt_good")


if __name__ == "__main__":
    unittest.main()
