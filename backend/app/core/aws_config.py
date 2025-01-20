"""
Config for AWS services
"""

from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings


class AWSConfig:
    """Config for AWS services"""
    def __init__(self, settings: Settings | None = None):
        if not settings:
            settings = get_settings()
        self.settings = settings
        self.ssm_client = boto3.client(
            "ssm",
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL,
        )

    def get_parameters(self, path: str = "/budget-app/") -> dict[str, Any]:
        """Retrieve parameters from AWS Parameter Store"""
        try:
            response = self.ssm_client.get_parameters_by_path(
                Path=path, Recursive=True, WithDecryption=True
            )
            return {
                param["Name"].split("/")[-1]: param["Value"]
                for param in response["Parameters"]
            }
        except ClientError as e:
            print(f"Error fetching parameters: {e}")
            return {}
