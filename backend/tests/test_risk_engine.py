import pytest
from app.services.risk_engine import calculate_risk

def test_critical_change_scores_100():
    changes = [{"breaking": True, "severity": "CRITICAL"}]
    score = calculate_risk(changes)
    assert score >= 75

def test_no_change_scores_zero():
    changes = []
    score = calculate_risk(changes)
    assert score == 0
