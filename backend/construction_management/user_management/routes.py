
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from user_management.models import User

user_bp = Blueprint("user", __name__)


@user_bp.route("/user", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "user_management",
        "status": "working"
    })


@user_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    Verify JWT token and return current user info.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "company_id": user.company_id
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
