from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from project_management.models.stage import ProjectStage
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, paginated_response

stage_bp = Blueprint('stages', __name__)


@stage_bp.route('/projects/<int:project_id>/stages', methods=['GET'])
@jwt_required()
def get_project_stages(project_id):
    """Get all stages for a project"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        stages = ProjectStage.query.filter_by(
            project_id=project_id,
            company_id=user.company_id
        ).all()

        data = [stage.to_dict() for stage in stages]
        return success_response(data, "Project stages retrieved")

    except Exception as e:
        return error_response(str(e), 500)


@stage_bp.route('/projects/<int:project_id>/stages', methods=['POST'])
@jwt_required()
def create_stage(project_id):
    """Create a new project stage"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()

        # Validation
        if not data.get('name'):
            return error_response("Stage name is required", 400)
        if data.get('billing_percentage', 0) < 0 or data.get('billing_percentage', 0) > 100:
            return error_response("Billing percentage must be between 0 and 100", 400)

        stage = ProjectStage(
            project_id=project_id,
            name=data['name'],
            description=data.get('description'),
            percentage_complete=data.get('percentage_complete', 0),
            billing_percentage=data.get('billing_percentage', 0),
            planned_start_date=data.get('planned_start_date'),
            planned_end_date=data.get('planned_end_date'),
            status=data.get('status', 'not_started'),
            company_id=user.company_id
        )

        db.session.add(stage)
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='ProjectStage',
            entity_id=stage.id,
            action='create',
            description=f'Created stage {stage.name}'
        )

        return success_response(stage.to_dict(), "Stage created", 201)

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@stage_bp.route('/projects/<int:project_id>/stages/<int:stage_id>', methods=['PUT'])
@jwt_required()
def update_stage(project_id, stage_id):
    """Update a project stage"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        stage = ProjectStage.query.filter_by(
            id=stage_id,
            project_id=project_id,
            company_id=user.company_id
        ).first()

        if not stage:
            return error_response("Stage not found", 404)

        data = request.get_json()

        # Update fields
        if 'name' in data:
            stage.name = data['name']
        if 'description' in data:
            stage.description = data['description']
        if 'percentage_complete' in data:
            stage.percentage_complete = min(100, max(0, data['percentage_complete']))
        if 'billing_percentage' in data:
            stage.billing_percentage = min(100, max(0, data['billing_percentage']))
        if 'status' in data:
            stage.status = data['status']
        if 'actual_start_date' in data:
            stage.actual_start_date = data['actual_start_date']
        if 'actual_end_date' in data:
            stage.actual_end_date = data['actual_end_date']

        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='ProjectStage',
            entity_id=stage.id,
            action='update',
            description=f'Updated stage {stage.name}'
        )

        return success_response(stage.to_dict(), "Stage updated")

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@stage_bp.route('/projects/<int:project_id>/stages/<int:stage_id>', methods=['DELETE'])
@jwt_required()
def delete_stage(project_id, stage_id):
    """Delete a project stage"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        stage = ProjectStage.query.filter_by(
            id=stage_id,
            project_id=project_id,
            company_id=user.company_id
        ).first()

        if not stage:
            return error_response("Stage not found", 404)

        db.session.delete(stage)
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='ProjectStage',
            entity_id=stage_id,
            action='delete',
            description=f'Deleted stage {stage.name}'
        )

        return success_response(None, "Stage deleted")

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@stage_bp.route('/projects/<int:project_id>/billing-schedule', methods=['GET'])
@jwt_required()
def get_billing_schedule(project_id):
    """Get billing schedule for project based on stages"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        from finance_management.models.invoice import Invoice

        stages = ProjectStage.query.filter_by(
            project_id=project_id,
            company_id=user.company_id
        ).order_by(ProjectStage.id).all()

        # Calculate billing amounts for each stage
        project = db.session.query(db.func.sum(Invoice.total)).filter_by(
            project_id=project_id,
            company_id=user.company_id
        ).scalar() or 0

        schedule = []
        for stage in stages:
            schedule.append({
                'stage_id': stage.id,
                'stage_name': stage.name,
                'planned_invoice_date': stage.planned_invoice_date.isoformat() if stage.planned_invoice_date else None,
                'actual_invoice_date': stage.actual_invoice_date.isoformat() if stage.actual_invoice_date else None,
                'billing_percentage': stage.billing_percentage,
                'planned_amount': project * (stage.billing_percentage / 100),
                'status': stage.status
            })

        return success_response(schedule, "Billing schedule retrieved")

    except Exception as e:
        return error_response(str(e), 500)
