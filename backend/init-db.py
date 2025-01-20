#!/usr/bin/env python3

import sys
from datetime import datetime, timedelta
from decimal import Decimal

import sqlalchemy
from sqlalchemy import MetaData, and_, create_engine, inspect, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists, drop_database

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, get_engine
from app.models.domain.models import Transaction
from app.schemas.bank_account import BankAccountCreate
from app.schemas.user import UserCreate
from app.services.bank_account_service import BankAccountService
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService

settings = get_settings()

# Test data configuration
TEST_USERS = [
    UserCreate(email="test@example.com", password="testpassword123"),
    UserCreate(email="mickey@example.com", password="mickeypass123"),
    UserCreate(email="alison@example.com", password="alisonpass123"),
]

ACCOUNT_TEMPLATES = [
    {
        "account_type": "checking",
        "account_name": "Main Checking",
        "account_identifier": "****1234",
        "access_token": "dummy_token_checking",
        "refresh_token": "dummy_refresh_checking",
        "institution_name": "Test Bank",
    },
    {
        "account_type": "savings",
        "account_name": "Emergency Fund",
        "account_identifier": "****5678",
        "access_token": "dummy_token_savings",
        "refresh_token": "dummy_refresh_savings",
        "institution_name": "Test Bank",
    },
    {
        "account_type": "credit",
        "account_name": "Credit Card",
        "account_identifier": "****9012",
        "access_token": "dummy_token_credit",
        "refresh_token": "dummy_refresh_credit",
        "institution_name": "Test Bank",
    },
]

CHECKING_TRANSACTIONS = [
    {"description": "Rent Payment - Housing", "amount": Decimal("-1500.00"), "day": 1},
    {
        "description": "Electric Bill - Utilities",
        "amount": Decimal("-120.00"),
        "day": 5,
    },
    {
        "description": "Internet Service - Utilities",
        "amount": Decimal("-80.00"),
        "day": 7,
    },
    {"description": "Phone Bill - Utilities", "amount": Decimal("-70.00"), "day": 10},
    {"description": "Salary Deposit - Income", "amount": Decimal("3500.00"), "day": 1},
    {
        "description": "Car Insurance - Transportation",
        "amount": Decimal("-100.00"),
        "day": 25,
    },
]

SAVINGS_TRANSACTIONS = [
    {"description": "Emergency Fund Transfer", "amount": Decimal("-500.00"), "day": 15},
    {"description": "Medical Bill Payment", "amount": Decimal("-1000.00"), "day": 20},
    {
        "description": "Investment Dividend - Income",
        "amount": Decimal("150.00"),
        "day": 15,
    },
    {"description": "Quarterly Bonus Deposit", "amount": Decimal("1000.00"), "day": 1},
]

CREDIT_TRANSACTIONS = [
    {
        "description": "Grocery Store - Food & Dining",
        "amount": Decimal("-200.00"),
        "day": 15,
    },
    {"description": "Gym Membership - Health", "amount": Decimal("-50.00"), "day": 20},
    {
        "description": "Streaming Service - Entertainment",
        "amount": Decimal("-15.00"),
        "day": 22,
    },
    {"description": "Online Shopping - Retail", "amount": Decimal("-150.00"), "day": 8},
    {
        "description": "Restaurant Dinner - Food & Dining",
        "amount": Decimal("-80.00"),
        "day": 12,
    },
    {
        "description": "Gas Station - Transportation",
        "amount": Decimal("-40.00"),
        "day": 18,
    },
]

ACCOUNT_TRANSACTIONS = {
    "checking": CHECKING_TRANSACTIONS,
    "savings": SAVINGS_TRANSACTIONS,
    "credit": CREDIT_TRANSACTIONS,
}


