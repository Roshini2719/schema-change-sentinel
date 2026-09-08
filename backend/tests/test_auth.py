import pytest

def test_valid_login(client, admin_user):
    response = client.post("/api/auth/login", data={"username": "admin@alpha.com", "password": "admin123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_login(client, admin_user):
    response = client.post("/api/auth/login", data={"username": "admin@alpha.com", "password": "wrongpassword"})
    assert response.status_code == 401
