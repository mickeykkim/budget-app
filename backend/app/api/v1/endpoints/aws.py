# app/api/v1/endpoints/aws.py
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

from app.core.config import get_settings

SETTINGS = get_settings()
router = APIRouter()


@router.get("/localstack-health")
async def get_localstack_health() -> Any:
    """Get LocalStack health status through backend proxy"""
    try:
        response = requests.get(
            f"{SETTINGS.AWS_ENDPOINT_URL}/_localstack/health", timeout=5  # Add timeout
        )
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"LocalStack service unavailable: {str(e)}"
        ) from e
