"""
Activity Logging Decorator & Utility Functions
Automatically logs user actions (Create, Update, Delete) for audit trail
"""

from functools import wraps
from flask import request
from flask_jwt_extended import get_jwt_identity
import json
from datetime import datetime

from extensions import db
from admin_management.models import ActivityLog
from user_management.models import User


def log_entity_action(
    user_id,
    company_id=None,
    entity_type=None,
    entity_id=None,
    action=None,
    old_values=None,
    new_values=None,
    entity_name=None,
    ip_address=None,
    user_agent=None
):
    """
    Utility function for direct logging of entity actions.
    More flexible than decorator for complex scenarios.

    Args:
        user_id (int): ID of user performing action
        company_id (int): ID of company (for multi-tenancy)
        entity_type (str): Type of entity (Project, Staff, Material, etc.)
        entity_id (int): ID of the entity being modified
        action (str): CREATE, UPDATE, DELETE, APPROVE, REJECT, etc.
        old_values (dict): Dictionary of old field values for updates
        new_values (dict): Dictionary of new field values
        entity_name (str): Display name of entity (optional, for readability)
        ip_address (str): IP address of request
        user_agent (str): User agent string

    Returns:
        ActivityLog: Created activity log object, or None on error
    """
    try:
        # Serialize old and new values to JSON
        old_value_json = json.dumps(old_values, default=str) if old_values else None
        new_value_json = json.dumps(new_values, default=str) if new_values else None

        activity = ActivityLog(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name or f"{entity_type}#{entity_id}",
            action=action.upper(),
            old_value=old_value_json,
            new_value=new_value_json,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow()
        )

        db.session.add(activity)
        db.session.commit()
        return activity

    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        db.session.rollback()
        return None


def log_activity(entity_type, action_type='UPDATE'):
    """
    Decorator to automatically log user actions for audit compliance.

    Usage:
        @log_activity('Project', 'CREATE')
        def create_project():
            ...

        @log_activity('Staff', 'UPDATE')
        def update_staff(staff_id):
            ...

        @log_activity('Invoice', 'DELETE')
        def delete_invoice(invoice_id):
            ...

    Args:
        entity_type (str): Type of entity being modified (e.g., 'Project', 'Staff', 'Invoice')
        action_type (str): Type of action (CREATE, UPDATE, DELETE, APPROVE, REJECT)

    Returns:
        Decorated function with automatic activity logging
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # Try to get user ID and company ID
            try:
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                company_id = user.company_id if user else None
            except:
                user_id = None
                company_id = None

            # Get request information
            ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
            user_agent = request.headers.get('User-Agent', '')

            # Store request data before function execution (for detecting changes)
            request_data_before = None
            if request.method in ['PUT', 'PATCH']:
                try:
                    request_data_before = request.get_json() or {}
                except:
                    pass

            # Execute the actual function
            response = func(*args, **kwargs)

            # After function execution, try to log the activity
            try:
                # Extract entity information from response if available
                entity_id = None
                entity_name = None
                old_value = None
                new_value = None

                # If response is a tuple (typical Flask response), extract JSON data
                if isinstance(response, tuple):
                    response_json = response[0]
                    status_code = response[1] if len(response) > 1 else 200
                else:
                    response_json = response
                    status_code = 200

                # Try to extract JSON from response
                try:
                    if hasattr(response_json, 'get_json'):
                        response_data = response_json.get_json()
                    else:
                        response_data = response_json
                except:
                    response_data = {}

                # Only log on successful operations (2xx status codes)
                if isinstance(status_code, int) and 200 <= status_code < 300:
                    # Extract entity info from response
                    if isinstance(response_data, dict) and 'data' in response_data:
                        data = response_data['data']
                        if isinstance(data, dict):
                            entity_id = data.get('id')
                            entity_name = data.get('name') or data.get('username') or str(entity_id)
                            new_value = json.dumps(data, default=str)

                    # For updates, capture old values from request
                    if action_type == 'UPDATE' and request_data_before:
                        old_value = json.dumps(request_data_before, default=str)

                    # If we couldn't extract entity_id from response, try to get from function arguments
                    if not entity_id:
                        # Common pattern: function(id) or function(entity_id=...)
                        if args and isinstance(args[-1], int):
                            entity_id = args[-1]
                        elif 'entity_id' in kwargs:
                            entity_id = kwargs['entity_id']
                        elif args:
                            try:
                                entity_id = int(str(args[-1]))
                            except:
                                pass

                    # Create activity log
                    if user_id and company_id:
                        activity = ActivityLog(
                            user_id=user_id,
                            company_id=company_id,
                            entity_type=entity_type,
                            entity_id=entity_id,
                            entity_name=entity_name or f"{entity_type}#{entity_id}",
                            action=action_type.upper(),
                            old_value=old_value,
                            new_value=new_value,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            timestamp=datetime.utcnow()
                        )

                        db.session.add(activity)
                        db.session.commit()

            except Exception as e:
                # Log activity errors but don't break the main function
                print(f"Error logging activity: {str(e)}")
                db.session.rollback()

            # Return the original response
            return response

        return wrapper

    return decorator


def log_bulk_action(entity_type, action_type='DELETE'):
    """
    Decorator for logging bulk operations (bulk delete, bulk update)

    Usage:
        @log_bulk_action('Project', 'DELETE')
        def bulk_delete_projects():
            ...

    Args:
        entity_type (str): Type of entity being modified
        action_type (str): Type of action (DELETE, UPDATE, etc.)

    Returns:
        Decorated function with bulk action logging
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            # Get user and company info
            try:
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                company_id = user.company_id if user else None
            except:
                user_id = None
                company_id = None

            # Get request information
            ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]

            # Extract IDs from request if available
            entity_ids = []
            try:
                request_data = request.get_json() or {}
                entity_ids = request_data.get('ids', []) or request_data.get('entity_ids', [])
            except:
                pass

            # Execute the actual function
            response = func(*args, **kwargs)

            # Check if operation was successful
            try:
                if isinstance(response, tuple):
                    response_json = response[0]
                    status_code = response[1] if len(response) > 1 else 200
                else:
                    response_json = response
                    status_code = 200

                # Log on successful operation
                if isinstance(status_code, int) and 200 <= status_code < 300:
                    if user_id and company_id:
                        # Create a single activity log for the bulk action
                        activity = ActivityLog(
                            user_id=user_id,
                            company_id=company_id,
                            entity_type=entity_type,
                            entity_id=None,
                            entity_name=f"Bulk {action_type.lower()} of {len(entity_ids)} items",
                            action=f"BULK_{action_type.upper()}",
                            old_value=json.dumps({'ids': entity_ids}, default=str) if entity_ids else None,
                            ip_address=ip_address,
                            timestamp=datetime.utcnow()
                        )

                        db.session.add(activity)
                        db.session.commit()

            except Exception as e:
                print(f"Error logging bulk activity: {str(e)}")
                db.session.rollback()

            return response

        return wrapper

    return decorator
