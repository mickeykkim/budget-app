"""
API layer for Monzo Bank interaction
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional, cast
from urllib.parse import urljoin

import requests
from fastapi import HTTPException
from typing_extensions import TypedDict

from app.core.config import get_settings
from app.services.bank_api.base import BankAPI, TokenRefreshError, TokenResponse

settings = get_settings()


class MonzoAccount(TypedDict):
    """Monzo account data"""

    id: str
    description: str
    created: str
    type: str


class MonzoTransaction(TypedDict):
    """Monzo transaction data"""

    id: str
    amount: int
    created: str
    description: str
    merchant: Optional[dict[str, Any]]


class MonzoAPI(BankAPI):
    """Monzo Bank API client"""

    def __init__(self) -> None:
        self.base_url = "https://api.monzo.com"
        self.client_id = settings.MONZO_CLIENT_ID
        self.client_secret = settings.MONZO_CLIENT_SECRET
        self.redirect_uri = settings.MONZO_REDIRECT_URI

    def _make_request(
        self, method: str, endpoint: str, access_token: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Make an authenticated request to the Monzo API"""
        url = urljoin(self.base_url, endpoint)
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.request(
                method=method, url=url, headers=headers, timeout=30, **kwargs
            )

            if response.status_code == 401:
                raise TokenRefreshError("Access token expired")
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Monzo API error: {response.text}",
                )

            return cast(dict[str, Any], response.json())

        except requests.RequestException as e:
            raise HTTPException(
                status_code=503, detail=f"Failed to communicate with Monzo: {str(e)}"
            ) from e

    def exchange_code(self, auth_code: str) -> TokenResponse:
        """Exchange authorization code for access token"""
        try:
            response = requests.post(
                f"{self.base_url}/oauth2/token",
                timeout=30,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": auth_code,
                },
            )

            if response.status_code != 200:
                raise TokenRefreshError(f"Code exchange failed: {response.text}")

            data = response.json()
            return TokenResponse(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=datetime.now(UTC) + timedelta(seconds=data["expires_in"]),
            )
        except requests.RequestException as e:
            raise TokenRefreshError(str(e)) from e

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token"""
        try:
            response = requests.post(
                f"{self.base_url}/oauth2/token",
                timeout=30,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                },
            )

            if response.status_code != 200:
                raise TokenRefreshError(f"Token refresh failed: {response.text}")

            data = response.json()
            return TokenResponse(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=datetime.now(UTC) + timedelta(seconds=data["expires_in"]),
            )
        except requests.RequestException as e:
            raise TokenRefreshError(str(e)) from e

    def get_accounts(self, access_token: str) -> list[MonzoAccount]:
        """Get Monzo accounts"""
        response = self._make_request("GET", "/accounts", access_token)
        return cast(list[MonzoAccount], response["accounts"])

    def get_transactions(
        self,
        access_token: str,
        account_id: str,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[MonzoTransaction]:
        """Get Monzo transactions"""
        params = {"account_id": account_id, "limit": limit}
        if since:
            params["since"] = since.isoformat() + "Z"

        response = self._make_request(
            "GET", "/transactions", access_token, params=params
        )
        return cast(list[MonzoTransaction], response["transactions"])
