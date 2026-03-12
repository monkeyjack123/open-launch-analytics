from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import secrets


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _redact_api_key(api_key: str) -> str:
    if len(api_key) <= 8:
        return "***"
    return f"{api_key[:4]}...{api_key[-4:]}"


@dataclass(frozen=True)
class ApiKeyRecord:
    key_id: str
    name: str
    created_at: str
    revoked_at: str | None
    preview: str


class ApiKeyManager:
    """In-memory API key lifecycle helper for MVP key create/rotate/revoke flows."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, str | None]] = {}
        self._hash_to_key_id: dict[str, str] = {}

    def create_key(self, name: str) -> dict[str, str]:
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("name must not be empty")

        key_id = f"key_{secrets.token_hex(8)}"
        api_key = f"ola_{secrets.token_urlsafe(24)}"
        created_at = _utc_now_iso()

        self._records[key_id] = {
            "name": cleaned_name,
            "created_at": created_at,
            "revoked_at": None,
            "preview": _redact_api_key(api_key),
        }
        self._hash_to_key_id[_hash_api_key(api_key)] = key_id

        return {
            "key_id": key_id,
            "name": cleaned_name,
            "api_key": api_key,
            "created_at": created_at,
        }

    def revoke_key(self, key_id: str) -> dict[str, object]:
        record = self._records.get(key_id)
        if record is None:
            return {"ok": False, "error": "not_found", "key_id": key_id}

        if record["revoked_at"] is not None:
            return {
                "ok": False,
                "error": "already_revoked",
                "key_id": key_id,
                "revoked_at": record["revoked_at"],
            }

        revoked_at = _utc_now_iso()
        record["revoked_at"] = revoked_at
        return {"ok": True, "key_id": key_id, "revoked_at": revoked_at}

    def rotate_key(self, key_id: str) -> dict[str, object]:
        record = self._records.get(key_id)
        if record is None:
            return {"ok": False, "error": "not_found", "key_id": key_id}

        if record["revoked_at"] is not None:
            return {"ok": False, "error": "revoked_key", "key_id": key_id}

        old_hashes = [h for h, existing_key_id in self._hash_to_key_id.items() if existing_key_id == key_id]
        for old_hash in old_hashes:
            del self._hash_to_key_id[old_hash]

        next_api_key = f"ola_{secrets.token_urlsafe(24)}"
        self._hash_to_key_id[_hash_api_key(next_api_key)] = key_id
        record["preview"] = _redact_api_key(next_api_key)

        return {
            "ok": True,
            "key_id": key_id,
            "api_key": next_api_key,
            "rotated_at": _utc_now_iso(),
        }

    def list_keys(self) -> list[ApiKeyRecord]:
        keys: list[ApiKeyRecord] = []
        for key_id, record in self._records.items():
            keys.append(
                ApiKeyRecord(
                    key_id=key_id,
                    name=str(record["name"]),
                    created_at=str(record["created_at"]),
                    revoked_at=record["revoked_at"] if isinstance(record["revoked_at"], str) else None,
                    preview=str(record["preview"]),
                )
            )
        return sorted(keys, key=lambda item: item.created_at)

    def active_key_hashes(self) -> set[str]:
        active_ids = {
            key_id for key_id, record in self._records.items() if record["revoked_at"] is None
        }
        return {digest for digest, key_id in self._hash_to_key_id.items() if key_id in active_ids}


def validate_api_key(api_key: str | None, valid_api_keys: set[str]) -> dict[str, object]:
    """Validate ingestion API key against a configured allowlist."""

    if api_key is None or not api_key.strip():
        return {
            "ok": False,
            "status": 401,
            "errors": [
                {
                    "field": "api_key",
                    "error": "missing_api_key",
                    "message": "API key is required",
                }
            ],
        }

    candidate = api_key.strip()
    if candidate not in valid_api_keys:
        return {
            "ok": False,
            "status": 403,
            "errors": [
                {
                    "field": "api_key",
                    "error": "invalid_api_key",
                    "message": "API key is invalid",
                }
            ],
        }

    return {"ok": True, "status": 200, "errors": []}


def validate_api_key_hash(api_key: str | None, valid_api_key_hashes: set[str]) -> dict[str, object]:
    """Validate ingestion API key by SHA-256 digest to avoid plaintext key storage."""

    if api_key is None or not api_key.strip():
        return validate_api_key(api_key, set())

    candidate_hash = _hash_api_key(api_key.strip())
    if candidate_hash not in valid_api_key_hashes:
        return {
            "ok": False,
            "status": 403,
            "errors": [
                {
                    "field": "api_key",
                    "error": "invalid_api_key",
                    "message": "API key is invalid",
                }
            ],
        }

    return {"ok": True, "status": 200, "errors": []}
