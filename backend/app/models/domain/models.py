from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy_utils import StringEncryptedType

from app.core.config import get_settings
from app.core.database import Base
from app.models.domain.types import SQLiteUUID

SETTINGS = get_settings()
ENCRYPTION_KEY = SETTINGS.ENCRYPTION_KEY


class User(Base):
    __tablename__ = "users"
    model_config = ConfigDict(from_attributes=True)

    id: Mapped[UUID] = mapped_column(SQLiteUUID, primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(
        StringEncryptedType(String, ENCRYPTION_KEY), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
    )

    # Relationships
    bank_accounts: Mapped[list["BankAccount"]] = relationship(
        "BankAccount", back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    model_config = ConfigDict(from_attributes=True)

    id: Mapped[UUID] = mapped_column(SQLiteUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    account_name: Mapped[str] = mapped_column(
        StringEncryptedType(String(255), ENCRYPTION_KEY), nullable=True
    )
    account_identifier: Mapped[str] = mapped_column(
        StringEncryptedType(String(255), ENCRYPTION_KEY), nullable=True
    )
    institution_name: Mapped[str] = mapped_column(String(255), nullable=True)

    # Encrypted tokens
    access_token: Mapped[Optional[str]] = mapped_column(
        StringEncryptedType(String, ENCRYPTION_KEY), nullable=True
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(
        StringEncryptedType(String, ENCRYPTION_KEY), nullable=True
    )

    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="bank_accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="bank_account", cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transactions"
    model_config = ConfigDict(from_attributes=True)

    id: Mapped[UUID] = mapped_column(SQLiteUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    bank_account_id: Mapped[UUID] = mapped_column(
        SQLiteUUID, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    bank_account: Mapped["BankAccount"] = relationship(
        "BankAccount", back_populates="transactions"
    )
