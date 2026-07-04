"""
Global error handler middleware for Flask.
Catches all exceptions and converts them to standardized JSON responses.
"""

from flask import jsonify, request, g
from werkzeug.exceptions import HTTPException
import uuid
import traceback
from exceptions import AppException
from utils.logger import log_error, get_request_context


def setup_error_handlers(app):
    """Register global error handlers for the Flask app."""

    @app.before_request
    def before_request():
        """Generate request ID and store in g."""
        g.request_id = request.headers.get('x-request-id', str(uuid.uuid4()))
        g.user_id = None
        g.company_id = None

    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """Handle custom AppException."""
        log_error(
            f"AppException: {error.error_code}",
            context={
                'error_code': error.error_code,
                'message': error.message,
                'details': error.details
            },
            exception=error
        )
        response = error.to_dict()
        return jsonify(response), error.http_status

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle Flask/Werkzeug HTTP exceptions."""
        log_error(
            f"HTTP Exception: {error.code}",
            context={
                'status': error.code,
                'message': error.description
            },
            exception=error
        )
        return jsonify({
            "success": False,
            "error": {
                "code": f"HTTP_{error.code}",
                "message": error.description or "An HTTP error occurred",
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "request_id": g.request_id
            }
        }), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all uncaught exceptions."""
        log_error(
            f"Unhandled Exception: {type(error).__name__}",
            context={
                'error_type': type(error).__name__,
                'traceback': traceback.format_exc()
            },
            exception=error
        )
        return jsonify({
            "success": False,
            "error": {
                "code": "ERR_INTERNAL",
                "message": "An unexpected error occurred",
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "request_id": g.request_id
            }
        }), 500

    @app.after_request
    def after_request(response):
        """Add request ID to response headers."""
        response.headers['x-request-id'] = getattr(g, 'request_id', 'unknown')
        return response
