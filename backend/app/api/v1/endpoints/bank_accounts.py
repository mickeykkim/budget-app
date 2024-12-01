from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.schemas.bank_account import (
    BankAccountCreate,
    BankAccountList,
    BankAccountRead,
    BankAccountUpdate,
)
from app.schemas.user import UserInDB
from app.services.bank_account_service import BankAccountService

router = APIRouter()


@router.post("", response_model=BankAccountRead)
def create_bank_account(
    bank_account_create: BankAccountCreate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BankAccountRead:
    """Create a new bank account."""
    bank_account_service = BankAccountService(db)
    bank_account = bank_account_service.create(current_user.id, bank_account_create)
    return BankAccountRead.model_validate(bank_account)


@router.get("", response_model=BankAccountList)
def list_bank_accounts(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_inactive: bool = Query(False, description="Include inactive accounts"),
) -> BankAccountList:
    """List bank accounts with pagination."""
    bank_account_service = BankAccountService(db)
    bank_accounts, total = bank_account_service.get_multi(
        current_user.id,
        skip=skip,
        limit=limit,
        include_inactive=include_inactive,
    )
    return BankAccountList(
        items=[BankAccountRead.model_validate(ba) for ba in bank_accounts],
        total=total,
    )


@router.get("/{bank_account_id}", response_model=BankAccountRead)
def get_bank_account(
    bank_account_id: UUID,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BankAccountRead:
    """Get a specific bank account."""
    bank_account_service = BankAccountService(db)
    bank_account = bank_account_service.get_by_id(current_user.id, bank_account_id)
    if not bank_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found",
        )
    return BankAccountRead.model_validate(bank_account)


@router.put("/{bank_account_id}", response_model=BankAccountRead)
def update_bank_account(
    bank_account_id: UUID,
    bank_account_update: BankAccountUpdate,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> BankAccountRead:
    """Update a bank account."""
    bank_account_service = BankAccountService(db)
    bank_account = bank_account_service.update(
        current_user.id, bank_account_id, bank_account_update
    )
    if not bank_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found",
        )
    return BankAccountRead.model_validate(bank_account)


@router.delete("/{bank_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank_account(
    bank_account_id: UUID,
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Soft delete a bank account."""
    bank_account_service = BankAccountService(db)
    if not bank_account_service.delete(current_user.id, bank_account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found",
        )