def reset_database():
    """Reset the database by dropping and recreating it"""
    print("\nResetting database...")
    engine = get_engine()

    try:
        # Close all connections
        engine.dispose()

        # Construct database URL for postgres database
        postgres_url = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
        )

        # Create a new engine specifically for the postgres database
        temp_engine = create_engine(postgres_url)

        database_url = (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

        with temp_engine.connect() as conn:
            # Terminate existing connections
            conn.execute(
                text(
                    """
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = :database
                    AND pid <> pg_backend_pid()
                    """
                ),
                {"database": settings.POSTGRES_DB},
            )
            conn.commit()

        # Drop and recreate database
        if database_exists(database_url):
            print("Dropping existing database...")
            drop_database(database_url)
        print("Creating new database...")
        create_database(database_url)

        # Clean up connections
        temp_engine.dispose()

        print("Database recreated successfully")
        return True

    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        return False


def run_migrations():
    """Run database migrations using Alembic"""
    try:
        print("Running database migrations...")
        # Create a fresh alembic config
        alembic_cfg = Config("alembic.ini")

        # Make sure we're starting from a clean state
        command.downgrade(alembic_cfg, "base")

        # Now run all upgrades
        command.upgrade(alembic_cfg, "head")

        print("Migrations completed successfully")
        return True
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False


def get_transaction_key(transaction, account_id, date):
    """Create a unique key for a transaction to check existence"""
    return f"{account_id}_{date.strftime('%Y-%m-%d')}_{transaction['description']}_{transaction['amount']}"


def create_test_data():
    """Create deterministic test users, bank accounts, and transactions"""
    print("\nStarting test data creation...")
    db = SessionLocal()

    try:
        # Initialize services
        user_service = UserService(db)
        bank_account_service = BankAccountService(db)
        transaction_service = TransactionService(db)

        created_users = []
        # Create test users if they don't exist
        for user_data in TEST_USERS:
            existing_user = user_service.get_by_email(user_data.email)
            if not existing_user:
                user = user_service.create(user_data)
                print(f"Created new user: {user_data.email}")
            else:
                user = existing_user
                print(f"Using existing user: {user_data.email}")
            created_users.append(user)

        # Process each user
        for user in created_users:
            print(f"\nProcessing accounts and transactions for user: {user.email}")

            # Get existing accounts for the user
            existing_accounts, _ = bank_account_service.get_multi(
                user.id, skip=0, limit=100, include_inactive=True
            )
            existing_accounts_map = {
                (acc.account_type, acc.account_name): acc for acc in existing_accounts
            }

            # Create missing accounts
            for account_template in ACCOUNT_TEMPLATES:
                account_key = (
                    account_template["account_type"],
                    account_template["account_name"],
                )

                if account_key not in existing_accounts_map:
                    account_data = {
                        **account_template,
                        "token_expires_at": datetime.now() + timedelta(days=30),
                    }
                    account = bank_account_service.create(
                        user.id, BankAccountCreate(**account_data)
                    )
                    print(f"Created new account: {account.account_name}")
                    existing_accounts_map[account_key] = account
                else:
                    print(f"Using existing account: {account_key[1]}")

            # Process transactions for each account
            for account_key, account in existing_accounts_map.items():
                print(f"\nProcessing transactions for account: {account.account_name}")

                # Get existing transactions
                existing_transactions, _ = transaction_service.get_multi(
                    user_id=user.id, bank_account_id=account.id, skip=0, limit=1000
                )

                # Create set of existing transaction keys
                existing_transaction_keys = {
                    get_transaction_key(
                        {"description": t.description, "amount": t.amount},
                        t.bank_account_id,
                        t.created_at,
                    )
                    for t in existing_transactions
                }

                # Get transaction template for account type
                transactions_template = ACCOUNT_TRANSACTIONS.get(
                    account.account_type, []
                )

                # Create 3 months of transactions
                start_date = datetime.now().replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

                for month in range(3):
                    current_date = start_date - timedelta(days=30 * month)

                    for transaction in transactions_template:
                        # Set transaction date
                        transaction_date = current_date.replace(day=transaction["day"])

                        # Check for existing transaction
                        transaction_key = get_transaction_key(
                            transaction, account.id, transaction_date
                        )

                        if transaction_key not in existing_transaction_keys:
                            new_transaction = Transaction(
                                user_id=user.id,
                                bank_account_id=account.id,
                                amount=transaction["amount"],
                                description=transaction["description"],
                                created_at=transaction_date,
                            )

                            db.add(new_transaction)
                            db.commit()
                            db.refresh(new_transaction)

                            print(
                                f"Created new transaction: {transaction['description']}"
                                f" on {transaction_date.date()}"
                            )
                        else:
                            print(
                                f"Skipping existing transaction: {transaction['description']}"
                                f" on {transaction_date.date()}"
                            )

        print("\nTest data creation completed successfully")
        return True

    except SQLAlchemyError as e:
        print(f"\nDatabase error during test data creation: {str(e)}")
        db.rollback()
        return False
    except Exception as e:
        print(f"\nUnexpected error during test data creation: {str(e)}")
        db.rollback()
        return False
    finally:
        print("\nClosing database connection...")
        db.close()


def main():
    """Main initialization sequence"""
    print("Starting database initialization...")

    try:
        if not reset_database():
            print("Database reset failed")
            sys.exit(1)

        if not run_migrations():
            print("Database initialization failed at migrations step")
            sys.exit(1)

        if not create_test_data():
            print("Database initialization failed at test data creation step")
            sys.exit(1)

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"Initialization failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
