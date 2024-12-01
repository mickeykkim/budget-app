from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionList,
    TransactionRead,
    TransactionUpdate,
)
from app.schemas.user import UserInDB
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post("", response_model=TransactionRead)
def create_transaction(
    transaction_create: TransactionCreate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TransactionRead:
    """Create a new transaction."""
    transaction_service = TransactionService(db)
    transaction = transaction_service.create(current_user.id, transaction_create)
    return TransactionRead.model_validate(transaction)


@router.get("", response_model=TransactionList)
def list_transactions(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    bank_account_id: UUID | None = None,
) -> TransactionList:
    """List transactions with pagination."""
    transaction_service = TransactionService(db)
    transactions, total = transaction_service.get_multi(
        current_user.id, skip=skip, limit=limit, bank_account_id=bank_account_id
    )
    return TransactionList(
        items=[TransactionRead.model_validate(t) for t in transactions],
        total=total,
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: UUID,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TransactionRead:
    """Get a specific transaction."""
    transaction_service = TransactionService(db)
    transaction = transaction_service.get_by_id(current_user.id, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return TransactionRead.model_validate(transaction)


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TransactionRead:
    """Update a transaction."""
    transaction_service = TransactionService(db)
    transaction = transaction_service.update(
        current_user.id, transaction_id, transaction_update
    )
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return TransactionRead.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: UUID,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete a transaction."""
    transaction_service = TransactionService(db)
    if not transaction_service.delete(current_user.id, transaction_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
