"""
Client-side error logging endpoint.
Receives error logs from the frontend and stores them for monitoring and debugging.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
from utils.logger import log_error, log_info
from exceptions import ValidationException, ServerException

client_logs_bp = Blueprint('client_logs', __name__, url_prefix='/api')


def handle_client_log_errors(f):
    """Decorator to handle errors in client log endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationException as e:
            return jsonify(e.to_dict()), e.http_status
        except ServerException as e:
            return jsonify(e.to_dict()), e.http_status
        except Exception as e:
            log_error("Unexpected error in client logs endpoint", exception=e)
            return jsonify({
                "success": False,
                "error": {
                    "code": "ERR_INTERNAL",
                    "message": "Failed to log client error"
                }
            }), 500
    return decorated_function


@client_logs_bp.route('/client-logs', methods=['POST'])
@handle_client_log_errors
def log_client_error():
    """
    Receive and log client-side errors from frontend.
    
    Expected payload:
    {
        "code": "REACT_ERROR",
        "message": "Error message",
        "component": "ComponentStack",
        "stack": "Stack trace",
        "url": "http://example.com/page",
        "timestamp": "2026-03-27T10:30:00.000Z",
        "userAgent": "Mozilla/5.0...",
        "context": "APIInterceptor:Error",
        "additionalInfo": {...}
    }
    """
    
    data = request.get_json()
    
    if not data:
        raise ValidationException("Request body is required")
    
    # Validate required fields
    if 'code' not in data:
        raise ValidationException("Error code is required")
    
    if 'message' not in data:
        raise ValidationException("Error message is required")
    
    # Extract client error details
    error_code = data.get('code')
    message = data.get('message')
    url = data.get('url', 'unknown')
    timestamp = data.get('timestamp', datetime.utcnow().isoformat())
    user_agent = data.get('userAgent', 'unknown')
    context = data.get('context', 'client')
    
    # Log the client error
    log_error(
        f"Client Error: {error_code}",
        context={
            'code': error_code,
            'message': message,
            'url': url,
            'context': context,
            'userAgent': user_agent,
            'component': data.get('component'),
            'stack': data.get('stack'),
            'additionalInfo': data.get('additionalInfo', {})
        }
    )
    
    log_info(
        f"Client error logged: {error_code}",
        context={
            'error_code': error_code,
            'url': url,
            'context': context
        }
    )
    
    return jsonify({
        "success": True,
        "message": "Error logged successfully",
        "timestamp": timestamp
    }), 201


@client_logs_bp.route('/client-logs/health-check', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify client logging is available.
    """
    return jsonify({
        "success": True,
        "message": "Client logging endpoint is available",
        "timestamp": datetime.utcnow().isoformat()
    }), 200


def register_client_logs_routes(app):
    """Register client logs routes with the app."""
    app.register_blueprint(client_logs_bp)
