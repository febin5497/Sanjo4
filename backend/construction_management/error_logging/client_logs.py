"""
Client Error Logging Routes

Receives and logs errors from frontend for monitoring and debugging.
"""

from flask import Blueprint, request, jsonify, g
from datetime import datetime
from extensions import db
from utils.response_formatter import success_response, error_response, server_error_response
from utils.logger import log_info, log_error
from exceptions.custom_exceptions import ValidationException

client_logs_bp = Blueprint("client_logs", __name__)


class ClientErrorLog(db.Model):
    """Model for storing frontend error logs"""

    __tablename__ = "client_error_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)
    company_id = db.Column(db.Integer, nullable=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    error_type = db.Column(db.String(50), nullable=False, index=True)  # validation, network, auth, etc.
    error_code = db.Column(db.String(50), nullable=True, index=True)
    error_message = db.Column(db.Text, nullable=False)
    context = db.Column(db.String(100), nullable=True)  # Where error occurred
    url = db.Column(db.String(500), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    request_id = db.Column(db.String(100), nullable=True, index=True)
    additional_data = db.Column(db.JSON, nullable=True)
    severity = db.Column(db.String(20), default="warning")  # info, warning, error, critical
    resolved = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "error_type": self.error_type,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "context": self.context,
            "url": self.url,
            "request_id": self.request_id,
            "severity": self.severity,
            "resolved": self.resolved,
        }


@client_logs_bp.route("/api/client-logs", methods=["POST"])
def log_client_error():
    """
    Log error from frontend

    Request body:
    {
        "timestamp": "2024-03-27T10:30:00",
        "context": "ProjectPage",
        "errorType": "network",
        "errorCode": "NETWORK_001",
        "errorMessage": "Failed to fetch projects",
        "requestId": "req_123_abc",
        "userAgent": "Mozilla/5.0...",
        "url": "http://localhost:5173/projects",
        "additionalData": {...}
    }
    """

    try:
        # Validate request
        data = request.get_json()
        if not data:
            raise ValidationException("Request body is required")

        # Extract required fields
        error_message = data.get("errorMessage")
        error_type = data.get("errorType", "unknown")
        context = data.get("context")

        if not error_message:
            raise ValidationException("errorMessage is required")

        # Get user info from JWT (if authenticated)
        user_id = g.get("user_id")
        company_id = g.get("company_id")

        # Create log entry
        log_entry = ClientErrorLog(
            user_id=user_id,
            company_id=company_id,
            error_type=error_type,
            error_code=data.get("errorCode"),
            error_message=error_message,
            context=context,
            url=data.get("url"),
            user_agent=data.get("userAgent"),
            request_id=data.get("requestId"),
            additional_data=data.get("additionalData"),
            severity=determine_severity(error_type),
        )

        # Save to database
        db.session.add(log_entry)
        db.session.commit()

        # Log to application logs
        log_info(
            f"Client error logged: {error_type} - {error_message}",
            context={
                "client_log_id": log_entry.id,
                "error_type": error_type,
                "context": context,
                "request_id": data.get("requestId")
            }
        )

        return success_response(
            data={"log_id": log_entry.id},
            message="Error logged successfully"
        ), 201

    except ValidationException as e:
        return e.to_dict(), e.http_status
    except Exception as e:
        log_error(
            message="Failed to log client error",
            context={"error_type": error_type if 'error_type' in locals() else "unknown"},
            exception=e
        )
        return server_error_response(details=str(e)), 500


@client_logs_bp.route("/api/client-logs", methods=["GET"])
def get_client_logs():
    """
    Retrieve client error logs (admin only)

    Query parameters:
    - error_type: Filter by error type
    - severity: Filter by severity
    - resolved: Filter by resolved status (true/false)
    - page: Page number (default 1)
    - per_page: Items per page (default 20)
    """

    try:
        # Parse query parameters
        error_type = request.args.get("error_type")
        severity = request.args.get("severity")
        resolved = request.args.get("resolved")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        # Build query
        query = ClientErrorLog.query

        # Apply filters
        if error_type:
            query = query.filter_by(error_type=error_type)
        if severity:
            query = query.filter_by(severity=severity)
        if resolved is not None:
            resolved_bool = resolved.lower() == "true"
            query = query.filter_by(resolved=resolved_bool)

        # Sort by newest first
        query = query.order_by(ClientErrorLog.created_at.desc())

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return success_response(
            data=[log.to_dict() for log in paginated.items],
            pagination={
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages
            },
            message="Client logs retrieved successfully"
        ), 200

    except Exception as e:
        log_error("Failed to retrieve client logs", exception=e)
        return server_error_response(details=str(e)), 500


@client_logs_bp.route("/api/client-logs/<int:log_id>/resolve", methods=["PATCH"])
def resolve_client_log(log_id):
    """
    Mark a client error log as resolved

    Request body:
    {
        "resolved": true,
        "notes": "Fixed in v1.2.0"
    }
    """

    try:
        log_entry = ClientErrorLog.query.get(log_id)
        if not log_entry:
            raise ResourceNotFoundException("Log not found", error_code="LOG_NOT_FOUND")

        data = request.get_json() or {}
        log_entry.resolved = data.get("resolved", True)

        db.session.commit()

        log_info(
            f"Client error log resolved: {log_id}",
            context={"log_id": log_id}
        )

        return success_response(
            data=log_entry.to_dict(),
            message="Log resolved"
        ), 200

    except Exception as e:
        log_error("Failed to resolve client log", exception=e)
        return server_error_response(details=str(e)), 500


@client_logs_bp.route("/api/client-logs/summary", methods=["GET"])
def get_client_logs_summary():
    """
    Get summary statistics of client errors
    """

    try:
        # Get error type distribution
        error_type_counts = db.session.query(
            ClientErrorLog.error_type,
            db.func.count(ClientErrorLog.id).label("count")
        ).filter(
            ClientErrorLog.resolved == False
        ).group_by(
            ClientErrorLog.error_type
        ).all()

        # Get severity distribution
        severity_counts = db.session.query(
            ClientErrorLog.severity,
            db.func.count(ClientErrorLog.id).label("count")
        ).filter(
            ClientErrorLog.resolved == False
        ).group_by(
            ClientErrorLog.severity
        ).all()

        # Get total unresolved errors
        total_unresolved = ClientErrorLog.query.filter_by(resolved=False).count()

        # Get most common errors
        most_common = db.session.query(
            ClientErrorLog.error_code,
            ClientErrorLog.error_message,
            db.func.count(ClientErrorLog.id).label("count")
        ).filter(
            ClientErrorLog.resolved == False
        ).group_by(
            ClientErrorLog.error_code,
            ClientErrorLog.error_message
        ).order_by(
            db.desc("count")
        ).limit(10).all()

        return success_response(
            data={
                "total_unresolved": total_unresolved,
                "by_type": [{"type": t, "count": c} for t, c in error_type_counts],
                "by_severity": [{"severity": s, "count": c} for s, c in severity_counts],
                "most_common": [
                    {
                        "error_code": code,
                        "error_message": msg,
                        "count": count
                    }
                    for code, msg, count in most_common
                ]
            },
            message="Summary retrieved successfully"
        ), 200

    except Exception as e:
        log_error("Failed to retrieve client logs summary", exception=e)
        return server_error_response(details=str(e)), 500


def determine_severity(error_type):
    """Determine severity level based on error type"""
    severity_map = {
        "validation": "info",
        "warning": "warning",
        "network": "warning",
        "auth": "error",
        "server": "error",
        "unknown": "warning"
    }
    return severity_map.get(error_type, "warning")


# Import for type hints in error handler
from exceptions.custom_exceptions import ResourceNotFoundException
