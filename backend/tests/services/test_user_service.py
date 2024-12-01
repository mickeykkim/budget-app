from app.schemas.user import UserCreate
from app.services.user_service import UserService


def test_create_user(db):
    user_service = UserService(db)
    user_data = UserCreate(email="newuser@example.com", password="password123")
    user = user_service.create(user_data)
    assert user.email == "newuser@example.com"
    assert hasattr(user, "hashed_password")
    assert user.hashed_password != "password123"


def test_authenticate_user(db, test_user):
    user_service = UserService(db)
    authenticated_user = user_service.authenticate(
        email="test@example.com", password="testpassword123"
    )
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email


def test_authenticate_user_invalid_password(db, test_user):
    user_service = UserService(db)
    authenticated_user = user_service.authenticate(
        email="test@example.com", password="wrongpassword"
    )
    assert authenticated_user is None


def test_get_user_by_email(db, test_user):
    user_service = UserService(db)
    user = user_service.get_by_email("test@example.com")
    assert user is not None
    assert user.email == test_user.email
