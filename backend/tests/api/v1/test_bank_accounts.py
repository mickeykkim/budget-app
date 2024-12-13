from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import status


def test_create_bank_account(client, user_token_headers):
    account_data = {
        "account_type": "plaid",
        "account_name": "Test Account",
        "account_identifier": "1234",
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "token_expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }

    response = client.post(
        "/api/v1/bank-accounts", json=account_data, headers=user_token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["account_name"] == "Test Account"
    assert data["account_type"] == "plaid"
    assert "id" in data


def test_list_bank_accounts(client, test_bank_account, user_token_headers):
    response = client.get("/api/v1/bank-accounts", headers=user_token_headers)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(test_bank_account.id)


def test_list_bank_accounts_pagination(
    client, db, test_user, test_bank_account, user_token_headers
):
    # Create additional bank accounts
    from app.models.domain.models import BankAccount

    for i in range(5):
        account = BankAccount(
            user_id=test_user.id,
            account_type="plaid",
            account_name=f"Account {i}",
            account_identifier=str(i),
            access_token=f"access_{i}",
            refresh_token=f"refresh_{i}",
            token_expires_at=datetime.now(UTC) + timedelta(hours=1),
            is_active=True,
        )
        db.add(account)
    db.commit()

    # Test first page
    response = client.get(
        "/api/v1/bank-accounts?skip=0&limit=3", headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 6
    assert len(data["items"]) == 3

    # Test second page
    response = client.get(
        "/api/v1/bank-accounts?skip=3&limit=3", headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 6
    assert len(data["items"]) == 3


def test_get_bank_account(client, test_bank_account, user_token_headers):
    response = client.get(
        f"/api/v1/bank-accounts/{test_bank_account.id}", headers=user_token_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_bank_account.id)
    assert data["account_name"] == test_bank_account.account_name


def test_get_nonexistent_bank_account(client, user_token_headers):
    response = client.get(
        f"/api/v1/bank-accounts/{uuid4()}", headers=user_token_headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_bank_account(client, test_bank_account, user_token_headers):
    update_data = {"account_name": "Updated Account Name"}

    response = client.put(
        f"/api/v1/bank-accounts/{test_bank_account.id}",
        json=update_data,
        headers=user_token_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["account_name"] == "Updated Account Name"
    assert data["id"] == str(test_bank_account.id)


def test_delete_bank_account(client, test_bank_account, user_token_headers):
    response = client.delete(
        f"/api/v1/bank-accounts/{test_bank_account.id}", headers=user_token_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify account is not returned in active accounts list
    response = client.get("/api/v1/bank-accounts", headers=user_token_headers)
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0


def test_unauthorized_access(client, test_bank_account):
    # Try without authentication
    response = client.get("/api/v1/bank-accounts")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Try with invalid token
    response = client.get(
        "/api/v1/bank-accounts", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_access_other_user_account(client, test_bank_account, test_user):
    # Create a new valid user and get their token
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "other@example.com", "password": "password123"},
    )
    assert response.status_code == 200

    # Login with the new user
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "other@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Try to access the first user's bank account with the new user's token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        f"/api/v1/bank-accounts/{test_bank_account.id}", headers=headers
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
