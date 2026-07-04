"""
Specialized Admin Management Routers - Using BaseResourceRouter

Auto-generates CRUD endpoints for admin entities:
- Roles
- Permissions

Consolidates explicit route implementations.
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from base.base_resource_router import BaseResourceRouter
from admin_management.models.role import Role
from admin_management.models.permission import Permission


# ==================== Role Router ====================

class RoleRouter(BaseResourceRouter):
    """Auto-generates Role CRUD endpoints"""
    model = Role
    entity_name = "Role"
    searchable_fields = ['name']

    @classmethod
    def schema(cls, obj):
        """Schema for Role responses"""
        return {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'is_system_role': obj.is_system_role,
            'permission_count': len(obj.permissions),
            'permissions': [{'id': p.id, 'name': p.name} for p in obj.permissions],
            'created_at': obj.created_at.isoformat() if obj.created_at else None,
            'updated_at': obj.updated_at.isoformat() if obj.updated_at else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Role creation"""
        errors = []
        if not data.get('name'):
            errors.append({'field': 'name', 'message': 'Role name required'})
        # Check for duplicate
        existing = cls.model.query.filter_by(name=data.get('name')).first()
        if existing:
            errors.append({'field': 'name', 'message': 'Role name already exists'})
        return errors


# ==================== Permission Router ====================

class PermissionRouter(BaseResourceRouter):
    """Auto-generates Permission CRUD endpoints"""
    model = Permission
    entity_name = "Permission"
    searchable_fields = ['name', 'description']

    @classmethod
    def schema(cls, obj):
        """Schema for Permission responses"""
        return {
            'id': obj.id,
            'name': obj.name,
            'description': obj.description,
            'category': obj.category if hasattr(obj, 'category') else None,
            'resource': obj.resource if hasattr(obj, 'resource') else None,
            'action': obj.action if hasattr(obj, 'action') else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Permission creation"""
        errors = []
        if not data.get('name'):
            errors.append({'field': 'name', 'message': 'Permission name required'})
        if not data.get('resource'):
            errors.append({'field': 'resource', 'message': 'Resource required'})
        if not data.get('action'):
            errors.append({'field': 'action', 'message': 'Action required'})
        return errors


# ==================== Register Routers ====================

def register_admin_routers(app):
    """Register all admin management routers with Flask app"""
    # Roles
    role_bp = RoleRouter.create_blueprint(url_prefix='/api/admin/roles')
    app.register_blueprint(role_bp)

    # Permissions
    permission_bp = PermissionRouter.create_blueprint(url_prefix='/api/admin/permissions')
    app.register_blueprint(permission_bp)
