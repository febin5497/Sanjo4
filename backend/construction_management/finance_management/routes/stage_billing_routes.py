import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from extensions import db
from project_management.models.stage import ProjectStage
from user_management.models import User
from project_management.models.models import Project
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, not_found_response, paginated_response, server_error_response

logger = logging.getLogger(__name__)

stage_billing_bp = Blueprint('stage_billing', __name__)


# ✅ Get all stages for a project
@stage_billing_bp.route('/projects/<int:project_id>/stages', methods=['GET'])
@jwt_required()
def get_project_stages(project_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project")

        stages = ProjectStage.query.filter_by(project_id=project_id).order_by(ProjectStage.stage_number).all()

        data = [stage.to_dict() for stage in stages]

        return success_response(data, "Project stages retrieved", status_code=200)
    except Exception as e:
        logger.error(f"Error fetching stages for project {project_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve project stages")


# ✅ Create new stage
@stage_billing_bp.route('/projects/<int:project_id>/stages', methods=['POST'])
@jwt_required()
def create_project_stage(project_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project")

        # Validation
        errors = []
        if not data.get('stage_name'):
            errors.append({"field": "stage_name", "message": "Stage name is required"})
        if data.get('billing_percentage') is None:
            errors.append({"field": "billing_percentage", "message": "Billing percentage is required"})
        elif not (0 < float(data.get('billing_percentage', 0)) <= 100):
            errors.append({"field": "billing_percentage", "message": "Billing percentage must be between 0 and 100"})
        if not data.get('stage_number'):
            errors.append({"field": "stage_number", "message": "Stage number is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Check total percentage doesn't exceed 100%
        existing_total = db.session.query(db.func.sum(ProjectStage.billing_percentage)).filter_by(
            project_id=project_id
        ).scalar() or 0
        new_total = existing_total + float(data.get('billing_percentage', 0))

        if new_total > 100:
            return error_response(f"Total billing percentage would exceed 100% (current: {existing_total}%, new: {new_total}%)", status_code=400)

        # Create stage
        stage = ProjectStage(
            project_id=project_id,
            stage_number=data.get('stage_number'),
            stage_name=data.get('stage_name'),
            description=data.get('description'),
            billing_percentage=float(data.get('billing_percentage')),
            milestone_date=datetime.strptime(data['milestone_date'], '%Y-%m-%d').date() if data.get('milestone_date') else None,
            planned_invoice_date=datetime.strptime(data['planned_invoice_date'], '%Y-%m-%d').date() if data.get('planned_invoice_date') else None,
            status=data.get('status', 'draft'),
            created_by_id=user_id
        )

        db.session.add(stage)
        db.session.commit()

        log_entity_action(user_id, 'ProjectStage', stage.id, 'CREATE', f"Created stage: {stage.stage_name}")

        return success_response(stage.to_dict(), "Stage created successfully", status_code=201)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating stage for project {project_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create stage")


# ✅ Update stage
@stage_billing_bp.route('/projects/<int:project_id>/stages/<int:stage_id>', methods=['PUT'])
@jwt_required()
def update_project_stage(project_id, stage_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        stage = ProjectStage.query.get(stage_id)
        if not stage or stage.project_id != project_id:
            return not_found_response("Stage")

        # Check if new percentage exceeds 100%
        if data.get('billing_percentage') is not None:
            new_percentage = float(data.get('billing_percentage'))
            existing_total = db.session.query(db.func.sum(ProjectStage.billing_percentage)).filter_by(
                project_id=project_id
            ).filter(ProjectStage.id != stage_id).scalar() or 0
            new_total = existing_total + new_percentage

            if new_total > 100:
                return error_response(f"Total billing percentage would exceed 100% (total would be: {new_total}%)", status_code=400)

            stage.billing_percentage = new_percentage

        # Update fields
        if data.get('stage_name'):
            stage.stage_name = data.get('stage_name')
        if data.get('description') is not None:
            stage.description = data.get('description')
        if data.get('stage_number'):
            stage.stage_number = data.get('stage_number')
        if data.get('status'):
            stage.status = data.get('status')
        if data.get('milestone_date'):
            stage.milestone_date = datetime.strptime(data['milestone_date'], '%Y-%m-%d').date()
        if data.get('planned_invoice_date'):
            stage.planned_invoice_date = datetime.strptime(data['planned_invoice_date'], '%Y-%m-%d').date()
        if data.get('actual_invoice_date'):
            stage.actual_invoice_date = datetime.strptime(data['actual_invoice_date'], '%Y-%m-%d').date()

        stage.updated_at = datetime.utcnow()
        db.session.commit()

        log_entity_action(user_id, 'ProjectStage', stage.id, 'UPDATE', f"Updated stage: {stage.stage_name}")

        return success_response(stage.to_dict(), "Stage updated successfully", status_code=200)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating stage {stage_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update stage")


# ✅ Delete stage
@stage_billing_bp.route('/projects/<int:project_id>/stages/<int:stage_id>', methods=['DELETE'])
@jwt_required()
def delete_project_stage(project_id, stage_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        stage = ProjectStage.query.get(stage_id)
        if not stage or stage.project_id != project_id:
            return not_found_response("Stage")

        stage_name = stage.stage_name
        db.session.delete(stage)
        db.session.commit()

        log_entity_action(user_id, 'ProjectStage', stage_id, 'DELETE', f"Deleted stage: {stage_name}")

        return success_response({"id": stage_id}, "Stage deleted successfully", status_code=200)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting stage {stage_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete stage")


# ✅ Get billing schedule for project
@stage_billing_bp.route('/billing-schedule', methods=['GET'])
@jwt_required()
def get_billing_schedule():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        project_id = request.args.get('project_id', None, type=int)

        if not project_id:
            return error_response("project_id is required", status_code=400)

        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project")

        stages = ProjectStage.query.filter_by(project_id=project_id).order_by(ProjectStage.stage_number).all()

        schedule_data = {
            "project_id": project_id,
            "project_name": project.name if project else None,
            "total_billing_percentage": sum(s.billing_percentage for s in stages),
            "stages": [
                {
                    "id": stage.id,
                    "stage_number": stage.stage_number,
                    "stage_name": stage.stage_name,
                    "billing_percentage": stage.billing_percentage,
                    "milestone_date": stage.milestone_date.isoformat() if stage.milestone_date else None,
                    "planned_invoice_date": stage.planned_invoice_date.isoformat() if stage.planned_invoice_date else None,
                    "actual_invoice_date": stage.actual_invoice_date.isoformat() if stage.actual_invoice_date else None,
                    "status": stage.status,
                }
                for stage in stages
            ]
        }

        return success_response(schedule_data, "Billing schedule retrieved", status_code=200)
    except Exception as e:
        logger.error(f"Error fetching billing schedule: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve billing schedule")
