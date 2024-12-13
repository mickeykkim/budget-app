from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
import requests
from fastapi import HTTPException

from app.services.bank_api import TokenRefreshError
from app.services.bank_api.monzo import MonzoAPI


@pytest.fixture
def monzo_api(mocker: Any) -> MonzoAPI:
    """Mock Monzo API with test credentials"""
    api = MonzoAPI()
    api.client_id = "test_client_id"
    api.client_secret = "test_client_secret"
    api.redirect_uri = "http://localhost:8000/callback"
    return api


@pytest.fixture
def mock_response(mocker: Any) -> Any:
    """Mock requests.Response"""
    response = mocker.Mock()
    response.status_code = 200
    return response


def test_exchange_code_success(
    monzo_api: MonzoAPI, mock_response: Any, mocker: Any
) -> None:
    """Test successful authorization code exchange"""
    mock_response.json.return_value = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600,
    }
    mocker.patch("requests.post", return_value=mock_response)

    result = monzo_api.exchange_code("test_auth_code")

    assert result["access_token"] == "test_access_token"
    assert result["refresh_token"] == "test_refresh_token"
    assert isinstance(result["expires_at"], datetime)


def test_exchange_code_failure(
    monzo_api: MonzoAPI, mock_response: Any, mocker: Any
) -> None:
    """Test failed authorization code exchange"""
    mock_response.status_code = 400
    mock_response.text = "Invalid code"
    mocker.patch("requests.post", return_value=mock_response)

    with pytest.raises(TokenRefreshError):
        monzo_api.exchange_code("invalid_code")


def test_refresh_token_success(
    monzo_api: MonzoAPI, mock_response: Any, mocker: Any
) -> None:
    """Test successful token refresh"""
    mock_response.json.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600,
    }
    mocker.patch("requests.post", return_value=mock_response)

    result = monzo_api.refresh_token("test_refresh_token")

    assert result["access_token"] == "new_access_token"
    assert result["refresh_token"] == "new_refresh_token"
    assert isinstance(result["expires_at"], datetime)


def test_get_accounts_success(
    monzo_api: MonzoAPI, mock_response: Any, mocker: Any
) -> None:
    """Test successful accounts retrieval"""
    mock_response.json.return_value = {
        "accounts": [
            {
                "id": "acc_123",
                "description": "Test Account",
                "created": "2024-01-01T00:00:00Z",
                "type": "uk_retail",
            }
        ]
    }
    mocker.patch("requests.request", return_value=mock_response)

    accounts = monzo_api.get_accounts("test_access_token")

    assert len(accounts) == 1
    assert accounts[0]["id"] == "acc_123"
    assert accounts[0]["description"] == "Test Account"


def test_get_accounts_unauthorized(
    monzo_api: MonzoAPI, mock_response: Any, mocker: Any
) -> None:
    """Test unauthorized accounts retrieval"""
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mocker.patch("requests.request", return_value=mock_response)

    with pytest.raises(TokenRefreshError):
        monzo_api.get_accounts("invalid_token")


def test_get_transactions_success(
    monzo_api: MonzoAPI, mock_response: Any, mocker: Any
) -> None:
    """Test successful transactions retrieval"""
    mock_response.json.return_value = {
        "transactions": [
            {
                "id": "tx_123",
                "amount": -500,  # Amount in pennies
                "created": "2024-01-01T00:00:00Z",
                "description": "Coffee",
                "merchant": {"name": "Costa Coffee"},
            }
        ]
    }
    mocker.patch("requests.request", return_value=mock_response)

    transactions = monzo_api.get_transactions(
        "test_access_token", "acc_123", since=datetime.now(UTC) - timedelta(days=7)
    )

    assert len(transactions) == 1
    assert transactions[0]["id"] == "tx_123"
    assert transactions[0]["amount"] == -500
    assert transactions[0]["description"] == "Coffee"


def test_get_transactions_network_error(monzo_api: MonzoAPI, mocker: Any) -> None:
    """Test network error handling"""
    mocker.patch(
        "requests.request", side_effect=requests.RequestException("Network error")
    )

    with pytest.raises(HTTPException):
        monzo_api.get_transactions("test_access_token", "acc_123")
