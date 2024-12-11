# tests/api/v1/endpoints/test_admin.py

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.user import UserCreate
from app.services.user_service import UserService


def test_reset_database_development(client: TestClient, db: Session, monkeypatch):
    """Test database reset in development environment"""
    # Mock the environment to be development
    settings = get_settings()
    monkeypatch.setattr(settings, "ENVIRONMENT", "development")

    # Create a test user
    user_service = UserService(db)
    test_user = user_service.create(
        UserCreate(email="test@example.com", password="testpass123")
    )
    assert test_user is not None

    # Verify user exists
    saved_user = user_service.get_by_email("test@example.com")
    assert saved_user is not None

    # Reset database
    response = client.post("/api/v1/admin/reset-database")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Database reset successful"}

    # Verify user still exists
    saved_user = user_service.get_by_email("test@example.com")
    assert saved_user is not None


def test_reset_database_production(client: TestClient, db: Session, monkeypatch):
    """Test database reset is blocked in production environment"""
    # Mock the environment to be production
    settings = get_settings()
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")

    # Attempt to reset database
    response = client.post("/api/v1/admin/reset-database")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "not allowed in this environment" in response.json()["detail"]
