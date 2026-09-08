import hashlib
import json
from typing import Optional, Dict, Any


def normalize_schema(schema: Dict[str, Any]) -> str:
    """Normalize a schema JSON for consistent hashing.
    Sorts keys, strips whitespace, lowercases type values."""
    def _normalize_value(value):
        if isinstance(value, dict):
            return {k: _normalize_value(v) for k, v in sorted(value.items())}
        elif isinstance(value, list):
            return [_normalize_value(item) for item in value]
        elif isinstance(value, str):
            return value.strip().lower()
        elif isinstance(value, bool):
            return value
        return value

    normalized = _normalize_value(schema)
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"))


def hash_schema(schema: Dict[str, Any]) -> str:
    """Generate SHA-256 hash of normalized schema."""
    normalized = normalize_schema(schema)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def is_duplicate_schema(new_hash: str, existing_hashes: list) -> bool:
    """Check if schema hash already exists."""
    return new_hash in existing_hashes
