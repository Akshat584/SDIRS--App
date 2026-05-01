import pytest
import os

# Set test environment
os.environ["ENVIRONMENT"] = "test"

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from main import app

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the tables after session
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    from app.models.sqlalchemy import User
    from app.core.security import get_password_hash
    
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=get_password_hash("StrongPassword123!"),
        role="citizen",
        status="active"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    from app.core.security import create_access_token
    access_token = create_access_token(data={"sub": test_user.email, "role": test_user.role})
    return {"Authorization": f"Bearer {access_token}"}
