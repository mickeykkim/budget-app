import logging

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.core.logging import (
    RequestResponseLogger,
    filter_sensitive_data,
    log_service_call,
    logger,
)
from app.main import app


# Test Logger Configuration
def test_logger_configuration():
    """Test if the logger is correctly configured."""
    assert logger is not None
    assert logging.getLogger().level == logging.INFO


# Test RequestResponseLogger Class
def test_get_filtered_query_params():
    """Test filtering of query parameters."""
    logger = RequestResponseLogger()

    # Create a test client
    client = TestClient(app)

    # Make an actual request with query parameters
    client.get("/?username=test&password=secret_password")
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/",
            "query_string": b"username=test&password=secret_password",
            "headers": [],
        }
    )

    # Get filtered parameters
    filtered_params = logger.get_filtered_query_params(request)

    # Ensure sensitive data is filtered
    assert filtered_params["password"] == "[FILTERED]"
    assert filtered_params["username"] == "test"


def test_create_log_context():
    """Test creation of log context."""
    logger = RequestResponseLogger()

    # Create a proper request object
    request = Request(
        scope={"type": "http", "method": "GET", "path": "/", "headers": []}
    )

    log_context = logger.create_log_context(request, None)

    # Ensure that the log context contains request-related data
    assert log_context["method"] == "GET"
    assert "request_id" in log_context
    assert log_context["client_ip"] is None


def test_log_request(db, test_user, caplog):
    """Test logging of request completion."""
    logger = RequestResponseLogger()

    # Create a proper request object
    request = Request(
        scope={"type": "http", "method": "GET", "path": "/", "headers": []}
    )

    # Make an actual request
    client = TestClient(app)
    response = client.get("/")

    # Creating log context
    log_context = logger.create_log_context(request, None)

    # Log the request completion
    with caplog.at_level(logging.INFO):
        logger.log_request(log_context, response, None)
        assert "request_complete" in caplog.text
        assert str(response.status_code) in caplog.text


def test_log_request_error(db, test_user, caplog):
    """Test logging of request errors."""
    logger = RequestResponseLogger()

    # Create a proper request object
    request = Request(
        scope={"type": "http", "method": "GET", "path": "/", "headers": []}
    )

    # Simulate an error during request processing
    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("An error occurred")
        except ValueError as e:
            log_context = logger.create_log_context(request, None)
            logger.log_request_error(log_context, e)

        # Check captured logs for the error
        assert "request_failed" in caplog.text
        assert "ValueError" in caplog.text


# Test filter_sensitive_data Function
def test_filter_sensitive_data():
    """Test that sensitive fields are correctly filtered from a dictionary."""
    input_data = {
        "password": "secret",
        "user_info": {"ssn": "123-45-6789", "name": "John Doe"},
        "other_field": "value",
    }

    # Filter sensitive data
    filtered_data = filter_sensitive_data(input_data)

    # Assert that sensitive data is replaced with '[FILTERED]'
    assert filtered_data["password"] == "[FILTERED]"
    assert filtered_data["user_info"]["ssn"] == "[FILTERED]"
    assert filtered_data["other_field"] == "value"


# Test StructuredLoggingMiddleware
def test_structured_logging_middleware(client: TestClient, caplog):
    """Test that the middleware logs requests and responses."""
    with caplog.at_level(logging.INFO):
        response = client.get("/")

        # Ensure the response contains the expected header for request ID
        assert "X-Request-ID" in response.headers
        assert response.headers["X-Request-ID"] is not None

        # Check that logs include information about the request and response
        assert "request_complete" in caplog.text


# Test log_service_call Decorator
@log_service_call()
def some_service_function(a: int, b: int) -> int:
    return a + b


def test_log_service_call_success(caplog):
    """Test logging when service call succeeds."""
    with caplog.at_level(logging.INFO):
        result = some_service_function(1, 2)

        # Verify the result
        assert result == 3

        # Capture logs
        assert "service_call_started" in caplog.text
        assert "service_call_completed" in caplog.text


def test_log_service_call_failure(caplog):
    """Test logging when service call fails."""

    @log_service_call()
    def some_service_function_fail():
        raise ValueError("An error occurred")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            some_service_function_fail()

        # Capture logs
        assert "service_call_failed" in caplog.text
        assert "ValueError" in caplog.text
