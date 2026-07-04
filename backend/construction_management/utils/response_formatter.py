"""
Response Formatter Utility

Provides standardized response formatting for all API endpoints.
Ensures consistent response structure across the entire API.

Standard Response Formats:

SUCCESS:
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {...} or [...],           # Optional
    "pagination": {...}                # Optional - for paginated responses
}

ERROR:
{
    "success": false,
    "error": "Error message",
    "details": "Additional context",   # Optional
    "errors": [...]                    # Optional - for validation errors
}
"""

from flask import jsonify


def success_response(data=None, message="Success", pagination=None, status_code=200):
    """
    Format a successful API response.

    Args:
        data: The response data (dict, list, or None)
        message: User-friendly success message
        pagination: Optional pagination info dict with keys: page, per_page, total, pages
        status_code: HTTP status code (200, 201, etc.)

    Returns:
        tuple: (response_object, status_code)

    Examples:
        # Single item
        return success_response(user.to_dict(), "User retrieved successfully")

        # Multiple items with pagination
        return success_response(
            [user.to_dict() for user in users],
            "Users retrieved successfully",
            pagination={"page": 1, "per_page": 20, "total": 100, "pages": 5}
        )

        # No data (e.g., delete operation)
        return success_response(message="User deleted successfully")

        # Created resource
        return success_response(new_user.to_dict(), "User created successfully", status_code=201)
    """
    response = {
        "success": True,
        "message": message
    }

    if data is not None:
        response["data"] = data

    if pagination is not None:
        response["pagination"] = pagination

    return jsonify(response), status_code


def error_response(error, details=None, errors=None, status_code=400):
    """
    Format an error API response.

    Args:
        error: Main error message (string)
        details: Optional additional context/details
        errors: Optional list of validation errors
                Format: [{"field": "name", "message": "Name is required"}, ...]
        status_code: HTTP status code (400, 404, 500, etc.)

    Returns:
        tuple: (response_object, status_code)

    Examples:
        # Simple error
        return error_response("User not found", status_code=404)

        # Error with details
        return error_response(
            "User not found",
            details="No user with ID 999 exists",
            status_code=404
        )

        # Validation error
        return error_response(
            "Validation failed",
            errors=[
                {"field": "email", "message": "Email is required"},
                {"field": "name", "message": "Name must be at least 2 characters"}
            ],
            status_code=400
        )
    """
    response = {
        "success": False,
        "message": error,
        "error": error
    }

    if details is not None:
        response["details"] = details

    if errors is not None:
        response["errors"] = errors

    return jsonify(response), status_code


def paginated_response(items, total, page, per_page, message="Records retrieved successfully", status_code=200):
    """
    Format a paginated list response with all pagination metadata.

    Args:
        items: List of items to return (already serialized to dicts/lists)
        total: Total number of items in database (not page size)
        page: Current page number (1-indexed)
        per_page: Items per page
        message: Success message
        status_code: HTTP status code

    Returns:
        tuple: (response_object, status_code)

    Examples:
        staff_list = [staff.to_dict() for staff in query.all()]
        return paginated_response(
            items=staff_list,
            total=query.count(),
            page=1,
            per_page=20
        )
    """
    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": total_pages
    }

    return success_response(
        data=items,
        message=message,
        pagination=pagination,
        status_code=status_code
    )


def validation_error_response(errors, status_code=400):
    """
    Format a validation error response for field-level errors.

    Args:
        errors: List of validation errors
                Format: [{"field": "name", "message": "Name is required"}, ...]
        status_code: HTTP status code (usually 400)

    Returns:
        tuple: (response_object, status_code)

    Example:
        return validation_error_response([
            {"field": "email", "message": "Email is required"},
            {"field": "password", "message": "Password must be at least 8 characters"}
        ])
    """
    return error_response(
        error="Validation failed",
        errors=errors,
        status_code=status_code
    )


def unauthorized_response(message="Unauthorized access"):
    """
    Format an unauthorized (401) response.

    Args:
        message: Custom message (default: "Unauthorized access")

    Returns:
        tuple: (response_object, 401)
    """
    return error_response(error=message, status_code=401)


def forbidden_response(message="Access denied"):
    """
    Format a forbidden (403) response.

    Args:
        message: Custom message (default: "Access denied")

    Returns:
        tuple: (response_object, 403)
    """
    return error_response(error=message, status_code=403)


def not_found_response(resource_type="Resource", details=None):
    """
    Format a not found (404) response.

    Args:
        resource_type: Type of resource (e.g., "User", "Material", "Project")
        details: Optional additional details

    Returns:
        tuple: (response_object, 404)

    Example:
        return not_found_response("User", details="No user with ID 999 found")
    """
    return error_response(
        error=f"{resource_type} not found",
        details=details,
        status_code=404
    )


def server_error_response(message="Internal server error", details=None):
    """
    Format a server error (500) response.

    Args:
        message: Error message
        details: Optional additional details (e.g., exception message)

    Returns:
        tuple: (response_object, 500)

    Example:
        try:
            # Do something
        except Exception as e:
            return server_error_response(details=str(e))
    """
    return error_response(
        error=message,
        details=details,
        status_code=500
    )
