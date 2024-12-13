from typing import Annotated, Generator
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.schemas.user import UserInDB
from app.services.user_service import UserService

SETTINGS = get_settings()
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=f"{SETTINGS.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: Annotated[str, Depends(OAUTH2_SCHEME)],
    db: Annotated[Session, Depends(get_db)],
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SETTINGS.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError as e:
        raise credentials_exception from e
    except jwt.PyJWTError as e:
        raise credentials_exception from e

    user_service = UserService(db)
    user = user_service.get_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    return UserInDB.model_validate(user)
