"""
Task Management Routes
Handles CRUD operations for project tasks and task-staff assignments
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime, date
from project_management.models import ProjectTask, ProjectAssignment
from project_management.models.task_assignment import TaskStaffAssignment
from staff_management.models import Staff
from utils.response_formatter import (
    success_response, error_response, paginated_response,
    not_found_response, server_error_response
)
from admin_management.utils.activity_logger import log_entity_action

task_bp = Blueprint("tasks", __name__, url_prefix="/api/projects")
task_bp.strict_slashes = False


# ============================================
# VALIDATION HELPERS
# ============================================
def validate_task_data(data):
    """Validate task input data"""
    errors = []

    if not data.get('task_name') or len(data.get('task_name', '').strip()) == 0:
        errors.append("Task name is required")
    elif len(data['task_name']) > 200:
        errors.append("Task name must be less than 200 characters")

    if not data.get('start_date'):
        errors.append("Start date is required")
    else:
        try:
            datetime.strptime(data['start_date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid start date format. Use YYYY-MM-DD")

    if not data.get('end_date'):
        errors.append("End date is required")
    else:
        try:
            datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid end date format. Use YYYY-MM-DD")

    if data.get('start_date') and data.get('end_date'):
        try:
            start = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            if end < start:
                errors.append("End date must be after start date")
        except:
            pass

    if data.get('progress'):
        try:
            progress = float(data['progress'])
            if not (0 <= progress <= 100):
                errors.append("Progress must be between 0 and 100")
        except (ValueError, TypeError):
            errors.append("Progress must be a valid number")

    if data.get('status') and data['status'] not in ['todo', 'in-progress', 'done', 'blocked']:
        errors.append("Status must be one of: todo, in-progress, done, blocked")

    return errors


# ============================================
# TASK MANAGEMENT ENDPOINTS
# ============================================

@task_bp.route('/<int:project_id>/tasks', methods=['GET'])
@jwt_required()
def get_project_tasks(project_id):
    """Get all tasks for a project with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status', None)
        sort_by = request.args.get('sort_by', 'order_index')  # order_index, start_date, priority

        # Query tasks for the project
        query = ProjectTask.query.filter_by(project_id=project_id)

        # Apply status filter if provided
        if status_filter:
            query = query.filter_by(status=status_filter)

        # Apply sorting
        if sort_by == 'start_date':
            query = query.order_by(ProjectTask.start_date)
        elif sort_by == 'priority':
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            # Note: SQLAlchemy doesn't directly support priority ordering, using order_index as default
            query = query.order_by(ProjectTask.order_index)
        else:
            query = query.order_by(ProjectTask.order_index)

        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return paginated_response(
            items=[task.to_dict() for task in paginated.items],
            page=page,
            per_page=per_page,
            total=paginated.total,
            message="Tasks retrieved successfully"
        )

    except Exception as e:
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task_detail(project_id, task_id):
    """Get detailed information about a specific task"""
    try:
        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()

        if not task:
            return not_found_response("Task not found")

        return success_response(data=task.to_dict(), message="Task retrieved successfully")

    except Exception as e:
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(project_id):
    """Create a new task for a project"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # Validate input
        errors = validate_task_data(data)
        if errors:
            return error_response(errors)

        # Create task
        task = ProjectTask(
            project_id=project_id,
            company_id=data.get('company_id'),  # Should be passed from frontend
            task_name=data['task_name'],
            description=data.get('description'),
            task_type=data.get('task_type', 'Activity'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'todo'),
            progress=float(data.get('progress', 0)),
            priority=data.get('priority', 'medium'),
            order_index=data.get('order_index', 0),
            created_by_user_id=user_id
        )

        db.session.add(task)
        db.session.commit()

        # Log activity
        log_entity_action('ProjectTask', task.id, 'CREATE', user_id, {
            'task_name': task.task_name,
            'start_date': task.start_date.isoformat(),
            'end_date': task.end_date.isoformat()
        })

        return success_response(
            data=task.to_dict(),
            status_code=201,
            message="Task created successfully"
        )

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(project_id, task_id):
    """Update task details"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()
        if not task:
            return not_found_response("Task not found")

        # Validate if dates are provided
        if 'start_date' in data or 'end_date' in data:
            errors = validate_task_data({
                'task_name': data.get('task_name', task.task_name),
                'start_date': data.get('start_date', task.start_date.isoformat()),
                'end_date': data.get('end_date', task.end_date.isoformat()),
                'progress': data.get('progress', task.progress),
                'status': data.get('status', task.status)
            })
            if errors:
                return error_response(errors)

        # Update fields
        if 'task_name' in data:
            task.task_name = data['task_name']
        if 'description' in data:
            task.description = data['description']
        if 'task_type' in data:
            task.task_type = data['task_type']
        if 'start_date' in data:
            task.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            task.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'status' in data:
            task.status = data['status']
        if 'progress' in data:
            task.progress = float(data['progress'])
        if 'priority' in data:
            task.priority = data['priority']
        if 'order_index' in data:
            task.order_index = data['order_index']

        task.updated_at = datetime.utcnow()
        db.session.commit()

        # Log activity
        log_entity_action('ProjectTask', task.id, 'UPDATE', user_id, {
            'fields_updated': list(data.keys())
        })

        return success_response(data=task.to_dict(), message="Task updated successfully")

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(project_id, task_id):
    """Delete a task (cascade deletes assignments)"""
    try:
        user_id = get_jwt_identity()
        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()

        if not task:
            return not_found_response("Task not found")

        task_name = task.task_name
        db.session.delete(task)
        db.session.commit()

        # Log activity
        log_entity_action('ProjectTask', task_id, 'DELETE', user_id, {
            'task_name': task_name
        })

        return success_response(message="Task deleted successfully")

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


