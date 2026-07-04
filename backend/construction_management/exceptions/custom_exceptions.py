"""
Custom exception hierarchy for centralized error handling.
Each exception type maps to an HTTP status code and error code.
"""

from datetime import datetime
import uuid


class AppException(Exception):
    """Base application exception class."""

    http_status = 500
    error_code = "ERR_INTERNAL"

    def __init__(self, message, error_code=None, http_status=None, details=None):
        """
        Initialize exception.

        Args:
            message: User-friendly error message
            error_code: Unique error identifier (e.g., AUTH_001, VAL_001)
            http_status: HTTP status code
            details: Additional error details (dict)
        """
        self.message = message
        self.error_code = error_code or self.error_code
        self.http_status = http_status or self.http_status
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.request_id = str(uuid.uuid4())

        super().__init__(self.message)

    def to_dict(self):
        """Convert exception to JSON-serializable dict."""
        return {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp,
                "request_id": self.request_id
            }
        }


class ValidationException(AppException):
    """400 - Invalid input data or missing required fields."""
    http_status = 400
    error_code = "VAL_001"

    def __init__(self, message, error_code="VAL_001", details=None):
        super().__init__(message, error_code, 400, details)


class AuthenticationException(AppException):
    """401 - Authentication failed (invalid credentials, expired token, etc)."""
    http_status = 401
    error_code = "AUTH_001"

    def __init__(self, message, error_code="AUTH_001", details=None):
        super().__init__(message, error_code, 401, details)


class AuthorizationException(AppException):
    """403 - User lacks required permissions."""
    http_status = 403
    error_code = "AUTH_003"

    def __init__(self, message, error_code="AUTH_003", details=None):
        super().__init__(message, error_code, 403, details)


class ResourceNotFoundException(AppException):
    """404 - Resource not found."""
    http_status = 404
    error_code = "NOT_FOUND"

    def __init__(self, message, error_code="NOT_FOUND", details=None):
        super().__init__(message, error_code, 404, details)


class ConflictException(AppException):
    """409 - Resource already exists or state conflict."""
    http_status = 409
    error_code = "CONFLICT"

    def __init__(self, message, error_code="CONFLICT", details=None):
        super().__init__(message, error_code, 409, details)


class ServerException(AppException):
    """500 - Internal server error."""
    http_status = 500
    error_code = "ERR_INTERNAL"

    def __init__(self, message, error_code="ERR_INTERNAL", details=None):
        super().__init__(message, error_code, 500, details)


class ExternalServiceException(AppException):
    """503 - External service unavailable."""
    http_status = 503
    error_code = "ERR_SERVICE_UNAVAILABLE"

    def __init__(self, message, error_code="ERR_SERVICE_UNAVAILABLE", details=None):
        super().__init__(message, error_code, 503, details)


class DatabaseException(AppException):
    """500 - Database operation failed."""
    http_status = 500
    error_code = "DB_001"

    def __init__(self, message, error_code="DB_001", details=None):
        super().__init__(message, error_code, 500, details)
