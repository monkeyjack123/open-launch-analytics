from __future__ import annotations

import unittest

from open_launch_analytics.quality import build_data_quality_report, build_health_status


class QualityTests(unittest.TestCase):
    def test_build_data_quality_report_tracks_invalid_and_missing_utm_rates(self) -> None:
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "Google",
                "utm_medium": "CPC",
                "utm_campaign": "Launch",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u2",
                # missing UTM -> defaults to direct/unknown
            },
            {
                "event_id": "evt_3",
                "event_name": "activation",
                # invalid: missing timestamp
                "user_id": "u3",
            },
        ]

        report = build_data_quality_report(events)

        self.assertEqual(
            report,
            {
                "total_events": 3,
                "invalid_events": 1,
                "invalid_payload_rate": 1 / 3,
                "missing_utm_events": 1,
                "missing_utm_rate": 1 / 3,
            },
        )

    def test_build_health_status_flags_degraded_when_invalid_payload_rate_too_high(self) -> None:
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "user_id": "u2",  # invalid: missing timestamp
            },
        ]

        health = build_health_status(events, max_invalid_payload_rate=0.2)

        self.assertFalse(health["ok"])
        self.assertEqual(health["status"], "degraded")
        self.assertEqual(health["quality"]["invalid_payload_rate"], 0.5)
        self.assertEqual(health["thresholds"]["max_invalid_payload_rate"], 0.2)

    def test_build_health_status_is_healthy_for_empty_dataset(self) -> None:
        health = build_health_status([])

        self.assertTrue(health["ok"])
        self.assertEqual(health["status"], "healthy")
        self.assertEqual(
            health["quality"],
            {
                "total_events": 0,
                "invalid_events": 0,
                "invalid_payload_rate": 0.0,
                "missing_utm_events": 0,
                "missing_utm_rate": 0.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
