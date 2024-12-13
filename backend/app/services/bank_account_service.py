"""
Service for BankAccount model
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.domain.models import BankAccount, Transaction
from app.schemas.bank_account import BankAccountCreate, BankAccountUpdate
from app.services.bank_api import TokenRefreshError
from app.services.bank_api.base import get_bank_api
from app.services.bank_api.monzo import MonzoAPI


class BankAccountService:
    """Service for BankAccount model"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self, user_id: UUID, bank_account_create: BankAccountCreate
    ) -> BankAccount:
        """Create a new bank account."""
        db_bank_account = BankAccount(
            user_id=user_id,
            account_type=bank_account_create.account_type,
            account_name=bank_account_create.account_name,
            account_identifier=bank_account_create.account_identifier,
            access_token=bank_account_create.access_token,
            refresh_token=bank_account_create.refresh_token,
            token_expires_at=bank_account_create.token_expires_at,
        )
        self.db.add(db_bank_account)
        self.db.commit()
        self.db.refresh(db_bank_account)
        return db_bank_account

    def get_by_id(self, user_id: UUID, bank_account_id: UUID) -> Optional[BankAccount]:
        """Get a bank account by ID, ensuring it belongs to the user."""
        return (
            self.db.query(BankAccount)
            .filter(
                BankAccount.id == bank_account_id,
                BankAccount.user_id == user_id,
            )
            .first()
        )

    def get_multi(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> tuple[list[BankAccount], int]:
        """Get multiple bank accounts with pagination."""
        conditions = [BankAccount.user_id == user_id]

        if not include_inactive:
            conditions.append(
                BankAccount.is_active  # noqa: E712  # pylint: disable=singleton-comparison
                == True
            )

        # Count total matching accounts
        count_query = (
            select(func.count())  # pylint: disable=not-callable
            .select_from(BankAccount)
            .where(and_(*conditions))
        )
        total = self.db.scalar(count_query) or 0

        # Get paginated accounts
        query = (
            select(BankAccount)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(BankAccount.created_at.desc())
        )
        bank_accounts = list(self.db.scalars(query).all())

        return bank_accounts, total

    def update(
        self,
        user_id: UUID,
        bank_account_id: UUID,
        bank_account_update: BankAccountUpdate,
    ) -> Optional[BankAccount]:
        """Update a bank account."""
        bank_account = self.get_by_id(user_id, bank_account_id)
        if not bank_account:
            return None

        update_data = bank_account_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(bank_account, field, value)

        self.db.commit()
        self.db.refresh(bank_account)
        return bank_account

    def delete(self, user_id: UUID, bank_account_id: UUID) -> bool:
        """Hard delete a bank account."""
        bank_account = self.get_by_id(user_id, bank_account_id)
        if not bank_account:
            return False

        # Remove associated transactions first
        self.db.query(Transaction).filter(
            Transaction.bank_account_id == bank_account_id
        ).delete()

        # Delete the bank account
        self.db.delete(bank_account)
        self.db.commit()
        return True

    def deactivate(self, user_id: UUID, bank_account_id: UUID) -> bool:
        """Soft delete a bank account by setting is_active to False."""
        bank_account = self.get_by_id(user_id, bank_account_id)
        if not bank_account:
            return False

        bank_account.is_active = False
        self.db.commit()
        return True

    def refresh_token(self, bank_account_id: UUID) -> BankAccount:
        """Refresh the access token for a bank account."""
        bank_account = (
            self.db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
        )

        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bank account not found"
            )

        if not bank_account.refresh_token:
            raise TokenRefreshError("No refresh token available")

        try:
            bank_api = get_bank_api(bank_account.account_type)
            token_response = bank_api.refresh_token(bank_account.refresh_token)

            bank_account.access_token = token_response["access_token"]
            bank_account.refresh_token = token_response.get(
                "refresh_token", bank_account.refresh_token
            )
            bank_account.token_expires_at = token_response["expires_at"]

            self.db.commit()
            self.db.refresh(bank_account)
            return bank_account

        except TokenRefreshError as e:
            # Re-raise the exception to be handled by the caller
            logger.error(f"Token refresh error: {e}")
            raise

    def sync_monzo_transactions(self, user_id: UUID, bank_account_id: UUID) -> int:
        """Sync transactions for a Monzo account"""
        bank_account = self.get_by_id(user_id, bank_account_id)
        if not bank_account or bank_account.account_type != "monzo":
            raise ValueError("Invalid bank account")

        if not bank_account.access_token or not bank_account.account_identifier:
            raise ValueError("Invalid bank account credentials")

        monzo_api = MonzoAPI()

        # Get latest transaction date for this account
        latest_transaction = (
            self.db.query(Transaction)
            .filter(Transaction.bank_account_id == bank_account_id)
            .order_by(Transaction.created_at.desc())
            .first()
        )

        since = latest_transaction.created_at if latest_transaction else None

        # Fetch transactions from Monzo
        transactions = monzo_api.get_transactions(
            access_token=bank_account.access_token,
            account_id=bank_account.account_identifier,
            since=since,
        )

        # Create new transactions
        new_transactions = []
        for txn in transactions:
            amount = Decimal(txn["amount"]) / 100  # Monzo amounts are in pennies
            new_transactions.append(
                Transaction(
                    user_id=bank_account.user_id,
                    bank_account_id=bank_account_id,
                    amount=amount,
                    description=txn.get("description", ""),
                    created_at=datetime.fromisoformat(txn["created"]).replace(
                        tzinfo=None
                    ),
                )
            )

        if new_transactions:
            self.db.bulk_save_objects(new_transactions)
            self.db.commit()

        return len(new_transactions)
