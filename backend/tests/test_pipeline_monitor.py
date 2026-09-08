import pytest
from app.services.pipeline_monitor import check_pipeline_health

def test_zero_records_detected():
    stats = {"expected_records": 1000, "actual_records": 0}
    health = check_pipeline_health(stats)
    assert not health.is_healthy

def test_large_drop_detected():
    stats = {"expected_records": 1000, "actual_records": 100}
    health = check_pipeline_health(stats)
    assert not health.is_healthy
