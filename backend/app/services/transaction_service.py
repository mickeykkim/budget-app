"""
Service for Transaction model
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.domain.models import BankAccount, Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    """Service for Transaction model"""

    def __init__(self, db: Session):
        self.db = db

    def _verify_bank_account(self, user_id: UUID, bank_account_id: UUID) -> None:
        """Verify that the bank account exists and belongs to the user."""
        bank_account = (
            self.db.query(BankAccount)
            .filter(
                BankAccount.id == bank_account_id,
                BankAccount.user_id == user_id,
                BankAccount.is_active  # noqa: E712  # pylint: disable=singleton-comparison
                == True,
            )
            .first()
        )
        if not bank_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found or inactive",
            )

    def create(
        self, user_id: UUID, transaction_create: TransactionCreate
    ) -> Transaction:
        """Create a new transaction."""
        self._verify_bank_account(user_id, transaction_create.bank_account_id)

        db_transaction = Transaction(
            user_id=user_id,
            bank_account_id=transaction_create.bank_account_id,
            amount=transaction_create.amount,
            description=transaction_create.description,
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction

    def get_by_id(self, user_id: UUID, transaction_id: UUID) -> Optional[Transaction]:
        """Get a transaction by ID, ensuring it belongs to the user."""
        transaction = (
            self.db.query(Transaction)
            .filter(Transaction.id == transaction_id, Transaction.user_id == user_id)
            .first()
        )
        return transaction

    def get_multi(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        bank_account_id: Optional[UUID] = None,
    ) -> tuple[list[Transaction], int]:
        """Get multiple transactions with pagination."""
        conditions = [Transaction.user_id == user_id]

        if bank_account_id:
            conditions.append(Transaction.bank_account_id == bank_account_id)

        # Count total matching transactions
        count_query = (
            select(func.count())  # pylint: disable=not-callable
            .select_from(Transaction)
            .where(and_(*conditions))
        )
        total = self.db.scalar(count_query) or 0

        # Get paginated transactions
        query = (
            select(Transaction)
            .where(and_(*conditions))
            .offset(skip)
            .limit(limit)
            .order_by(Transaction.created_at.desc())
        )
        transactions = list(self.db.scalars(query).all())

        return transactions, total

    def update(
        self,
        user_id: UUID,
        transaction_id: UUID,
        transaction_update: TransactionUpdate,
    ) -> Optional[Transaction]:
        """Update a transaction."""
        transaction = self.get_by_id(user_id, transaction_id)
        if not transaction:
            return None

        update_data = transaction_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, user_id: UUID, transaction_id: UUID) -> bool:
        """Delete a transaction."""
        transaction = self.get_by_id(user_id, transaction_id)
        if not transaction:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True
