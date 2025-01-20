from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing_extensions import TypedDict

from app.api.dependencies import get_current_user, get_db
from app.core.config import get_settings
from app.schemas.bank_account import BankAccountCreate
from app.schemas.user import UserInDB
from app.services.bank_account_service import BankAccountService
from app.services.bank_api.monzo import MonzoAPI

settings = get_settings()
router = APIRouter()


class OAuthCallbackResponse(TypedDict):
    status: str
    accounts: list[dict[str, str | None]]


@router.get("/monzo/auth", response_model=dict[str, str])
async def monzo_auth_url() -> dict[str, str]:
    """Generate Monzo authorization URL"""
    return {
        "auth_url": (
            "https://auth.monzo.com/"
            f"?client_id={settings.MONZO_CLIENT_ID}"
            f"&redirect_uri={settings.MONZO_REDIRECT_URI}"
            "&response_type=code"
            "&state=monzo"
        )
    }


@router.get("/callback", response_model=OAuthCallbackResponse)
async def oauth_callback(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    code: str = Query(...),
    state: str = Query(...),
) -> OAuthCallbackResponse:
    """Handle OAuth callback from Monzo"""
    if state != "monzo":
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    try:
        monzo_api = MonzoAPI()
        token_response = monzo_api.exchange_code(code)

        # Get account information
        accounts = monzo_api.get_accounts(token_response["access_token"])
        if not accounts:
            raise HTTPException(
                status_code=400,
                detail="No Monzo accounts found",
            )

        # Create bank account records for each Monzo account
        bank_account_service = BankAccountService(db)
        created_accounts = []

        for account in accounts:
            bank_account = bank_account_service.create(
                user_id=current_user.id,
                bank_account_create=BankAccountCreate(
                    account_type="monzo",
                    account_name=account.get("description", "Monzo Account"),
                    account_identifier=account["id"],
                    access_token=token_response["access_token"],
                    refresh_token=token_response["refresh_token"],
                    token_expires_at=token_response["expires_at"],
                ),
            )
            created_accounts.append(bank_account)

        return {
            "status": "success",
            "accounts": [
                {"id": str(acc.id), "name": acc.account_name}
                for acc in created_accounts
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
