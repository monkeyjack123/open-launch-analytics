from __future__ import annotations

import unittest

from open_launch_analytics.quality import (
    build_attribution_completeness_report,
    build_daily_quality_trend,
    build_data_quality_report,
    build_health_status,
    build_ingestion_slo_report,
)


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

    def test_build_attribution_completeness_report_tracks_conversion_match_rate(self) -> None:
        events = [
            {
                "event_id": "evt_1",
                "event_name": "signup",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "launch",
            },
            {
                "event_id": "evt_2",
                "event_name": "activation",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u1",
                # missing UTM => unattributed conversion
            },
            {
                "event_id": "evt_3",
                "event_name": "visit",
                "timestamp": "2026-03-05T11:00:00Z",
                "user_id": "u1",
            },
            {
                "event_id": "evt_4",
                "event_name": "signup",
                "user_id": "u2",  # invalid, should be ignored
            },
        ]

        report = build_attribution_completeness_report(events)

        self.assertEqual(report["conversion_events"], ["activation", "signup"])
        self.assertEqual(report["conversions"], 2)
        self.assertEqual(report["attributed_conversions"], 1)
        self.assertEqual(report["unattributed_conversions"], 1)
        self.assertEqual(report["attribution_match_rate"], 0.5)

    def test_build_attribution_completeness_report_supports_custom_conversion_events(self) -> None:
        events = [
            {
                "event_id": "evt_1",
                "event_name": "purchase",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "x",
                "utm_medium": "email",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_2",
                "event_name": "purchase",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u2",
            },
        ]

        report = build_attribution_completeness_report(events, conversion_events=[" purchase "])

        self.assertEqual(report["conversion_events"], ["purchase"])
        self.assertEqual(report["conversions"], 2)
        self.assertEqual(report["attributed_conversions"], 1)
        self.assertEqual(report["unattributed_conversions"], 1)
        self.assertEqual(report["attribution_match_rate"], 0.5)

    def test_build_attribution_completeness_report_validates_empty_conversion_events(self) -> None:
        with self.assertRaisesRegex(ValueError, "conversion_events must contain at least one non-empty event name"):
            build_attribution_completeness_report([], conversion_events=["   "])

    def test_build_ingestion_slo_report_tracks_error_rate_and_p95_latency(self) -> None:
        samples = [
            {"ok": True, "latency_ms": 120},
            {"ok": True, "latency_ms": 180},
            {"ok": False, "latency_ms": 220},
            {"ok": True, "latency_ms": 240},
            {"ok": True, "latency_ms": 900},
        ]

        report = build_ingestion_slo_report(
            samples,
            max_error_rate=0.25,
            max_p95_latency_ms=800,
        )

        self.assertFalse(report["ok"])
        self.assertEqual(report["status"], "degraded")
        self.assertEqual(report["samples"], 5)
        self.assertEqual(report["errors"], 1)
        self.assertEqual(report["error_rate"], 0.2)
        self.assertEqual(report["latency"]["p95_ms"], 900.0)

    def test_build_ingestion_slo_report_handles_empty_and_invalid_samples(self) -> None:
        empty_report = build_ingestion_slo_report([])
        self.assertTrue(empty_report["ok"])
        self.assertIsNone(empty_report["error_rate"])
        self.assertIsNone(empty_report["latency"]["p95_ms"])

        report = build_ingestion_slo_report(
            [
                {"ok": True, "latency_ms": 100},
                {"ok": False, "latency_ms": -1},  # invalid latency
                {"ok": False},  # missing latency
            ],
            max_error_rate=0.9,
            max_p95_latency_ms=200,
        )

        self.assertEqual(report["invalid_samples"], 2)
        self.assertEqual(report["latency"]["p95_ms"], 100.0)

    def test_build_daily_quality_trend_groups_rates_by_day(self) -> None:
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "launch",
            },
            {
                "event_id": "evt_2",
                "event_name": "signup",
                "timestamp": "2026-03-05T10:00:00Z",
                "user_id": "u2",
            },
            {
                "event_id": "evt_3",
                "event_name": "activation",
                "timestamp": "2026-03-05T11:00:00Z",
                "user_id": "u3",
                "utm_source": "email",
                "utm_medium": "newsletter",
                "utm_campaign": "march",
            },
            {
                "event_id": "evt_4",
                "event_name": "visit",
                "timestamp": "2026-03-06T09:00:00Z",
                "user_id": "u4",
            },
            {
                "event_id": "evt_5",
                "event_name": "signup",
                "user_id": "u5",  # invalid and unassigned (no timestamp)
            },
        ]

        report = build_daily_quality_trend(events)

        self.assertEqual(report["unassigned_invalid_events"], 1)
        self.assertEqual(
            report["rows"],
            [
                {
                    "date": "2026-03-05",
                    "events": 3,
                    "invalid_events": 0,
                    "invalid_payload_rate": 0.0,
                    "missing_utm_events": 1,
                    "missing_utm_rate": 1 / 3,
                },
                {
                    "date": "2026-03-06",
                    "events": 1,
                    "invalid_events": 0,
                    "invalid_payload_rate": 0.0,
                    "missing_utm_events": 1,
                    "missing_utm_rate": 1.0,
                },
            ],
        )

    def test_build_daily_quality_trend_supports_day_limit_and_validation(self) -> None:
        events = [
            {
                "event_id": "evt_1",
                "event_name": "visit",
                "timestamp": "2026-03-05T09:00:00Z",
                "user_id": "u1",
            },
            {
                "event_id": "evt_2",
                "event_name": "visit",
                "timestamp": "2026-03-06T09:00:00Z",
                "user_id": "u2",
            },
        ]

        report = build_daily_quality_trend(events, days=1)
        self.assertEqual(len(report["rows"]), 1)
        self.assertEqual(report["rows"][0]["date"], "2026-03-06")

        with self.assertRaisesRegex(ValueError, "days must be positive when provided"):
            build_daily_quality_trend(events, days=0)


if __name__ == "__main__":
    unittest.main()
