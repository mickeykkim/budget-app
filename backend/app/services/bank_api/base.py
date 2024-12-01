from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Type

from typing_extensions import TypedDict


class TokenResponse(TypedDict):
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime


class BankAPIError(Exception):
    """Base exception for bank API errors."""

    pass


class TokenRefreshError(BankAPIError):
    """Raised when token refresh fails."""

    pass


class BankAPI(ABC):
    """Abstract base class for bank API implementations."""

    @abstractmethod
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        pass

    @abstractmethod
    def exchange_code(self, auth_code: str) -> TokenResponse:
        """Exchange authorization code for access token."""
        pass


def get_bank_api(account_type: str) -> BankAPI:
    """Factory function to get appropriate bank API implementation."""
    # Import here to avoid circular imports
    from app.services.bank_api.monzo import MonzoAPI

    apis: dict[str, Type[BankAPI]] = {
        "monzo": MonzoAPI,
    }

    api_class = apis.get(account_type.lower())
    if not api_class:
        raise ValueError(f"Unsupported bank API type: {account_type}")

    return api_class()
