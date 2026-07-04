"""
Admin Management Routes
Endpoints for managing roles, permissions, users, and activity logs
"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from io import StringIO
import csv

from extensions import db
from admin_management.models import Role, Permission, UserRole, ActivityLog
from company_settings.models import CompanySettings
from user_management.models import User
from utils.role_required import role_required

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


# ==================== PERMISSIONS ENDPOINTS ====================

@admin_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    """Get all permissions, optionally filtered by category"""
    try:
        category = request.args.get('category')

        if category:
            permissions = Permission.query.filter_by(category=category).all()
        else:
            permissions = Permission.query.all()

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in permissions],
            'count': len(permissions)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/permissions/categories', methods=['GET'])
@jwt_required()
def get_permission_categories():
    """Get all permission categories"""
    try:
        # Get distinct categories
        categories = db.session.query(Permission.category).distinct().all()
        categories = [c[0] for c in categories]

        return jsonify({
            'success': True,
            'data': categories
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ROLES ENDPOINTS ====================

@admin_bp.route('/roles', methods=['GET'])
@jwt_required()
@role_required(['manage_roles', 'view_admin_dashboard'])
def get_roles():
    """Get all roles"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Paginate roles
        paginated = Role.query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/roles', methods=['POST'])
@jwt_required()
@role_required(['manage_roles'])
def create_role():
    """Create a new role"""
    try:
        data = request.get_json()

        # Validation
        if not data or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Role name is required'
            }), 400

        # Check if role already exists
        existing = Role.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': f"Role '{data['name']}' already exists"
            }), 409

        # Create role
        role = Role(
            name=data['name'],
            description=data.get('description', ''),
            is_system_role=False  # Custom roles are not system roles
        )

        # Add permissions if provided
        if data.get('permission_ids'):
            permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
            role.permissions = permissions

        db.session.add(role)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Role '{role.name}' created successfully",
            'data': role.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/roles/<int:role_id>', methods=['GET'])
@jwt_required()
@role_required(['manage_roles'])
def get_role(role_id):
    """Get specific role details"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404

        return jsonify({
            'success': True,
            'data': role.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/roles/<int:role_id>', methods=['PUT'])
@jwt_required()
@role_required(['manage_roles'])
def update_role(role_id):
    """Update role details and permissions"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404

        # Prevent updating system roles
        if role.is_system_role:
            return jsonify({
                'success': False,
                'error': 'Cannot modify system roles'
            }), 403

        data = request.get_json()

        # Update role name and description
        if 'name' in data:
            role.name = data['name']
        if 'description' in data:
            role.description = data['description']

        # Update permissions if provided
        if 'permission_ids' in data:
            permissions = Permission.query.filter(Permission.id.in_(data['permission_ids'])).all()
            role.permissions = permissions

        role.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Role updated successfully',
            'data': role.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
@role_required(['manage_roles'])
def delete_role(role_id):
    """Delete a role (only non-system roles)"""
    try:
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404

        # Prevent deleting system roles
        if role.is_system_role:
            return jsonify({
                'success': False,
                'error': 'Cannot delete system roles'
            }), 403

        # Check if any users have this role
        user_count = UserRole.query.filter_by(role_id=role_id).count()
        if user_count > 0:
            return jsonify({
                'success': False,
                'error': f'Cannot delete role: {user_count} users are assigned to this role'
            }), 409

        db.session.delete(role)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Role '{role.name}' deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== USER MANAGEMENT ENDPOINTS ====================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required(['manage_users'])
