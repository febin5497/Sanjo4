"""
Structured logging utility for centralized error handling.
Logs to both file and activity logger database.
"""

import logging
import os
from datetime import datetime
from flask import has_request_context, request, g
from functools import wraps

# Configure file logger
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ContextFilter(logging.Filter):
    """Add request context to log records."""

    def filter(self, record):
        if has_request_context():
            record.request_id = getattr(g, 'request_id', 'no-id')
        else:
            record.request_id = 'no-context'

        # Add other context fields if available
        record.user_id = getattr(g, 'user_id', '-')
        record.company_id = getattr(g, 'company_id', '-')
        return True


# Apply context filter to all handlers
for handler in logger.handlers:
    handler.addFilter(ContextFilter())


def get_request_context():
    """Extract request context if available."""
    context = {}
    if has_request_context():
        context['request_id'] = getattr(g, 'request_id', None)
        context['user_id'] = getattr(g, 'user_id', None)
        context['company_id'] = getattr(g, 'company_id', None)
        context['endpoint'] = request.endpoint
        context['method'] = request.method
        context['path'] = request.path
    return context


def log_info(message, context=None, **kwargs):
    """Log info level message with context."""
    ctx = get_request_context()
    if context:
        ctx.update(context)
    logger.info(f"{message} | Context: {ctx}", **kwargs)


def log_warning(message, context=None, **kwargs):
    """Log warning level message with context."""
    ctx = get_request_context()
    if context:
        ctx.update(context)
    logger.warning(f"{message} | Context: {ctx}", **kwargs)


def log_error(message, context=None, exception=None, **kwargs):
    """Log error level message with context and optional exception."""
    ctx = get_request_context()
    if context:
        ctx.update(context)
    if exception:
        logger.error(f"{message} | Exception: {str(exception)} | Context: {ctx}",
                    exc_info=True, **kwargs)
    else:
        logger.error(f"{message} | Context: {ctx}", **kwargs)


def log_critical(message, context=None, exception=None, **kwargs):
    """Log critical level message with context and optional exception."""
    ctx = get_request_context()
    if context:
        ctx.update(context)
    if exception:
        logger.critical(f"{message} | Exception: {str(exception)} | Context: {ctx}",
                       exc_info=True, **kwargs)
    else:
        logger.critical(f"{message} | Context: {ctx}", **kwargs)


def log_action(action_type, resource_type, resource_id, status, user_id=None, company_id=None, details=None):
    """
    Log an action for audit trail.

    Args:
        action_type: create, read, update, delete
        resource_type: Staff, Project, Task, etc.
        resource_id: ID of the resource
        status: success, failure
        user_id: User performing action
        company_id: Company context
        details: Additional details (dict)
    """
    ctx = {
        'action_type': action_type,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'status': status,
        'user_id': user_id,
        'company_id': company_id,
        'details': details or {},
        'timestamp': datetime.utcnow().isoformat()
    }
    ctx.update(get_request_context())
    logger.info(f"Action: {action_type} on {resource_type}({resource_id}) - {status} | Context: {ctx}")


def log_decorator(log_level='info'):
    """
    Decorator to automatically log function calls.
    
    Usage:
        @log_decorator()
        def my_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                log_func = getattr(logger, log_level)
                log_func(f"Function {func.__name__} executed successfully")
                return result
            except Exception as e:
                log_error(f"Function {func.__name__} failed", exception=e)
                raise
        return wrapper
    return decorator