# ============================================
# TASK STAFF ASSIGNMENT ENDPOINTS
# ============================================

@task_bp.route('/<int:project_id>/tasks/<int:task_id>/assign-staff', methods=['POST'])
@jwt_required()
def assign_staff_to_task(project_id, task_id):
    """Assign a staff member to a task"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        staff_id = data.get('staff_id')

        if not staff_id:
            return error_response(["staff_id is required"])

        # Verify task exists
        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()
        if not task:
            return not_found_response("Task not found")

        # Verify staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff member not found")

        # Check if already assigned and active
        existing = TaskStaffAssignment.query.filter_by(
            task_id=task_id,
            staff_id=staff_id,
            removed_on=None
        ).first()

        if existing:
            return error_response(["Staff member already assigned to this task"])

        # Create assignment
        assignment = TaskStaffAssignment(
            task_id=task_id,
            staff_id=staff_id,
            company_id=task.company_id,
            role_on_task=data.get('role_on_task'),
            hours_allocated=data.get('hours_allocated'),
            notes=data.get('notes'),
            assigned_by_user_id=user_id
        )

        db.session.add(assignment)
        db.session.commit()

        # Log activity
        log_entity_action('TaskStaffAssignment', assignment.id, 'CREATE', user_id, {
            'task_id': task_id,
            'staff_id': staff_id,
            'staff_name': f"{staff.first_name} {staff.last_name}"
        })

        return success_response(
            data=assignment.to_dict(),
            status_code=201,
            message=f"Staff member assigned to task successfully"
        )

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks/<int:task_id>/unassign-staff', methods=['POST'])
@jwt_required()
def unassign_staff_from_task(project_id, task_id):
    """Remove a staff member from a task (soft delete)"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        staff_id = data.get('staff_id')

        if not staff_id:
            return error_response(["staff_id is required"])

        # Verify task exists
        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()
        if not task:
            return not_found_response("Task not found")

        # Find active assignment
        assignment = TaskStaffAssignment.query.filter_by(
            task_id=task_id,
            staff_id=staff_id,
            removed_on=None
        ).first()

        if not assignment:
            return not_found_response("Staff assignment not found")

        # Soft delete by setting removed_on
        assignment.removed_on = datetime.utcnow()
        db.session.commit()

        # Log activity
        staff = Staff.query.get(staff_id)
        log_entity_action('TaskStaffAssignment', assignment.id, 'DELETE', user_id, {
            'task_id': task_id,
            'staff_id': staff_id,
            'staff_name': f"{staff.first_name} {staff.last_name}" if staff else "Unknown"
        })

        return success_response(message="Staff member removed from task successfully")

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks/<int:task_id>/staff', methods=['GET'])
@jwt_required()
def get_task_staff(project_id, task_id):
    """Get all staff assigned to a task (active assignments)"""
    try:
        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()
        if not task:
            return not_found_response("Task not found")

        # Get active assignments
        assignments = TaskStaffAssignment.query.filter_by(
            task_id=task_id,
            removed_on=None
        ).all()

        return success_response(
            data=[a.to_dict() for a in assignments],
            message="Task staff retrieved successfully"
        )

    except Exception as e:
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/tasks/<int:task_id>/bulk-assign', methods=['POST'])
@jwt_required()
def bulk_assign_staff_to_task(project_id, task_id):
    """Assign multiple staff members to a task at once"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        staff_ids = data.get('staff_ids', [])

        if not isinstance(staff_ids, list) or len(staff_ids) == 0:
            return error_response(["staff_ids must be a non-empty array"])

        # Verify task exists
        task = ProjectTask.query.filter_by(id=task_id, project_id=project_id).first()
        if not task:
            return not_found_response("Task not found")

        assignments = []
        errors = []

        for staff_id in staff_ids:
            try:
                # Verify staff exists
                staff = Staff.query.get(staff_id)
                if not staff:
                    errors.append(f"Staff ID {staff_id} not found")
                    continue

                # Check if already assigned
                existing = TaskStaffAssignment.query.filter_by(
                    task_id=task_id,
                    staff_id=staff_id,
                    removed_on=None
                ).first()

                if existing:
                    errors.append(f"Staff {staff.first_name} {staff.last_name} already assigned")
                    continue

                # Create assignment
                assignment = TaskStaffAssignment(
                    task_id=task_id,
                    staff_id=staff_id,
                    company_id=task.company_id,
                    assigned_by_user_id=user_id
                )
                db.session.add(assignment)
                assignments.append(assignment)

            except Exception as e:
                errors.append(f"Error assigning staff {staff_id}: {str(e)}")

        db.session.commit()

        # Log activity
        log_entity_action('TaskStaffAssignment', task_id, 'BULK_CREATE', user_id, {
            'count': len(assignments),
            'staff_ids': staff_ids
        })

        return success_response(
            data={
                'assigned': [a.to_dict() for a in assignments],
                'errors': errors
            },
            status_code=201,
            message=f"Assigned {len(assignments)} staff member(s) to task"
        )

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


# ============================================
# PROJECT-LEVEL STAFF ASSIGNMENT ENDPOINTS
# ============================================

@task_bp.route('/<int:project_id>/assign-staff', methods=['POST'])
@jwt_required()
def assign_staff_to_project(project_id):
    """Assign staff to a project"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        staff_id = data.get('staff_id')

        if not staff_id:
            return error_response(["staff_id is required"])

        # Verify project exists
        from project_management.models.models import Project
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project not found")

        # Verify staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff not found")

        # Check if already assigned (use ProjectAssignment if available)
        from project_management.models.project_assignment import ProjectAssignment
        existing = ProjectAssignment.query.filter_by(
            project_id=project_id,
            staff_id=staff_id
        ).first()

        if existing:
            return error_response(["Staff is already assigned to this project"], 400)

        # Create assignment
        assignment = ProjectAssignment(
            project_id=project_id,
            staff_id=staff_id,
            company_id=project.company_id,
            assigned_by_user_id=user_id
        )
        db.session.add(assignment)

        # Also create history record
        from project_management.models.models import ProjectStaffHistory
        history = ProjectStaffHistory(
            project_id=project_id,
            staff_id=staff_id
        )
        db.session.add(history)
        db.session.commit()

        # Log activity
        log_entity_action('ProjectAssignment', project_id, 'CREATE', user_id, {
            'staff_id': staff_id
        })

        return success_response(
            data=assignment.to_dict() if hasattr(assignment, 'to_dict') else {
                'id': assignment.id,
                'project_id': assignment.project_id,
                'staff_id': assignment.staff_id
            },
            status_code=201,
            message="Staff assigned to project successfully"
        )

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/unassign-staff', methods=['POST'])
@jwt_required()
def unassign_staff_from_project(project_id):
    """Unassign staff from a project"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        staff_id = data.get('staff_id')

        if not staff_id:
            return error_response(["staff_id is required"])

        # Verify project exists
        from project_management.models.models import Project
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project not found")

        # Find assignment
        from project_management.models.project_assignment import ProjectAssignment
        assignment = ProjectAssignment.query.filter_by(
            project_id=project_id,
            staff_id=staff_id
        ).first()

        if not assignment:
            return error_response(["Staff is not assigned to this project"], 400)

        # Delete assignment
        db.session.delete(assignment)

        # Update history record with unassigned_date
        from project_management.models.models import ProjectStaffHistory
        from datetime import datetime
        history_record = ProjectStaffHistory.query.filter_by(
            project_id=project_id,
            staff_id=staff_id,
            unassigned_date=None  # Get the active record
        ).first()

        if history_record:
            history_record.unassigned_date = datetime.utcnow()
            db.session.add(history_record)

        db.session.commit()

        # Log activity
        log_entity_action('ProjectAssignment', project_id, 'DELETE', user_id, {
            'staff_id': staff_id
        })

        return success_response(
            message="Staff unassigned from project successfully"
        )

    except Exception as e:
        db.session.rollback()
        return server_error_response(str(e))


@task_bp.route('/<int:project_id>/history', methods=['GET'])
@jwt_required()
def get_project_staff_history(project_id):
    """Get staff assignment history for a project"""
    try:
        user_id = get_jwt_identity()

        # Verify project exists
        from project_management.models.models import Project, ProjectStaffHistory
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project not found")

        # Get all history records for this project
        history_records = ProjectStaffHistory.query.filter_by(
            project_id=project_id
        ).order_by(ProjectStaffHistory.assigned_date.desc()).all()

        # Enrich with staff details
        from staff_management.models import Staff
        enriched_history = []
        for record in history_records:
            staff = Staff.query.get(record.staff_id)
            if staff:
                enriched_history.append({
                    'id': record.id,
                    'staff_id': record.staff_id,
                    'staff_name': f"{staff.first_name} {staff.last_name}",
                    'staff_email': staff.email,
                    'staff_role': staff.role,
                    'staff_department': staff.department,
                    'assigned_date': record.assigned_date.strftime('%Y-%m-%d %H:%M:%S') if record.assigned_date else None,
                    'unassigned_date': record.unassigned_date.strftime('%Y-%m-%d %H:%M:%S') if record.unassigned_date else None,
                    'is_active': record.unassigned_date is None
                })

        return success_response(
            data=enriched_history,
            message="Project staff history retrieved successfully"
        )

    except Exception as e:
        return server_error_response(str(e))