def get_users():
    """Get all users with pagination and filters"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        search = request.args.get('search')

        # Base query
        query = User.query

        # Apply filters
        if search:
            query = query.filter(
                (User.name.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.username.ilike(f'%{search}%'))
            )

        if role_filter:
            # Filter by role
            query = query.join(UserRole).filter(
                UserRole.role_id == role_filter
            ).distinct()

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Get user data with roles
        users_data = []
        for u in paginated.items:
            roles = u.get_roles()
            user_dict = {
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'username': u.username,
                'is_active': u.is_active if hasattr(u, 'is_active') else True,
                'created_at': u.created_at.isoformat() if u.created_at else None,
                'roles': [{'id': r.id, 'name': r.name} for r in roles]
            }
            users_data.append(user_dict)

        return jsonify({
            'success': True,
            'data': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required(['manage_users'])
def create_user():
    """Create a new user account"""
    try:
        data = request.get_json()

        # Validation
        if not data or not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Name, email, and password are required'
            }), 400

        # Check if user already exists
        existing = User.query.filter(
            (User.email == data['email']) | (User.username == data['email'].split('@')[0])
        ).first()

        if existing:
            return jsonify({
                'success': False,
                'error': 'User with this email already exists'
            }), 409

        # Create user
        user = User(
            name=data['name'],
            email=data['email'],
            username=data.get('username', data['email'].split('@')[0]),
            password=data['password'],
            is_active=True
        )

        db.session.add(user)
        db.session.commit()

        # Log activity
        try:
            activity = ActivityLog(
                user_id=get_jwt_identity(),
                entity_type='User',
                entity_id=user.id,
                action='create',
                new_value=f"User {user.name} created"
            )
            db.session.add(activity)
            db.session.commit()
        except:
            pass  # Activity logging failure should not prevent user creation

        return jsonify({
            'success': True,
            'message': f"User '{user.name}' created successfully",
            'data': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'roles': []
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required(['manage_users'])
def update_user(user_id):
    """Update user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        data = request.get_json()

        # Update name if provided
        if 'name' in data:
            user.name = data['name']

        # Update email if provided
        if 'email' in data:
            # Check if new email already exists
            existing = User.query.filter(
                (User.email == data['email']) & (User.id != user_id)
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'This email is already in use'
                }), 409
            user.email = data['email']

        # Update password if provided
        if 'password' in data and data['password']:
            user.password = data['password']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        # Log activity
        try:
            activity = ActivityLog(
                user_id=get_jwt_identity(),
                entity_type='User',
                entity_id=user.id,
                action='update',
                new_value=f"User {user.name} updated"
            )
            db.session.add(activity)
            db.session.commit()
        except:
            pass

        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'data': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'username': user.username,
                'is_active': user.is_active,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'roles': [r.name for r in user.get_roles()]
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['manage_users'])
def delete_user(user_id):
    """Delete/Deactivate a user"""
    try:
        # Prevent deleting own account
        current_user_id = get_jwt_identity()
        if current_user_id == user_id:
            return jsonify({
                'success': False,
                'error': 'Cannot delete your own account'
            }), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Soft delete - just deactivate
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()

        # Log activity
        try:
            activity = ActivityLog(
                user_id=current_user_id,
                entity_type='User',
                entity_id=user.id,
                action='delete',
                new_value=f"User {user.name} deactivated"
            )
            db.session.add(activity)
            db.session.commit()
        except:
            pass

        return jsonify({
            'success': True,
            'message': f"User '{user.name}' has been deactivated"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@jwt_required()
@role_required(['manage_users'])
def get_user_roles(user_id):
    """Get all roles assigned to a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        user_roles = UserRole.query.filter_by(
            user_id=user_id
        ).all()

        return jsonify({
            'success': True,
            'data': [ur.to_dict() for ur in user_roles]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@jwt_required()
@role_required(['manage_users'])
def assign_role_to_user(user_id):
    """Assign a role to a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        data = request.get_json()
        role_id = data.get('role_id')

        if not role_id:
            return jsonify({
                'success': False,
                'error': 'role_id is required'
            }), 400

        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'success': False,
                'error': 'Role not found'
            }), 404

        # Check if user already has this role
        existing = UserRole.query.filter_by(
            user_id=user_id,
            role_id=role_id
        ).first()

        if existing:
            return jsonify({
                'success': False,
                'error': f"User already has role '{role.name}'"
            }), 409

        # Create user role assignment
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by_id=current_user_id
        )

        db.session.add(user_role)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Role '{role.name}' assigned to user '{user.username}'",
            'data': user_role.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@jwt_required()
