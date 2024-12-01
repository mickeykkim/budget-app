from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.domain.types import SQLiteUUID


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(SQLiteUUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount", back_populates="user"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user"
    )


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[UUID] = mapped_column(SQLiteUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(SQLiteUUID, ForeignKey("users.id"))
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    account_name: Mapped[Optional[str]] = mapped_column(String(255))
    account_identifier: Mapped[Optional[str]] = mapped_column(String(255))
    access_token: Mapped[Optional[str]] = mapped_column(String)
    refresh_token: Mapped[Optional[str]] = mapped_column(String)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship("User", back_populates="bank_accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="bank_account"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(SQLiteUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(SQLiteUUID, ForeignKey("users.id"))
    bank_account_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("bank_accounts.id")
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount", back_populates="transactions"
    )
