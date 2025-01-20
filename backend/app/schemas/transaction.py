from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    amount: Decimal = Field(..., description="Transaction amount")
    description: str | None = Field(None, description="Transaction description")


class TransactionCreate(TransactionBase):
    bank_account_id: UUID = Field(..., description="ID of the associated bank account")


class TransactionUpdate(TransactionBase):
    pass


class TransactionInDB(TransactionBase):
    id: UUID
    user_id: UUID
    bank_account_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionRead(TransactionInDB):
    pass


class TransactionList(BaseModel):
    items: list[TransactionRead]
    total: int
