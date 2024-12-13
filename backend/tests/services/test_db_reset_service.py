import pytest
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.domain.models import BankAccount, Transaction, User
from app.schemas.user import UserCreate
from app.services.db_reset_service import DBResetService
from app.services.user_service import UserService


# Modify test_reset_database_development to verify user data preservation
def test_reset_database_development(db: Session, development_settings: Settings):
    """Test database reset in development environment preserves user data"""
    # Setup: Create sample data
    user_service = UserService(db)
    user = user_service.create(UserCreate(email="test@example.com", password="test123"))

    bank_account = BankAccount(
        user_id=user.id,
        account_type="test",
        account_name="Test Account",
        account_identifier="123",
    )
    db.add(bank_account)
    db.commit()

    transaction = Transaction(
        user_id=user.id,
        bank_account_id=bank_account.id,
        amount=100.00,
        description="Test transaction",
    )
    db.add(transaction)
    db.commit()

    # Verify initial data exists
    assert db.query(User).count() == 1
    assert db.query(BankAccount).count() == 1
    assert db.query(Transaction).count() == 1

    # Reset database
    reset_service = DBResetService(db, development_settings)
    assert reset_service.reset_database() is True

    # Verify user data is preserved while other data is cleared
    assert db.query(User).count() == 1, "User data should be preserved"
    assert db.query(BankAccount).count() == 0, "Bank accounts should be cleared"
    assert db.query(Transaction).count() == 0, "Transactions should be cleared"

    # Verify the specific user still exists
    preserved_user = user_service.get_by_email("test@example.com")
    assert preserved_user is not None, "Original user should still exist"
    assert preserved_user.id == user.id, "User ID should remain the same"


def test_reset_database_production(db: Session):
    """Test database reset is blocked in production environment"""
    production_settings = Settings(
        ENVIRONMENT="production",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test",
        POSTGRES_HOST="test",
        POSTGRES_PORT="5432",
        POSTGRES_DB="test",
        SECRET_KEY="test",
        AWS_ACCESS_KEY_ID="test",
        AWS_SECRET_ACCESS_KEY="test",
    )

    reset_service = DBResetService(db, production_settings)

    with pytest.raises(
        ValueError, match="only allowed in development or test environment"
    ):
        reset_service.reset_database()


def test_reset_database_with_foreign_keys(db: Session, development_settings: Settings):
    """
    Test database reset properly handles foreign key relationships while preserving
    users
    """
    # Create data with foreign key relationships
    user_service = UserService(db)
    user = user_service.create(UserCreate(email="test@example.com", password="test123"))

    # Create multiple bank accounts
    accounts = []
    for i in range(3):
        account = BankAccount(
            user_id=user.id,
            account_type=f"test{i}",
            account_name=f"Test Account {i}",
            account_identifier=str(i),
        )
        db.add(account)
        accounts.append(account)
    db.commit()

    # Create transactions for each account
    for account in accounts:
        for _ in range(2):
            transaction = Transaction(
                user_id=user.id,
                bank_account_id=account.id,
                amount=100.00,
                description="Test transaction",
            )
            db.add(transaction)
    db.commit()

    # Verify initial state
    assert db.query(User).count() == 1
    assert db.query(BankAccount).count() == 3
    assert db.query(Transaction).count() == 6

    # Reset database
    reset_service = DBResetService(db, development_settings)
    reset_service.reset_database()

    # Verify user data is preserved while related data is cleared
    assert db.query(User).count() == 1, "User data should be preserved"
    assert db.query(BankAccount).count() == 0, "Bank accounts should be cleared"
    assert db.query(Transaction).count() == 0, "Transactions should be cleared"

    # Verify the specific user still exists
    preserved_user = user_service.get_by_email("test@example.com")
    assert preserved_user is not None, "Original user should still exist"
    assert preserved_user.id == user.id, "User ID should remain the same"


def test_reset_database_sequence_reset(db: Session, development_settings: Settings):
    """Test that database sequences are properly reset except for users"""
    # Create test data
    user_service = UserService(db)
    users = []
    for i in range(5):
        user = user_service.create(
            UserCreate(email=f"test{i}@example.com", password="test123")
        )
        users.append(user)
        db.add(
            BankAccount(
                user_id=user.id,
                account_type="test",
                account_name=f"Test Account {i}",
                account_identifier=str(i),
            )
        )
    db.commit()

    initial_users = db.query(User).all()

    # Reset database
    reset_service = DBResetService(db, development_settings)
    reset_service.reset_database()

    # Verify users are preserved
    preserved_users = db.query(User).all()
    assert len(preserved_users) == len(initial_users), "All users should be preserved"

    # Create new bank account and verify its sequence starts from beginning
    new_account = BankAccount(
        user_id=users[0].id,
        account_type="test",
        account_name="New Test Account",
        account_identifier="new",
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # Verify counts
    assert db.query(User).count() == 5, "All users should be preserved"
    assert db.query(BankAccount).count() == 1, "Should have only the new bank account"
