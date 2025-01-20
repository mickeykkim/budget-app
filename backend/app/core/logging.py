"""
Logging module
"""

import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, AsyncGenerator, Callable, Optional, TypeVar, Union, cast
from uuid import UUID, uuid4

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from structlog.types import EventDict, Processor
from structlog.typing import WrappedLogger

# Configure standard logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Type aliases for clarity
JsonDict = dict[str, Union[str, int, float, bool, None, "JsonDict", list[Any]]]
QueryParams = dict[str, str]
FilteredDict = dict[str, Any]

# Sensitive fields that should be filtered in logs
SENSITIVE_FIELDS = {
    # Authentication & Security
    "password",
    "password_confirmation",
    "old_password",
    "new_password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "key",
    "authorization",
    # Personal Information
    "ssn",
    "social_security",
    "credit_card",
    "card_number",
    "cvv",
    "pin",
    # Financial
    "account_number",
    "routing_number",
    "sort_code",
    "iban",
    "bic",
    # OAuth & Session
    "state",
    "code",
    "session",
    "csrf",
}

# Type variable for the decorator
F = TypeVar("F", bound=Callable[..., Any])


def serialize_uuid(
    _logger: WrappedLogger, _name: str, event_dict: EventDict
) -> EventDict:
    """Custom processor to handle UUID serialization."""
    for key, value in event_dict.items():
        if isinstance(value, UUID):
            event_dict[key] = str(value)
    return event_dict


# Configure structlog
processors: list[Processor] = [
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.contextvars.merge_contextvars,
    cast(Processor, serialize_uuid),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    structlog.processors.JSONRenderer(serializer=json.dumps),
]

structlog.configure(
    processors=processors,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Create a logger instance with explicit type
logger = structlog.get_logger()
Logger = structlog.stdlib.BoundLogger


class RequestResponseLogger:
    """Handles request and response logging logic."""

    def __init__(self) -> None:
        self.logger: Logger = logger
        self.start_time: datetime = datetime.now(UTC)
        self.request_id: str = ""

    def get_filtered_query_params(self, request: Request) -> Optional[FilteredDict]:
        """Extract and filter query parameters."""
        query_params = dict(request.query_params.items())
        if not query_params:
            return None

        # Convert query params to the correct type for filtering
        typed_params: JsonDict = dict(query_params.items())
        return cast(FilteredDict, filter_sensitive_data(typed_params))

    def create_log_context(
        self,
        request: Request,
        query_params: Optional[FilteredDict],
    ) -> FilteredDict:
        """Create the base log context from request data."""
        return {
            "request_id": self.request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": query_params,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
        }

    async def extract_response_body(self, response: Response) -> Optional[FilteredDict]:
        """Extract and filter response body if present."""
        if response.status_code == 204:
            return None

        try:
            if hasattr(response, "body"):
                body = response.body
                if isinstance(body, bytes):
                    response_dict = json.loads(body.decode())
                    if isinstance(response_dict, dict):
                        return cast(
                            FilteredDict,
                            filter_sensitive_data(cast(JsonDict, response_dict)),
                        )
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            pass
        return None

    def log_request(
        self,
        log_context: FilteredDict,
        response: Response,
        response_body: Optional[FilteredDict],
    ) -> None:
        """Log the end of request processing."""
        duration = (datetime.now(UTC) - self.start_time).total_seconds()
        bound_logger = self.logger.bind(**log_context)
        bound_logger.info(
            "request_complete",
            status_code=response.status_code,
            duration=duration,
            response_body=response_body,
        )

    def log_request_error(self, log_context: FilteredDict, error: Exception) -> None:
        """Log request processing errors."""
        duration = (datetime.now(UTC) - self.start_time).total_seconds()
        bound_logger = self.logger.bind(**log_context)
        bound_logger.error(
            "request_failed",
            error=str(error),
            error_type=type(error).__name__,
            duration=duration,
            traceback=True,
        )


def filter_sensitive_data(
    data: JsonDict | list[Any], replacement: str = "[FILTERED]"
) -> FilteredDict | list[Any]:
    """
    Recursively filter sensitive data in a dictionary or list.
    Returns a filtered copy of the input data structure.
    """
    if isinstance(data, dict):
        filtered: FilteredDict = {}
        for key, value in data.items():
            # Check if the key contains any sensitive field names
            is_sensitive = any(
                sensitive_field in key.lower() for sensitive_field in SENSITIVE_FIELDS
            )

            if is_sensitive:
                filtered[key] = replacement
            elif isinstance(value, (dict, list)):
                filtered[key] = filter_sensitive_data(
                    cast(Union[JsonDict, list[Any]], value)
                )
            else:
                filtered[key] = value
        return filtered
    if isinstance(data, list):
        return [
            (
                filter_sensitive_data(cast(JsonDict, item))
                if isinstance(item, dict)
                else item
            )
            for item in data
        ]
    return cast(list[Any], data)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured logging middleware for FastAPI; wraps dispatch calls with logging
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response_logger = RequestResponseLogger()
        response_logger.request_id = request.headers.get("X-Request-ID", str(uuid4()))

        # Process request data
        query_params = response_logger.get_filtered_query_params(request)
        log_context = response_logger.create_log_context(request, query_params)

        try:
            # Process request
            response = await call_next(request)

            # Extract and log response
            response_body = await response_logger.extract_response_body(response)
            response_logger.log_request(log_context, response, response_body)

            # Add request ID to response
            response.headers["X-Request-ID"] = response_logger.request_id
            return response

        except Exception as e:
            response_logger.log_request_error(log_context, e)
            raise


@asynccontextmanager
async def logging_lifespan(_app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Lifespan context manager for logging"""
    # Startup event
    logger.info("application_startup", status="starting")
    yield
    # Shutdown event
    logger.info("application_shutdown", status="shutting_down")


def log_service_call(service_logger: Logger = logger) -> Callable[[F], F]:
    """Decorator for logging service method calls."""

    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            service_name = func.__module__.split(".")[-1]
            method_name = func.__name__

            bound_logger = service_logger.bind(
                service=service_name,
                method=method_name,
            )

            try:
                bound_logger.info("service_call_started")
                result = func(*args, **kwargs)
                bound_logger.info("service_call_completed")
                return result
            except Exception as e:
                bound_logger.error(
                    "service_call_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        return cast(F, wrapper)

    return decorator
