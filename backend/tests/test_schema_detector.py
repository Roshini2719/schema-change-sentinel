import pytest
from app.services.schema_detector import detect_schema_changes

BASE_SCHEMA = {
    "fields": {
        "transaction_id": {"type": "string", "required": True, "nullable": False, "primary_key": True},
        "customer_id": {"type": "string", "required": True, "nullable": False},
        "amount": {"type": "decimal", "required": True, "nullable": False},
        "currency": {"type": "string", "required": True, "nullable": False},
        "transaction_date": {"type": "datetime", "required": True, "nullable": False},
        "status": {"type": "enum", "required": True, "nullable": False, "values": ["SUCCESS", "FAILED", "PENDING"]},
    }
}

def test_required_field_removed():
    new_schema = {"fields": {k: v for k, v in BASE_SCHEMA["fields"].items() if k != "customer_id"}}
    changes = detect_schema_changes(BASE_SCHEMA, new_schema)
    assert any(c.breaking and c.severity == "CRITICAL" for c in changes)

def test_decimal_to_string():
    new_schema = {"fields": dict(BASE_SCHEMA["fields"])}
    new_schema["fields"]["amount"] = {"type": "string", "required": True, "nullable": False}
    changes = detect_schema_changes(BASE_SCHEMA, new_schema)
    assert any(c.breaking and c.severity == "CRITICAL" for c in changes)

def test_optional_nullable_field_added():
    new_schema = {"fields": dict(BASE_SCHEMA["fields"])}
    new_schema["fields"]["notes"] = {"type": "string", "required": False, "nullable": True}
    changes = detect_schema_changes(BASE_SCHEMA, new_schema)
    assert not any(c.breaking for c in changes)

def test_required_field_added_without_default():
    new_schema = {"fields": dict(BASE_SCHEMA["fields"])}
    new_schema["fields"]["notes"] = {"type": "string", "required": True, "nullable": False}
    changes = detect_schema_changes(BASE_SCHEMA, new_schema)
    assert any(c.breaking for c in changes)

def test_primary_key_removed():
    new_schema = {"fields": {k: v for k, v in BASE_SCHEMA["fields"].items() if k != "transaction_id"}}
    changes = detect_schema_changes(BASE_SCHEMA, new_schema)
    assert any(c.breaking and c.severity == "CRITICAL" for c in changes)

def test_enum_value_removed():
    new_schema = {"fields": dict(BASE_SCHEMA["fields"])}
    new_schema["fields"]["status"] = {"type": "enum", "required": True, "nullable": False, "values": ["SUCCESS", "FAILED"]}
    changes = detect_schema_changes(BASE_SCHEMA, new_schema)
    assert any(c.breaking for c in changes)

def test_nullable_to_non_nullable():
    base = {"fields": {"notes": {"type": "string", "required": False, "nullable": True}}}
    new_schema = {"fields": {"notes": {"type": "string", "required": False, "nullable": False}}}
    changes = detect_schema_changes(base, new_schema)
    assert any(c.breaking for c in changes)
