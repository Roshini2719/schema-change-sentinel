from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoints():
    print("🧪 Running End-to-End FastAPI integration tests...")
    
    # Root health check
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

    # Login
    login_res = client.post("/api/auth/login", json={"email": "admin@finbank.com", "password": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Dashboard Metrics
    metrics_res = client.get("/api/dashboard/metrics", headers=headers)
    assert metrics_res.status_code == 200
    metrics_data = metrics_res.json()
    assert "total_runs" in metrics_data

    # List Schemas
    schemas_res = client.get("/api/schemas", headers=headers)
    assert schemas_res.status_code == 200
    assert len(schemas_res.json()) > 0

    # Demo Scenario (Removed Required Field)
    scenario_res = client.post("/api/demo/run-scenario", json={"scenario": "SCENARIO_2_REMOVED_REQUIRED"}, headers=headers)
    assert scenario_res.status_code == 200
    sc_data = scenario_res.json()
    assert sc_data["publication_decision"] == "BLOCK"

    # Experiments Endpoint
    exp_res = client.post("/api/experiments/run?runs_count=50", headers=headers)
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["sentinel_metrics"]["unsafe_publication_rate_pct"] == 0.0

    print("✅ All FastAPI integration tests passed with 100% success!")

if __name__ == "__main__":
    test_api_endpoints()
