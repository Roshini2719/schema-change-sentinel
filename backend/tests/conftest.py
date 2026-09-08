import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def org_alpha(db_session):
    org = Organization(name="Fintech Alpha", status="active")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def org_beta(db_session):
    org = Organization(name="Fintech Beta", status="active")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def admin_user(db_session, org_alpha):
    user = User(
        organization_id=org_alpha.id,
        name="Admin User",
        email="admin@alpha.com",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def engineer_user(db_session, org_alpha):
    user = User(
        organization_id=org_alpha.id,
        name="Engineer User",
        email="engineer@alpha.com",
        password_hash=hash_password("engineer123"),
        role=UserRole.DATA_ENGINEER,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def analyst_user(db_session, org_alpha):
    user = User(
        organization_id=org_alpha.id,
        name="Analyst User",
        email="analyst@alpha.com",
        password_hash=hash_password("analyst123"),
        role=UserRole.DATA_ANALYST,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def beta_user(db_session, org_beta):
    user = User(
        organization_id=org_beta.id,
        name="Beta Admin",
        email="admin@beta.com",
        password_hash=hash_password("beta123"),
        role=UserRole.ADMIN,
        status="active",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_auth_header(user):
    token = create_access_token({"sub": user.id, "org": user.organization_id, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}
