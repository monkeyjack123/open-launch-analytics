from datetime import datetime, timezone
import json
import unittest

from open_launch_analytics.sample_data import build_sample_events, sample_events_to_ndjson


class SampleDataTests(unittest.TestCase):
    def test_build_sample_events_generates_funnel_per_user(self) -> None:
        start = datetime(2026, 3, 6, 7, 0, 0, tzinfo=timezone.utc)
        events = build_sample_events(users=2, start_at=start)

        self.assertEqual(len(events), 6)
        self.assertEqual(events[0]["event_id"], "sample-1-visit")
        self.assertEqual(events[-1]["event_id"], "sample-2-activation")
        self.assertEqual(events[0]["timestamp"], "2026-03-06T07:10:00Z")

    def test_build_sample_events_with_non_positive_users_returns_empty(self) -> None:
        self.assertEqual(build_sample_events(users=0), [])
        self.assertEqual(build_sample_events(users=-2), [])

    def test_sample_events_to_ndjson_serialization(self) -> None:
        events = [
            {
                "event_id": "sample-1-visit",
                "user_id": "user-1",
                "event_name": "visit",
                "timestamp": "2026-03-06T07:10:00Z",
                "utm_source": "twitter",
                "utm_medium": "social",
                "utm_campaign": "spring-launch",
            }
        ]

        ndjson = sample_events_to_ndjson(events)
        parsed = json.loads(ndjson)
        self.assertEqual(parsed["event_name"], "visit")
        self.assertEqual(parsed["utm_campaign"], "spring-launch")


if __name__ == "__main__":
    unittest.main()
