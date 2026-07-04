"""
BaseResourceRouter - Phase 2.2 Implementation

Auto-generates standard CRUD endpoints for any resource type.
Consolidates 40+ route implementations into a single base class.

Eliminates code duplication for:
- List with pagination and filtering
- Create new resource
- Get single resource
- Update resource
- Delete resource
- Bulk operations

Usage:
    class StaffRouter(BaseResourceRouter):
        model = Staff
        schema = StaffSchema

    app.register_blueprint(StaffRouter.blueprint)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from user_management.models import User
from constants import PAGINATION
from utils.response_formatter import (
    success_response,
    error_response,
    paginated_response,
    validation_error_response
)
from admin_management.utils.activity_logger import log_entity_action


class BaseResourceRouter:
    """
    Base class for resource-based REST API endpoints.

    Provides automatic CRUD endpoint generation for any model.

    Child classes must define:
    - model: SQLAlchemy model class
    - schema: Serialization schema (callable that returns dict from model)
    - entity_name: Human-readable name for logging (e.g., 'Staff', 'Material')
    - searchable_fields: List of field names to search in (optional)

    Auto-generated endpoints:
    - GET /api/<resource>/ - List with pagination
    - POST /api/<resource>/ - Create
    - GET /api/<resource>/<id> - Get single
    - PUT /api/<resource>/<id> - Update
    - DELETE /api/<resource>/<id> - Delete
    - POST /api/<resource>/bulk/delete - Bulk delete
    """

    # Override in child classes
    model = None
    schema = None
    entity_name = None
    searchable_fields = []
    default_per_page = PAGINATION['default_per_page']

    @classmethod
    def create_blueprint(cls, url_prefix=None):
        """
        Create Flask blueprint with all CRUD endpoints.

        Args:
            url_prefix: URL prefix for endpoints (e.g., '/api/staff')

        Returns:
            Flask Blueprint with all CRUD routes
        """
        if not cls.model or not cls.schema:
            raise ValueError(f"{cls.__name__} must define model and schema")

        blueprint = Blueprint(
            cls.model.__tablename__,
            __name__,
            url_prefix=url_prefix or f'/api/{cls.model.__tablename__}'
        )

        # Register all endpoints
        blueprint.add_url_rule(
            '/',
            f'{cls.model.__tablename__}_list',
            cls._list,
            methods=['GET']
        )

        blueprint.add_url_rule(
            '/',
            f'{cls.model.__tablename__}_create',
            cls._create,
            methods=['POST']
        )

        blueprint.add_url_rule(
            '/<int:resource_id>',
            f'{cls.model.__tablename__}_get',
            cls._get,
            methods=['GET']
        )

        blueprint.add_url_rule(
            '/<int:resource_id>',
            f'{cls.model.__tablename__}_update',
            cls._update,
            methods=['PUT']
        )

        blueprint.add_url_rule(
            '/<int:resource_id>',
            f'{cls.model.__tablename__}_delete',
            cls._delete,
            methods=['DELETE']
        )

        blueprint.add_url_rule(
            '/bulk/delete',
            f'{cls.model.__tablename__}_bulk_delete',
            cls._bulk_delete,
            methods=['POST']
        )

        return blueprint

    # ==================== Endpoints ====================

    @classmethod
    @jwt_required()
    def _list(cls):
        """
        List all resources with pagination and filtering.

        Query params:
        - page: Page number (default 1)
        - per_page: Items per page (default 10)
        - search: Search term (searches in searchable_fields)
        - filter_<field>: Filter by field value (e.g., filter_status=active)

        Returns:
            Paginated list of resources
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            # Pagination params
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', cls.default_per_page, type=int)

            # Clamp per_page to limits
            per_page = min(per_page, PAGINATION['max_per_page'])
            per_page = max(per_page, PAGINATION['min_per_page'])

            # Build query
            query = cls.model.query

            # Multi-tenancy: filter by company_id if model has it
            if hasattr(cls.model, 'company_id'):
                query = query.filter_by(company_id=user.company_id)

            # Search
            search_term = request.args.get('search', None, type=str)
            if search_term and cls.searchable_fields:
                search_filters = []
                for field_name in cls.searchable_fields:
                    if hasattr(cls.model, field_name):
                        field = getattr(cls.model, field_name)
                        search_filters.append(field.ilike(f"%{search_term}%"))
                if search_filters:
                    from sqlalchemy import or_
                    query = query.filter(or_(*search_filters))

            # Dynamic filters (filter_<field>=value)
            for key, value in request.args.items():
                if key.startswith('filter_'):
                    field_name = key.replace('filter_', '')
                    if hasattr(cls.model, field_name):
                        field = getattr(cls.model, field_name)
                        query = query.filter(field == value)

            # Execute query
            total = query.count()
            paginated = query.paginate(page=page, per_page=per_page)

            return paginated_response(
                [cls.schema(item) for item in paginated.items],
                total,
                page,
                per_page,
                f"{cls.entity_name or cls.model.__name__} retrieved"
            )

        except Exception as e:
            return error_response(str(e), 500)

    @classmethod
    @jwt_required()
    def _create(cls):
        """
        Create new resource.

        JSON body: Resource data

        Returns:
            Created resource
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            data = request.get_json() or {}

            # Validate required fields (if model defines them)
            errors = cls._validate_create(data)
            if errors:
                return validation_error_response(errors)

            # Create instance
            instance = cls.model(**data)

            # Set multi-tenancy
            if hasattr(instance, 'company_id'):
                instance.company_id = user.company_id
            if hasattr(instance, 'created_by_id'):
                instance.created_by_id = current_user_id

            db.session.add(instance)
            db.session.commit()

            # Log action
            log_entity_action(
                user_id=current_user_id,
                entity_type=cls.entity_name or cls.model.__name__,
                entity_id=instance.id,
                action='create',
                description=f"Created {cls.entity_name}"
            )

            return success_response(
                cls.schema(instance),
                f"{cls.entity_name} created successfully",
                status_code=201
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @classmethod
    @jwt_required()
    def _get(cls, resource_id):
        """
        Get single resource by ID.

        Returns:
            Resource data
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            query = cls.model.query.filter_by(id=resource_id)

            if hasattr(cls.model, 'company_id'):
                query = query.filter_by(company_id=user.company_id)

            instance = query.first()

            if not instance:
                return error_response(f"{cls.entity_name} not found", 404)

            return success_response(
                cls.schema(instance),
                f"{cls.entity_name} retrieved"
            )

        except Exception as e:
            return error_response(str(e), 500)

    @classmethod
    @jwt_required()
    def _update(cls, resource_id):
        """
        Update resource.

        JSON body: Fields to update

        Returns:
            Updated resource
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            data = request.get_json() or {}

            query = cls.model.query.filter_by(id=resource_id)

            if hasattr(cls.model, 'company_id'):
                query = query.filter_by(company_id=user.company_id)

            instance = query.first()

            if not instance:
                return error_response(f"{cls.entity_name} not found", 404)

            # Update fields
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            # Update metadata
            if hasattr(instance, 'updated_by_id'):
                instance.updated_by_id = current_user_id

            db.session.commit()

            # Log action
            log_entity_action(
                user_id=current_user_id,
                entity_type=cls.entity_name or cls.model.__name__,
                entity_id=resource_id,
                action='update',
                description=f"Updated {cls.entity_name}",
                new_values=data
            )

            return success_response(
                cls.schema(instance),
                f"{cls.entity_name} updated successfully"
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @classmethod
    @jwt_required()
    def _delete(cls, resource_id):
        """
        Delete resource.

        Returns:
            Success response
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            query = cls.model.query.filter_by(id=resource_id)

            if hasattr(cls.model, 'company_id'):
                query = query.filter_by(company_id=user.company_id)

            instance = query.first()

            if not instance:
                return error_response(f"{cls.entity_name} not found", 404)

            db.session.delete(instance)
            db.session.commit()

            # Log action
            log_entity_action(
                user_id=current_user_id,
                entity_type=cls.entity_name or cls.model.__name__,
                entity_id=resource_id,
                action='delete',
                description=f"Deleted {cls.entity_name}"
            )

            return success_response(
                None,
                f"{cls.entity_name} deleted successfully"
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @classmethod
    @jwt_required()
    def _bulk_delete(cls):
        """
        Delete multiple resources.

        JSON body:
        {
            "ids": [1, 2, 3, ...]
        }

        Returns:
            Number deleted
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            data = request.get_json() or {}

            ids = data.get('ids', [])

            if not ids or not isinstance(ids, list):
                return error_response("ids must be a non-empty list", 400)

            query = cls.model.query.filter(cls.model.id.in_(ids))

            if hasattr(cls.model, 'company_id'):
                query = query.filter_by(company_id=user.company_id)

            deleted_count = query.delete()
            db.session.commit()

            # Log action
            log_entity_action(
                user_id=current_user_id,
                entity_type=cls.entity_name or cls.model.__name__,
                entity_id=None,
                action='bulk_delete',
                description=f"Bulk deleted {deleted_count} {cls.entity_name} resources"
            )

            return success_response(
                {'deleted': deleted_count},
                f"{deleted_count} {cls.entity_name} resources deleted"
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    # ==================== Helpers ====================

    @classmethod
    def _validate_create(cls, data):
        """
        Validate create request data.

        Override in child classes to add custom validation.

        Args:
            data: Request JSON data

        Returns:
            List of validation errors (empty if valid)
        """
        return []

    @staticmethod
    def register_blueprint(app, blueprint, url_prefix=None):
        """
        Register blueprint with Flask app.

        Args:
            app: Flask app
            blueprint: Blueprint from create_blueprint()
            url_prefix: URL prefix (optional, can be in blueprint)
        """
        app.register_blueprint(blueprint, url_prefix=url_prefix)
