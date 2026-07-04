"""
Role and Permission-based authorization decorator
Enhanced to support both role names and granular permissions
"""

from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify, request
from user_management.models import User


def role_required(*allowed_items):
    """
    Decorator to enforce role and permission-based access control.

    Can be used in multiple ways:
    1. @role_required('admin', 'manager')  - Check if user has any of these roles
    2. @role_required(['read_projects', 'create_project'])  - Check if user has any of these permissions
    3. @role_required('manage_users')  - Check if user has this permission

    Args:
        *allowed_items: Variable length argument list of role names or permission names
                       Can include strings and lists

    Returns:
        Decorated function with authorization check
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            user_id = get_jwt_identity()

            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    "success": False,
                    "error": "User not found"
                }), 404

            # Flatten allowed items (handle both individual args and lists)
            allowed_items_list = []
            for item in allowed_items:
                if isinstance(item, (list, tuple)):
                    allowed_items_list.extend(item)
                else:
                    allowed_items_list.append(item)

            # If no restrictions specified, allow all authenticated users
            if not allowed_items_list:
                return func(*args, **kwargs)

            # Check if user has any of the allowed roles or permissions
            has_access = False

            # Get user's roles from RBAC system
            user_roles = user.get_roles()
            user_role_names = [r.name for r in user_roles]

            # Get user's permissions from RBAC system
            user_permissions = user.get_permissions()

            # Also check direct User model role field for common admin roles
            if user.role in ('admin', 'super_admin', 'Super Admin'):
                user_role_names.append(user.role)

            # Check against allowed items
            for item in allowed_items_list:
                # Check if it's a role name
                if item in user_role_names:
                    has_access = True
                    break
                # Check if it's a permission name
                elif item in user_permissions:
                    has_access = True
                    break

            if not has_access:
                return jsonify({
                    "success": False,
                    "error": "Permission denied: Insufficient privileges",
                    "required": allowed_items_list
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator