"""
Service for User model
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import logger
from app.core.security import get_password_hash, verify_password
from app.models.domain.models import BankAccount, Transaction, User
from app.schemas.user import UserCreate

settings = get_settings()


class UserService:
    """Service for User model"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get a user by id"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_in: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            email=user_in.email, hashed_password=get_password_hash(user_in.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(
            password, str(user.hashed_password)
        ):  # Convert to str explicitly
            return None
        return user

    def delete(self, user_id: UUID) -> bool:
        """
        Hard delete a user and all associated data.

        Cascades deletion to:
        - Transactions
        - Bank Accounts
        - User
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        try:
            # Delete all transactions associated with the user
            self.db.query(Transaction).filter(Transaction.user_id == user_id).delete()

            # Delete all bank accounts associated with the user
            self.db.query(BankAccount).filter(BankAccount.user_id == user_id).delete()

            # Delete the user
            self.db.delete(user)
            self.db.commit()
            return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            self.db.rollback()
            logger.error(f"Error deleting user: {e}")
            return False
