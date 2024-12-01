from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.core.config import Settings, get_settings
from app.core.database import Base
from app.core.security import create_access_token
from app.main import app
from app.models.domain.models import BankAccount
from app.schemas.user import UserCreate
from app.services.user_service import UserService


# SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Test settings override
def get_test_settings():
    return Settings(
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT="5432",
        POSTGRES_DB="test_db",
        SECRET_KEY="test_secret_key",
        AWS_ACCESS_KEY_ID="test",
        AWS_SECRET_ACCESS_KEY="test",
    )


# Override settings for testing
app.dependency_overrides[get_settings] = get_test_settings

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    # Create all tables for each test
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    # Start a nested transaction
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Roll back the nested transaction
    if transaction.is_active:
        transaction.rollback()
    session.close()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Don't close here as it's handled in the db fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db):
    user_service = UserService(db)
    user_data = UserCreate(email="test@example.com", password="testpassword123")
    user = user_service.create(user_data)
    db.commit()  # Make sure to commit the transaction
    return user


@pytest.fixture
def test_bank_account(db, test_user) -> BankAccount:
    bank_account = BankAccount(
        user_id=test_user.id,
        account_type="plaid",
        account_name="Test Checking Account",
        account_identifier="1234",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        token_expires_at=datetime.utcnow() + timedelta(hours=1),
        is_active=True,
    )
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    return bank_account


@pytest.fixture
def mock_bank_api(mocker):
    mock_api = mocker.Mock()
    mock_api.refresh_token.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_at": datetime.utcnow() + timedelta(days=30),
    }
    return mock_api


@pytest.fixture
def user_token_headers(test_user) -> dict[str, str]:
    """Create authentication headers for a test user."""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def mock_monzo_api(mocker):
    """Create a mock Monzo API with default successful responses"""
    mock_api = mocker.Mock()
    mock_api.exchange_code.return_value = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_at": datetime.utcnow() + timedelta(hours=1),
    }
    mock_api.get_accounts.return_value = [
        {
            "id": "acc_123",
            "description": "Test Account",
            "created": "2024-01-01T00:00:00Z",
            "type": "uk_retail",
        }
    ]
    return mock_api
