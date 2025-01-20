from typing import Any
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import get_settings

settings = get_settings()


def test_monzo_auth_url(client: TestClient) -> None:
    """Test generation of Monzo authorization URL"""
    response = client.get("/api/v1/oauth/monzo/auth")
    assert response.status_code == status.HTTP_200_OK
    assert "auth_url" in response.json()
    auth_url = response.json()["auth_url"]
    assert settings.MONZO_CLIENT_ID in auth_url
    assert settings.MONZO_REDIRECT_URI in auth_url


def test_oauth_callback_invalid_state(
    client: TestClient, user_token_headers: dict[str, str]
) -> None:
    """Test callback with invalid state parameter"""
    response = client.get(
        "/api/v1/oauth/callback?code=test_code&state=invalid",
        headers=user_token_headers,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_oauth_callback_success(
    client: TestClient,
    user_token_headers: dict[str, str],
    mocker: Any,
    mock_monzo_api,
) -> None:
    """Test successful OAuth callback"""
    mocker.patch(
        "app.api.v1.endpoints.oauth.routes.MonzoAPI", return_value=mock_monzo_api
    )

    response = client.get(
        "/api/v1/oauth/callback?code=test_code&state=monzo",
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert len(data["accounts"]) == 1
    assert "id" in data["accounts"][0]
    assert UUID(data["accounts"][0]["id"])  # Verify it's a valid UUID
    assert data["accounts"][0]["name"] == "Test Account"


def test_oauth_callback_no_accounts(
    client: TestClient,
    user_token_headers: dict[str, str],
    mocker: Any,
    mock_monzo_api,
) -> None:
    """Test OAuth callback when no accounts are found"""
    mock_monzo_api.get_accounts.return_value = []
    mocker.patch(
        "app.api.v1.endpoints.oauth.routes.MonzoAPI", return_value=mock_monzo_api
    )

    response = client.get(
        "/api/v1/oauth/callback?code=test_code&state=monzo",
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No Monzo accounts found" in response.json()["detail"]


def test_oauth_callback_unauthorized(client: TestClient) -> None:
    """Test OAuth callback without authentication"""
    response = client.get("/api/v1/oauth/callback?code=test_code&state=monzo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
