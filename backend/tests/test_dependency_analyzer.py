import pytest
from app.services.dependency_analyzer import extract_fields, analyze_dependencies

def test_extract_fields_from_select():
    query = "SELECT id, name FROM users"
    fields = extract_fields(query)
    assert "id" in fields
    assert "name" in fields

def test_extract_fields_from_aggregation():
    query = "SELECT SUM(amount), AVG(price) FROM sales"
    fields = extract_fields(query)
    assert "amount" in fields
    assert "price" in fields

def test_affected_dependency_detected():
    changed_fields = ["amount"]
    dependencies = [{"id": 1, "query": "SELECT SUM(amount) FROM tx"}]
    affected = analyze_dependencies(changed_fields, dependencies)
    assert len(affected) == 1
    assert affected[0]["id"] == 1
