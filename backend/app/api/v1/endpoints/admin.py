# app/api/v1/endpoints/admin.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.config import get_settings
from app.services.db_reset_service import DBResetService

SETTINGS = get_settings()
router = APIRouter()


@router.post("/reset-database", status_code=status.HTTP_200_OK)
def reset_database(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """
    Reset the database by clearing all data.
    Only available in development/test environment.
    """
    if SETTINGS.ENVIRONMENT not in ["development", "test"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Database reset not allowed in this environment",
        )

    try:
        db_reset_service = DBResetService(db, SETTINGS)
        db_reset_service.reset_database()
        return {"message": "Database reset successful"}
    except ValueError as e:
        if "only allowed in development or test environment" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database reset failed: {str(e)}",
        ) from e
