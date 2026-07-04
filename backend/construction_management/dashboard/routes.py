
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "dashboard",
        "status": "working"
    })


@dashboard_bp.route("/api/dashboard", methods=["GET"])
@jwt_required(optional=True)
def api_dashboard():
    """Alias for /dashboard (frontend calls /api/dashboard)"""
    return jsonify({
        "success": True,
        "data": {
            "monthlyRevenue": 0
        }
    })
