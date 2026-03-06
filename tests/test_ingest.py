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

    def test_ingest_event_returns_401_when_api_key_missing(self):
        payload = {
            "event_id": "evt_102",
            "event_name": "visit",
            "timestamp": "2026-03-05T10:30:00Z",
            "user_id": "user_102",
        }

        result = ingest_event(payload, valid_api_keys={"k_live_1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 401)
        self.assertEqual(result["errors"][0]["error"], "missing_api_key")
        self.assertIsNone(result["event"])

    def test_ingest_event_returns_403_when_api_key_invalid(self):
        payload = {
            "event_id": "evt_103",
            "event_name": "visit",
            "timestamp": "2026-03-05T10:31:00Z",
            "user_id": "user_103",
        }

        result = ingest_event(payload, api_key="k_bad", valid_api_keys={"k_live_1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 403)
        self.assertEqual(result["errors"][0]["error"], "invalid_api_key")
        self.assertIsNone(result["event"])

    def test_ingest_event_returns_accepted_for_valid_api_key(self):
        payload = {
            "event_id": "evt_104",
            "event_name": "visit",
            "timestamp": "2026-03-05T10:32:00Z",
            "user_id": "user_104",
            "utm_source": "X",
        }

        result = ingest_event(payload, api_key="k_live_1", valid_api_keys={"k_live_1"})

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 202)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["event"]["utm_source"], "x")

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
