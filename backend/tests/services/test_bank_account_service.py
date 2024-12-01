from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.schemas.bank_account import BankAccountCreate, BankAccountUpdate
from app.services.bank_account_service import BankAccountService
from app.services.bank_api.base import TokenRefreshError


def test_create_bank_account(db: Session, test_user):
    service = BankAccountService(db)
    account_data = BankAccountCreate(
        account_type="monzo",
        account_name="My Checking",
        account_identifier="5678",
        access_token="access_123",
        refresh_token="refresh_123",
        token_expires_at=datetime.utcnow() + timedelta(hours=1),
    )

    account = service.create(test_user.id, account_data)
    assert account.account_name == "My Checking"
    assert account.account_type == "monzo"
    assert account.user_id == test_user.id
    assert account.is_active is True


def test_get_bank_account(db: Session, test_user, test_bank_account):
    service = BankAccountService(db)
    retrieved_account = service.get_by_id(test_user.id, test_bank_account.id)
    assert retrieved_account is not None
    assert retrieved_account.id == test_bank_account.id


def test_get_bank_account_wrong_user(db: Session, test_bank_account):
    service = BankAccountService(db)
    wrong_user_id = uuid4()
    retrieved_account = service.get_by_id(wrong_user_id, test_bank_account.id)
    assert retrieved_account is None


def test_get_multi_bank_accounts(db: Session, test_user, test_bank_account):
    # Create another bank account
    service = BankAccountService(db)
    account_data = BankAccountCreate(
        account_type="truelayer",
        account_name="My Savings",
        account_identifier="9012",
        access_token="access_456",
        refresh_token="refresh_456",
        token_expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    service.create(test_user.id, account_data)

    # Test pagination
    accounts, total = service.get_multi(test_user.id, skip=0, limit=10)
    assert total == 2
    assert len(accounts) == 2


def test_get_multi_bank_accounts_pagination(db: Session, test_user, test_bank_account):
    service = BankAccountService(db)

    # Create 5 more accounts
    for i in range(5):
        account_data = BankAccountCreate(
            account_type="monzo",
            account_name=f"Account {i}",
            account_identifier=str(i),
            access_token=f"access_{i}",
            refresh_token=f"refresh_{i}",
            token_expires_at=datetime.utcnow() + timedelta(hours=1),
        )
        service.create(test_user.id, account_data)

    # Test first page
    accounts, total = service.get_multi(test_user.id, skip=0, limit=3)
    assert total == 6  # 5 new + 1 from fixture
    assert len(accounts) == 3

    # Test second page
    accounts, total = service.get_multi(test_user.id, skip=3, limit=3)
    assert total == 6
    assert len(accounts) == 3


def test_update_bank_account(db: Session, test_user, test_bank_account):
    service = BankAccountService(db)
    update_data = BankAccountUpdate(
        account_name="Updated Account Name", access_token="new_access_token"
    )

    updated_account = service.update(test_user.id, test_bank_account.id, update_data)
    assert updated_account is not None
    assert updated_account.account_name == "Updated Account Name"
    assert updated_account.access_token == "new_access_token"


def test_delete_bank_account(db: Session, test_user, test_bank_account):
    service = BankAccountService(db)
    assert service.delete(test_user.id, test_bank_account.id) is True

    # Verify account is marked as inactive
    account = service.get_by_id(test_user.id, test_bank_account.id)
    assert account is not None
    assert account.is_active is False


def test_refresh_token_success(db: Session, test_bank_account, mock_bank_api, mocker):
    mocker.patch(
        "app.services.bank_account_service.get_bank_api", return_value=mock_bank_api
    )
    service = BankAccountService(db)

    updated_account = service.refresh_token(test_bank_account.id)
    assert updated_account is not None
    assert updated_account.access_token == "new_access_token"
    assert updated_account.refresh_token == "new_refresh_token"


def test_refresh_token_failure(db: Session, test_bank_account, mock_bank_api, mocker):
    mock_bank_api.refresh_token.side_effect = TokenRefreshError(
        "Failed to refresh token"
    )
    mocker.patch(
        "app.services.bank_account_service.get_bank_api", return_value=mock_bank_api
    )
    service = BankAccountService(db)

    with pytest.raises(TokenRefreshError):
        service.refresh_token(test_bank_account.id)
