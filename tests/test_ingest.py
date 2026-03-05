import unittest

from open_launch_analytics.ingest import ingest_event


class IngestEventTests(unittest.TestCase):
    def test_ingest_event_returns_accepted_for_valid_payload(self):
        payload = {
            "event_id": "evt_100",
            "event_name": "signup",
            "timestamp": "2026-03-05T10:00:00Z",
            "user_id": "user_100",
            "utm_source": "  ProductHunt  ",
        }

        result = ingest_event(payload)

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 202)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["event"]["utm_source"], "producthunt")
        self.assertEqual(result["event"]["utm_medium"], "unknown")

    def test_ingest_event_returns_errors_for_invalid_payload(self):
        payload = {
            "event_id": "evt_101",
            "timestamp": "invalid",
            "user_id": "user_101",
        }

        result = ingest_event(payload)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 400)
        self.assertIsNone(result["event"])
        self.assertGreaterEqual(len(result["errors"]), 2)
        error_fields = {e["field"] for e in result["errors"]}
        self.assertIn("event_name", error_fields)
        self.assertIn("timestamp", error_fields)


if __name__ == "__main__":
    unittest.main()
