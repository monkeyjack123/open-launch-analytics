import unittest

from open_launch_analytics.auth import validate_api_key


class ApiKeyValidationTests(unittest.TestCase):
    def test_missing_api_key_returns_401(self):
        result = validate_api_key(None, {"k_live_1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 401)
        self.assertEqual(result["errors"][0]["error"], "missing_api_key")

    def test_invalid_api_key_returns_403(self):
        result = validate_api_key("k_bad", {"k_live_1"})

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 403)
        self.assertEqual(result["errors"][0]["error"], "invalid_api_key")

    def test_valid_api_key_returns_ok(self):
        result = validate_api_key("k_live_1", {"k_live_1"})

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["errors"], [])


if __name__ == "__main__":
    unittest.main()
