from flask import Blueprint, request, jsonify
from user_management.models import User
from company_settings.models import Company
from extensions import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# Login user and generate JWT
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Validate inputs
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    # Find user by username
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Check if user account is active
    if not user.is_active:
        return jsonify({"error": "Account is inactive. Contact administrator."}), 403

    # Verify password
    if not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Get staff information using direct SQL to avoid ORM schema issues
    staff_id = None
    position = None
    department = None
    staff_name = user.name or user.username

    try:
        from sqlalchemy import text
        result = db.session.execute(
            text('SELECT id, staff_id, name, designation, department FROM staff WHERE user_id = :user_id'),
            {'user_id': user.id}
        ).fetchone()

        if result:
            staff_id = result[0]  # id column (integer database ID)
            staff_name = result[2]  # name
            position = result[3]  # designation
            department = result[4]  # department
    except Exception as e:
        # If direct SQL also fails, just continue without staff info
        print(f"Warning: Could not load staff info: {str(e)}")
        pass

    # Create access token
    access_token = create_access_token(identity=str(user.id))

    response = {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "password_change_required": user.password_change_required,
            "staff_id": staff_id,
            "position": position,
            "department": department,
            "name": staff_name
        }
    }

    # Warn if password change is required
    if user.password_change_required:
        response["message"] = "Password change required on first login"

    return jsonify(response), 200


# Logout (invalidate token on client side - JWT is stateless, but provide the endpoint)
@auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


# Get current user info
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    staff_id = None
    position = None
    department = None
    staff_name = user.name or user.username

    try:
        from sqlalchemy import text
        result = db.session.execute(
            text('SELECT id, staff_id, name, designation, department FROM staff WHERE user_id = :user_id'),
            {'user_id': user.id}
        ).fetchone()

        if result:
            staff_id = result[0]
            staff_name = result[2]
            position = result[3]
            department = result[4]
    except Exception:
        pass

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "company_id": user.company_id,
            "password_change_required": user.password_change_required,
            "staff_id": staff_id,
            "position": position,
            "department": department
        }
    }), 200


# Register a new user
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request body:
    {
        "username": "john_doe",
        "password": "SecurePassword123!",
        "role": "admin"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"{field.title()} is required"
                }), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')
        role = data.get('role', '').strip()

        # Validate username
        if len(username) < 3:
            return jsonify({
                "success": False,
                "error": "Username must be at least 3 characters"
            }), 400

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                "success": False,
                "error": "Username already exists"
            }), 400

        # Validate password strength
        if len(password) < 8:
            return jsonify({
                "success": False,
                "error": "Password must be at least 8 characters"
            }), 400

        if not any(char.isupper() for char in password):
            return jsonify({
                "success": False,
                "error": "Password must contain at least one uppercase letter"
            }), 400

        if not any(char.isdigit() for char in password):
            return jsonify({
                "success": False,
                "error": "Password must contain at least one digit"
            }), 400

        # Create new user
        new_user = User(
            username=username,
            role=role
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "data": {
                "user_id": new_user.id,
                "username": new_user.username,
                "role": new_user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# Change password (required on first login)
@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password. Optionally verify old password.

    Request body:
    {
        "old_password": "Erp@123",  # Optional, but recommended
        "new_password": "NewPassword123!"
    }
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        data = request.get_json()

        new_password = data.get('new_password', '').strip()
        old_password = data.get('old_password', '')

        # Validate new password
        if not new_password:
            return jsonify({
                "success": False,
                "error": "New password is required"
            }), 400

        if len(new_password) < 8:
            return jsonify({
                "success": False,
                "error": "Password must be at least 8 characters"
            }), 400

        if not any(char.isupper() for char in new_password):
            return jsonify({
                "success": False,
                "error": "Password must contain at least one uppercase letter"
            }), 400

        if not any(char.isdigit() for char in new_password):
            return jsonify({
                "success": False,
                "error": "Password must contain at least one digit"
            }), 400

        if not any(char.isalnum() and not char.isalnum() or char in "!@#$%^&*" for char in new_password):
            # Allow alphanumeric and common special characters
            pass

        # Verify old password if provided
        if old_password and not user.check_password(old_password):
            return jsonify({
                "success": False,
                "error": "Current password is incorrect"
            }), 401

        # Change password
        user.change_password(new_password)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

