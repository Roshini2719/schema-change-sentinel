import pytest
from app.services.contract_validator import validate_contract

def test_valid_schema_passes_contract():
    schema = {"fields": {"id": {"type": "string", "required": True}, "val": {"type": "int", "required": True}}}
    contract = {"rules": [{"field": "id", "type": "string"}, {"field": "val", "type": "int"}]}
    result = validate_contract(schema, contract)
    assert result.is_valid

def test_missing_required_field_violates():
    schema = {"fields": {"val": {"type": "int", "required": True}}}
    contract = {"rules": [{"field": "id", "required": True}]}
    result = validate_contract(schema, contract)
    assert not result.is_valid

def test_wrong_type_violates():
    schema = {"fields": {"id": {"type": "int", "required": True}}}
    contract = {"rules": [{"field": "id", "type": "string"}]}
    result = validate_contract(schema, contract)
    assert not result.is_valid
