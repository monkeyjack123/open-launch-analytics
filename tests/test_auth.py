import unittest

from open_launch_analytics.auth import (
    ApiKeyManager,
    validate_api_key,
    validate_api_key_hash,
)


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


class ApiKeyManagerTests(unittest.TestCase):
    def test_create_and_validate_hashed_key(self):
        manager = ApiKeyManager()

        created = manager.create_key("ingest-prod")
        result = validate_api_key_hash(created["api_key"], manager.active_key_hashes())

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], 200)

    def test_rotate_key_invalidates_old_secret(self):
        manager = ApiKeyManager()

        created = manager.create_key("ingest-prod")
        rotated = manager.rotate_key(created["key_id"])

        stale_result = validate_api_key_hash(created["api_key"], manager.active_key_hashes())
        fresh_result = validate_api_key_hash(rotated["api_key"], manager.active_key_hashes())

        self.assertFalse(stale_result["ok"])
        self.assertEqual(stale_result["status"], 403)
        self.assertTrue(fresh_result["ok"])

    def test_revoke_key_blocks_validation(self):
        manager = ApiKeyManager()

        created = manager.create_key("ingest-staging")
        revoke = manager.revoke_key(created["key_id"])
        result = validate_api_key_hash(created["api_key"], manager.active_key_hashes())

        self.assertTrue(revoke["ok"])
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 403)

    def test_list_keys_never_exposes_plaintext_api_key(self):
        manager = ApiKeyManager()
        created = manager.create_key("owner")

        records = manager.list_keys()

        self.assertEqual(len(records), 1)
        self.assertNotIn(created["api_key"], records[0].preview)
        self.assertIn("...", records[0].preview)


if __name__ == "__main__":
    unittest.main()
