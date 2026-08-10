"""ProjectForge AI — Test Configuration & Fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Override engine in database module BEFORE importing main app
import backend.app.core.database as db_module

# Use file-based test database or in-memory shared engine
TEST_DB_URL = "sqlite:///./test_projectforge.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
db_module.engine = test_engine
db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

import backend.app.models  # Register all models with Base.metadata
from backend.app.core.database import Base, get_db
from backend.app.main import app
from backend.app.core.security import hash_password
from backend.app.models.user import User


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Create fresh database tables for each test."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(setup_test_db):
    """Provide DB session for tests."""
    session = db_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden DB dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user in DB."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Login and return authorization headers with Bearer token."""
    res = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "password123",
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

