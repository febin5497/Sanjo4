from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from user_management.models import User
from flask import jsonify


def require_auth():

    try:

        verify_jwt_in_request()

        user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 401

        return user

    except Exception:

        return jsonify({"error": "Unauthorized"}), 401

def require_role(allowed_roles):

    def wrapper():

        verify_jwt_in_request()

        user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 401

        if user.role not in allowed_roles:
            return jsonify({"error": "Access denied"}), 403

        return user

    return wrapper