@role_required(['manage_users'])
def remove_role_from_user(user_id, role_id):
    """Remove a role from a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        user_role = UserRole.query.filter_by(
            user_id=user_id,
            role_id=role_id
        ).first()

        if not user_role:
            return jsonify({
                'success': False,
                'error': 'User does not have this role'
            }), 404

        role = Role.query.get(role_id)
        db.session.delete(user_role)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Role '{role.name}' removed from user '{user.username}'"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== ACTIVITY LOG ENDPOINTS ====================

@admin_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
@role_required(['view_audit_logs'])
def get_activity_logs():
    """Get activity logs with filters and pagination"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        entity_type = request.args.get('entity_type')
        action = request.args.get('action')
        user_id = request.args.get('user_id', type=int)
        days = request.args.get('days', 30, type=int)

        # Base query
        query = ActivityLog.query

        # Filter by date range
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(ActivityLog.timestamp >= start_date)

        # Apply filters
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if action:
            query = query.filter_by(action=action)
        if user_id:
            query = query.filter_by(user_id=user_id)

        # Sort by timestamp descending
        query = query.order_by(ActivityLog.timestamp.desc())

        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'data': [log.to_dict() for log in paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/activity-logs/<int:log_id>', methods=['GET'])
@jwt_required()
@role_required(['view_audit_logs'])
def get_activity_log_detail(log_id):
    """Get detailed activity log with full change information"""
    try:
        log = ActivityLog.query.get(log_id)
        if not log:
            return jsonify({
                'success': False,
                'error': 'Activity log not found'
            }), 404

        return jsonify({
            'success': True,
            'data': log.to_dict(include_changes=True)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/activity-logs/export', methods=['POST'])
@jwt_required()
@role_required(['view_audit_logs'])
def export_activity_logs():
    """Export activity logs to CSV"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json() or {}
        days = data.get('days', 30)
        entity_type = data.get('entity_type')
        action = data.get('action')

        # Build query
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        query = ActivityLog.query.filter(
            ActivityLog.timestamp >= start_date
        )

        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if action:
            query = query.filter_by(action=action)

        logs = query.order_by(ActivityLog.timestamp.desc()).all()

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Timestamp', 'User', 'Entity Type', 'Entity ID', 'Action',
            'Old Value', 'New Value', 'IP Address'
        ])

        # Write data
        for log in logs:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.user.username if log.user else 'Unknown',
                log.entity_type,
                log.entity_id,
                log.action,
                log.old_value or '',
                log.new_value or '',
                log.ip_address or ''
            ])

        # Create file response
        output.seek(0)
        filename = f"activity_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        return send_file(
            StringIO(output.getvalue()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== DASHBOARD ENDPOINTS ====================

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@role_required(['view_admin_dashboard'])
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Count active users
        active_users = User.query.count()

        # Count roles
        total_roles = db.session.query(UserRole).distinct(UserRole.role_id).count()

        # Count recent activities (last 24 hours)
        from datetime import timedelta
        recent_activities = ActivityLog.query.filter(
            ActivityLog.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ).count()

        # Most active users (last 7 days)
        from sqlalchemy import func
        top_users = db.session.query(
            User.username,
            func.count(ActivityLog.id).label('count')
        ).join(ActivityLog, ActivityLog.user_id == User.id).filter(
            ActivityLog.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).group_by(User.id).order_by(func.count(ActivityLog.id).desc()).limit(5).all()

        return jsonify({
            'success': True,
            'data': {
                'active_users': active_users,
                'total_roles': total_roles,
                'recent_activities_24h': recent_activities,
                'top_users': [{'username': u[0], 'activities': u[1]} for u in top_users]
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
