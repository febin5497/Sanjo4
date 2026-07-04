"""Exceptions module - Custom exception classes for error handling."""

from .custom_exceptions import (
    AppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ResourceNotFoundException,
    ConflictException,
    ServerException,
    ExternalServiceException,
    DatabaseException,
)

__all__ = [
    "AppException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ConflictException",
    "ServerException",
    "ExternalServiceException",
    "DatabaseException",
]
