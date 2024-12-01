from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BankAccountBase(BaseModel):
    account_type: str = Field(
        ..., description="Type of bank account (e.g., checking, savings)"
    )
    account_name: Optional[str] = Field(
        None, description="User-defined name for the account"
    )
    account_identifier: Optional[str] = Field(
        None, description="Last 4 digits or identifier of the account"
    )


class BankAccountCreate(BankAccountBase):
    access_token: str = Field(..., description="Access token from bank API")
    refresh_token: Optional[str] = Field(
        None, description="Refresh token from bank API"
    )
    token_expires_at: Optional[datetime] = Field(
        None, description="Token expiration timestamp"
    )


class BankAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    is_active: Optional[bool] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class BankAccountInDB(BankAccountBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class BankAccountRead(BankAccountInDB):
    pass


class BankAccountList(BaseModel):
    items: list[BankAccountRead]
    total: int
