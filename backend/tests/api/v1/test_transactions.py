import uuid
from decimal import Decimal
from typing import Any

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.domain.models import BankAccount, Transaction


@pytest.fixture
def test_bank_account(db: Session, test_user: Any) -> BankAccount:
    bank_account = BankAccount(
        user_id=test_user.id,
        account_type="checking",
        account_name="Test Account",
        account_identifier="123456789",
        is_active=True,
    )
    db.add(bank_account)
    db.commit()
    db.refresh(bank_account)
    return bank_account


@pytest.fixture
def test_transaction(
    db: Session, test_user: Any, test_bank_account: BankAccount
) -> Transaction:
    transaction = Transaction(
        user_id=test_user.id,
        bank_account_id=test_bank_account.id,
        amount=Decimal("100.50"),
        description="Test transaction",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@pytest.fixture
def user_token_headers(test_user: Any) -> dict[str, str]:
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


def test_create_transaction(
    client: Any,
    test_bank_account: BankAccount,
    user_token_headers: dict[str, str],
) -> None:
    transaction_data = {
        "bank_account_id": str(test_bank_account.id),
        "amount": 150.75,
        "description": "New test transaction",
    }

    response = client.post(
        "/api/v1/transactions",
        json=transaction_data,
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == "150.75"
    assert data["description"] == "New test transaction"
    assert data["bank_account_id"] == str(test_bank_account.id)
    assert "id" in data
    assert "created_at" in data


def test_create_transaction_invalid_bank_account(
    client: Any,
    user_token_headers: dict[str, str],
) -> None:
    transaction_data = {
        "bank_account_id": str(uuid.uuid4()),  # Random non-existent bank account
        "amount": 150.75,
        "description": "New test transaction",
    }

    response = client.post(
        "/api/v1/transactions",
        json=transaction_data,
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_transaction(
    client: Any,
    test_transaction: Transaction,
    user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"/api/v1/transactions/{test_transaction.id}",
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_transaction.id)
    assert data["amount"] == str(test_transaction.amount)
    assert data["description"] == test_transaction.description


def test_get_non_existent_transaction(
    client: Any,
    user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"/api/v1/transactions/{uuid.uuid4()}",
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_transactions(
    client: Any,
    test_transaction: Transaction,
    user_token_headers: dict[str, str],
) -> None:
    response = client.get("/api/v1/transactions", headers=user_token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(test_transaction.id)


def test_list_transactions_with_pagination(
    client: Any,
    db: Session,
    test_user: Any,
    test_bank_account: BankAccount,
    user_token_headers: dict[str, str],
) -> None:
    # Create 15 transactions
    for i in range(15):
        transaction = Transaction(
            user_id=test_user.id,
            bank_account_id=test_bank_account.id,
            amount=Decimal(f"{100 + i}.00"),
            description=f"Transaction {i}",
        )
        db.add(transaction)
    db.commit()

    # Test first page
    response = client.get(
        "/api/v1/transactions?skip=0&limit=10",
        headers=user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 15
    assert len(data["items"]) == 10

    # Test second page
    response = client.get(
        "/api/v1/transactions?skip=10&limit=10",
        headers=user_token_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 15
    assert len(data["items"]) == 5


def test_list_transactions_by_bank_account(
    client: Any,
    test_transaction: Transaction,
    test_bank_account: BankAccount,
    user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"/api/v1/transactions?bank_account_id={test_bank_account.id}",
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["bank_account_id"] == str(test_bank_account.id)


def test_update_transaction(
    client: Any,
    test_transaction: Transaction,
    user_token_headers: dict[str, str],
) -> None:
    update_data = {
        "amount": 200.25,
        "description": "Updated transaction",
    }

    response = client.put(
        f"/api/v1/transactions/{test_transaction.id}",
        json=update_data,
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_transaction.id)
    assert data["amount"] == "200.25"
    assert data["description"] == "Updated transaction"


def test_delete_transaction(
    client: Any,
    test_transaction: Transaction,
    user_token_headers: dict[str, str],
) -> None:
    response = client.delete(
        f"/api/v1/transactions/{test_transaction.id}",
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify transaction is deleted
    response = client.get(
        f"/api/v1/transactions/{test_transaction.id}",
        headers=user_token_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
