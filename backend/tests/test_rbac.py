import pytest
from tests.conftest import get_auth_header

def test_analyst_cannot_create_partner(client, analyst_user):
    headers = get_auth_header(analyst_user)
    response = client.post("/api/partners", json={"name": "New Partner"}, headers=headers)
    assert response.status_code == 403

def test_engineer_can_create_partner(client, engineer_user):
    headers = get_auth_header(engineer_user)
    response = client.post("/api/partners", json={"name": "New Partner"}, headers=headers)
    assert response.status_code in [200, 201]
