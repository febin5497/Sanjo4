"""
Error codes reference for all possible API errors.
Used for documentation, testing, and consistent error reporting.
"""

ERROR_CODES = {
    # Authentication Errors (AUTH_xxx)
    "AUTH_001": "Invalid email or password",
    "AUTH_002": "Token expired or invalid",
    "AUTH_003": "Account inactive or disabled",
    "AUTH_004": "Email not verified",
    "AUTH_005": "Too many login attempts, try again later",
    "AUTH_006": "Session expired",

    # Validation Errors (VAL_xxx)
    "VAL_001": "Invalid input data",
    "VAL_002": "Missing required field",
    "VAL_003": "Field validation failed",
    "VAL_004": "Invalid email format",
    "VAL_005": "Invalid date format",
    "VAL_006": "Password does not meet requirements",
    "VAL_007": "Email already registered",
    "VAL_008": "Invalid phone number",

    # Authorization Errors (PERM_xxx)
    "PERM_001": "Insufficient permissions for this action",
    "PERM_002": "Access denied",
    "PERM_003": "Company access denied",
    "PERM_004": "Project access denied",

    # Database Errors (DB_xxx)
    "DB_001": "Database operation failed",
    "DB_002": "Query execution error",
    "DB_003": "Transaction failed",
    "DB_004": "Constraint violation",
    "DB_005": "Connection error",

    # Resource Errors (RES_xxx)
    "RES_001": "Resource not found",
    "RES_002": "Project not found",
    "RES_003": "Staff member not found",
    "RES_004": "Task not found",
    "RES_005": "Company not found",
    "RES_006": "User not found",

    # Conflict Errors (CONF_xxx)
    "CONF_001": "Resource already exists",
    "CONF_002": "Invalid state transition",
    "CONF_003": "Duplicate entry detected",
    "CONF_004": "Related resources still exist",

    # Server Errors (ERR_xxx)
    "ERR_INTERNAL": "Internal server error",
    "ERR_NOT_IMPLEMENTED": "Feature not implemented",
    "ERR_SERVICE_UNAVAILABLE": "Service temporarily unavailable",
    "ERR_TIMEOUT": "Request timeout",
    "ERR_FILE_UPLOAD": "File upload failed",
    "ERR_FILE_NOT_FOUND": "File not found",

    # Business Logic Errors (BIZ_xxx)
    "BIZ_001": "Insufficient funds",
    "BIZ_002": "Inventory out of stock",
    "BIZ_003": "Invalid quantity",
    "BIZ_004": "Order cannot be processed",
    "BIZ_005": "Staff already assigned to project",
    "BIZ_006": "Cannot unassign all staff from project",
    "BIZ_007": "Vehicle already assigned",
    "BIZ_008": "Maintenance required",
}


def get_error_message(error_code):
    """
    Get the error message for a given error code.

    Args:
        error_code: Error code string (e.g., "AUTH_001")

    Returns:
        Error message or generic message if code not found
    """
    return ERROR_CODES.get(error_code, "An error occurred")
