import pytest
from app.services.publication_gate import evaluate_publication

def test_breaking_change_blocked():
    change = {"type": "decimal_to_string", "field": "amount"}
    dependencies = [{"id": 1}]
    result = evaluate_publication(change, dependencies)
    assert result.decision == "BLOCK"

def test_safe_change_allowed():
    change = {"type": "add_optional_field", "field": "notes"}
    dependencies = []
    result = evaluate_publication(change, dependencies)
    assert result.decision == "ALLOW"

def test_fail_closed_on_error():
    malformed_data = "not_a_dict"
    result = evaluate_publication(malformed_data, [])
    assert result.decision == "BLOCK"
    assert "safety message" in result.reason.lower() or "error" in result.reason.lower()
