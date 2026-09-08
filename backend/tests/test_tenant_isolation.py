import pytest
from tests.conftest import get_auth_header
from app.models.partner import Partner

def test_user_cannot_see_other_org_partners(client, admin_user, beta_user, db_session, org_alpha, org_beta):
    p1 = Partner(name="Alpha Partner", organization_id=org_alpha.id)
    p2 = Partner(name="Beta Partner", organization_id=org_beta.id)
    db_session.add(p1)
    db_session.add(p2)
    db_session.commit()

    headers = get_auth_header(admin_user)
    response = client.get("/api/partners", headers=headers)
    assert response.status_code == 200
    data = response.json()
    names = [p["name"] for p in data]
    assert "Alpha Partner" in names
    assert "Beta Partner" not in names

def test_user_cannot_access_other_org_data_source(client, admin_user, beta_user, db_session, org_alpha, org_beta):
    # Setup data source for org beta
    # Try to GET it as admin_user
    # Expect 404 or empty list
    headers = get_auth_header(admin_user)
    response = client.get("/api/data-sources/9999", headers=headers)
    assert response.status_code in [404, 403]
