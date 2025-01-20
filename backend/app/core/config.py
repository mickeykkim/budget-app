"""
Config for app
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Config for app"""
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Budget App"

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:  # pylint: disable=invalid-name
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # AWS Settings
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "eu-west-2"
    AWS_ENDPOINT_URL: Optional[str] = None

    # Monzo Settings
    MONZO_CLIENT_ID: Optional[str] = None
    MONZO_CLIENT_SECRET: Optional[str] = None
    MONZO_REDIRECT_URI: Optional[str] = None

    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Environment-specific settings
    ENVIRONMENT: str = "development"
    ENCRYPTION_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    @classmethod
    def from_aws(cls) -> "Settings":
        """Load settings from AWS Parameter Store in production"""
        if os.getenv("ENVIRONMENT") == "production":
            from app.core.aws_config import AWSConfig  # pylint: disable=cyclic-import

            aws_config = AWSConfig()
            params = aws_config.get_parameters()
            return cls(**params)
        return cls()


@lru_cache
def get_settings() -> Settings:
    return Settings()
