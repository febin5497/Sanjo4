"""
Specialized Project Management Routers - Using BaseResourceRouter

Auto-generates CRUD endpoints for project entities:
- Projects
- Stages
- Task Models

Consolidates explicit route implementations.
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from base.base_resource_router import BaseResourceRouter
from project_management.models.models import Project
from project_management.models.stage import ProjectStage
from project_management.models.task_model import ProjectTask
from user_management.models import User


# ==================== Project Router ====================

class ProjectRouter(BaseResourceRouter):
    """Auto-generates Project CRUD endpoints"""
    model = Project
    entity_name = "Project"
    searchable_fields = ['name', 'location']

    @classmethod
    def schema(cls, obj):
        """Schema for Project responses"""
        return {
            'id': obj.id,
            'name': obj.name,
            'location': obj.location,
            'start_date': obj.start_date.isoformat(),
            'status': obj.status,
            'client_id': obj.client_id,
            'company_id': obj.company_id,
            'rate_per_sqft': float(obj.rate_per_sqft) if obj.rate_per_sqft else None,
            'square_feet': float(obj.square_feet) if obj.square_feet else None,
            'total_contract_value': float(obj.square_feet * obj.rate_per_sqft) if (obj.square_feet and obj.rate_per_sqft) else None,
            'user_id': obj.user_id,
            'agreement': obj.agreement,
            'plan': obj.plan,
            'three_d_plan': obj.three_d_plan,
            'panchayat_certificate': obj.panchayat_certificate,
            'latitude': obj.latitude,
            'longitude': obj.longitude
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Project creation"""
        errors = []
        if not data.get('name'):
            errors.append({'field': 'name', 'message': 'Project name required'})
        if not data.get('location'):
            errors.append({'field': 'location', 'message': 'Location required'})
        if not data.get('start_date'):
            errors.append({'field': 'start_date', 'message': 'Start date required'})
        if not data.get('client_id'):
            errors.append({'field': 'client_id', 'message': 'Client required'})
        return errors


# ==================== Stage Router ====================

class StageRouter(BaseResourceRouter):
    """Auto-generates Project Stage CRUD endpoints"""
    model = ProjectStage
    entity_name = "Stage"
    searchable_fields = ['name']

    @classmethod
    def schema(cls, obj):
        """Schema for Stage responses"""
        return {
            'id': obj.id,
            'project_id': obj.project_id,
            'name': obj.name,
            'description': obj.description if hasattr(obj, 'description') else None,
            'sequence': obj.sequence if hasattr(obj, 'sequence') else 0,
            'status': obj.status if hasattr(obj, 'status') else 'pending',
            'start_date': obj.start_date.isoformat() if hasattr(obj, 'start_date') and obj.start_date else None,
            'end_date': obj.end_date.isoformat() if hasattr(obj, 'end_date') and obj.end_date else None,
            'percentage_complete': obj.percentage_complete if hasattr(obj, 'percentage_complete') else 0,
            'budget_amount': float(obj.budget_amount) if hasattr(obj, 'budget_amount') and obj.budget_amount else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Stage creation"""
        errors = []
        if not data.get('project_id'):
            errors.append({'field': 'project_id', 'message': 'Project ID required'})
        if not data.get('name'):
            errors.append({'field': 'name', 'message': 'Stage name required'})
        return errors


# ==================== Task Model Router ====================

class TaskModelRouter(BaseResourceRouter):
    """Auto-generates Task Model CRUD endpoints"""
    model = ProjectTask
    entity_name = "Task"
    searchable_fields = ['title', 'description']

    @classmethod
    def schema(cls, obj):
        """Schema for Task responses"""
        return {
            'id': obj.id,
            'project_id': obj.project_id if hasattr(obj, 'project_id') else None,
            'title': obj.title,
            'description': obj.description if hasattr(obj, 'description') else None,
            'status': obj.status if hasattr(obj, 'status') else 'open',
            'priority': obj.priority if hasattr(obj, 'priority') else 'medium',
            'assigned_to': obj.assigned_to if hasattr(obj, 'assigned_to') else None,
            'start_date': obj.start_date.isoformat() if hasattr(obj, 'start_date') and obj.start_date else None,
            'due_date': obj.due_date.isoformat() if hasattr(obj, 'due_date') and obj.due_date else None,
            'created_by': obj.created_by if hasattr(obj, 'created_by') else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Task creation"""
        errors = []
        if not data.get('title'):
            errors.append({'field': 'title', 'message': 'Task title required'})
        if not data.get('project_id'):
            errors.append({'field': 'project_id', 'message': 'Project ID required'})
        return errors


# ==================== Register Routers ====================

def register_project_routers(app):
    """Register all project management routers with Flask app"""
    # Projects
    project_bp = ProjectRouter.create_blueprint(url_prefix='/api/projects')
    app.register_blueprint(project_bp)

    # Stages
    stage_bp = StageRouter.create_blueprint(url_prefix='/api/projects/stages')
    app.register_blueprint(stage_bp)

    # Tasks
    task_bp = TaskModelRouter.create_blueprint(url_prefix='/api/projects/tasks')
    app.register_blueprint(task_bp)
