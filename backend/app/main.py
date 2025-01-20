"""
Main entrypoint into backend.
"""

from fastapi import FastAPI
from starlette.middleware import Middleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import StructuredLoggingMiddleware, logging_lifespan

settings = get_settings()


def create_application() -> FastAPI:
    """
    Create application with middleware already configured

    Returns:
        FastAPI: FastAPI application
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        middleware=[Middleware(StructuredLoggingMiddleware)],
        lifespan=logging_lifespan,
    )
    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application


app = create_application()
