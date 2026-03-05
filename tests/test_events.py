import unittest

from open_launch_analytics.events import normalize_event, validate_event


class EventValidationTests(unittest.TestCase):
    def test_validate_event_accepts_valid_payload(self):
        payload = {
            "event_id": "evt_1",
            "event_name": "signup",
            "timestamp": "2026-03-05T09:00:00Z",
            "user_id": "user_1",
            "utm_source": "Twitter",
        }
        self.assertEqual(validate_event(payload), [])

    def test_validate_event_reports_missing_and_format_errors(self):
        payload = {
            "event_id": "",
            "timestamp": "03/05/2026",
            "user_id": "user_2",
            "utm_source": 123,
        }
        errors = validate_event(payload)
        error_fields = {e["field"] for e in errors}
        self.assertIn("event_name", error_fields)
        self.assertIn("event_id", error_fields)
        self.assertIn("timestamp", error_fields)
        self.assertIn("utm_source", error_fields)


class EventNormalizationTests(unittest.TestCase):
    def test_normalize_event_applies_defaults_and_lowercases(self):
        payload = {
            "event_id": "evt_2",
            "event_name": "visit",
            "timestamp": "2026-03-05T09:00:00Z",
            "user_id": "u2",
            "utm_source": "  LINKEDIN ",
            "utm_medium": "",
        }

        normalized = normalize_event(payload)

        self.assertEqual(normalized["utm_source"], "linkedin")
        self.assertEqual(normalized["utm_medium"], "unknown")
        self.assertEqual(normalized["utm_campaign"], "unknown")


if __name__ == "__main__":
    unittest.main()
