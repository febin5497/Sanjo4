import os
from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensions import db
from project_management.models.models import Project, ProjectStaffHistory
from project_management.models.project_assignment import ProjectAssignment
from staff_management.models import Staff
from utils.response_formatter import (
    success_response, error_response, paginated_response,
    server_error_response, not_found_response
)

logger = logging.getLogger(__name__)

project_bp = Blueprint("project", __name__, url_prefix="/api/projects")

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "docx", "xlsx", "glb", "gltf", "obj", "stl", "fbx", "3ds"}

DOC_MAP = {
    "Agreement": "agreement",
    "PLAN": "plan",
    "3D Plan": "three_d_plan",
    "Panchayat Certificate": "panchayat_certificate",
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def project_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "location": p.location,
        "start_date": p.start_date.strftime("%Y-%m-%d") if p.start_date else None,
        "status": p.status,
        "rate_per_sqft": p.rate_per_sqft,
        "square_feet": p.square_feet,
        "client_id": p.client_id,
        "client": getattr(p.client, 'name', None) if p.client else None,
        "company_id": p.company_id,
        "agreement": getattr(p, 'agreement', None),
        "plan": getattr(p, 'plan', None),
        "three_d_plan": getattr(p, 'three_d_plan', None),
        "panchayat_certificate": getattr(p, 'panchayat_certificate', None),
        "latitude": p.latitude,
        "longitude": p.longitude,
    }


# ── GET /api/projects ─────────────────────────────────────────────────────────
@project_bp.route("/", methods=["GET"])
@jwt_required()
def list_projects():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        status_filter = request.args.get("status")
        search = request.args.get("search", "").strip()

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        # Use joinedload to eagerly load client relationship and avoid N+1 queries
        from sqlalchemy.orm import joinedload
        query = Project.query.options(joinedload(Project.client))

        if status_filter:
            query = query.filter(Project.status == status_filter)
        if search:
            query = query.filter(Project.name.ilike(f"%{search}%"))

        paginated = query.order_by(Project.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return paginated_response(
            items=[project_to_dict(p) for p in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Projects retrieved successfully"
        )
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        logger.error(f"Get projects error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve projects")


# ── POST /api/projects ────────────────────────────────────────────────────────
@project_bp.route("/", methods=["POST"])
@jwt_required()
def create_project():
    from user_management.models import User
    from admin_management.utils.activity_logger import log_entity_action

    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user or not user.company_id:
            return error_response("User or company not found", status_code=400)

        data = request.get_json(silent=True) or {}

        name = (data.get("name") or "").strip()
        location = (data.get("location") or "").strip()
        start_date_str = data.get("start_date", "")
        client_id = data.get("client_id")

        # Validate required fields
        errors = []
        if not name:
            errors.append({"field": "name", "message": "Project name is required"})
        if not location:
            errors.append({"field": "location", "message": "Location is required"})
        if not start_date_str:
            errors.append({"field": "start_date", "message": "Start date is required"})
        if not client_id:
            errors.append({"field": "client_id", "message": "Client ID is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            return error_response("Invalid start_date format. Use YYYY-MM-DD", status_code=400)

        project = Project(
            name=name,
            location=location,
            start_date=start_date,
            rate_per_sqft=data.get("rate_per_sqft"),
            square_feet=data.get("square_feet"),
            status=data.get("status", "Not Started"),
            client_id=client_id,
            user_id=int(user_id),
            company_id=user.company_id,
        )

        db.session.add(project)
        db.session.commit()

        # ✅ LOG ACTIVITY
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id,
            entity_type='Project',
            entity_id=project.id,
            action='CREATE',
            new_values=project_to_dict(project),
            entity_name=project.name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(project_to_dict(project), "Project created successfully", status_code=201)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create project error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create project")


# ── GET /api/projects/<id> ────────────────────────────────────────────────────
@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project(project_id):
    try:
        from sqlalchemy.orm import joinedload
        project = Project.query.options(joinedload(Project.client)).get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        return success_response(project_to_dict(project), "Project retrieved successfully")
    except Exception as e:
        logger.error(f"Get project error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve project")


# ── PUT /api/projects/<id> ────────────────────────────────────────────────────
@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def update_project(project_id):
    from user_management.models import User
    from admin_management.utils.activity_logger import log_entity_action

    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        data = request.get_json(silent=True) or {}

        # Capture old values BEFORE update
        old_values = project_to_dict(project)

        if "name" in data:
            project.name = data["name"].strip()
        if "location" in data:
            project.location = data["location"].strip()
        if "start_date" in data:
            try:
                project.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
            except ValueError:
                return error_response("Invalid start_date format. Use YYYY-MM-DD", status_code=400)
        if "rate_per_sqft" in data:
            project.rate_per_sqft = data["rate_per_sqft"]
        if "square_feet" in data:
            project.square_feet = data["square_feet"]
        if "status" in data:
            project.status = data["status"]
        if "client_id" in data:
            project.client_id = data["client_id"]

        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Project',
            entity_id=project.id,
            action='UPDATE',
            old_values=old_values,
            new_values=project_to_dict(project),
            entity_name=project.name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(project_to_dict(project), "Project updated successfully")
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update project error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update project")


# ── DELETE /api/projects/<id> ─────────────────────────────────────────────────
@project_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def delete_project(project_id):
    from user_management.models import User
    from admin_management.utils.activity_logger import log_entity_action

    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        # Capture data BEFORE delete (for audit trail)
        deleted_data = project_to_dict(project)
        project_name = project.name

        db.session.delete(project)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Project',
            entity_id=project_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=project_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Project deleted successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete project error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete project")


# ── POST /api/projects/<id>/upload ────────────────────────────────────────────
@project_bp.route("/<int:project_id>/upload", methods=["POST"])
@jwt_required()
def upload_document(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        doc_type = request.form.get("doc_type", "").strip()
        file = request.files.get("file")

        # Validate required fields
        errors = []
        if not file:
            errors.append({"field": "file", "message": "File is required"})
        if not doc_type:
            errors.append({"field": "doc_type", "message": "Document type is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        if not allowed_file(file.filename):
            return error_response("File type not allowed. Allowed types: pdf, jpg, jpeg, png, docx, xlsx", status_code=400)

        filename = secure_filename(file.filename)
        upload_dir = os.path.join("uploads", "projects", str(project_id))
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, filename))

        col = DOC_MAP.get(doc_type)
        if col:
            setattr(project, col, filename)
            db.session.commit()

        return success_response({"filename": filename}, "File uploaded successfully", status_code=201)
    except OSError as e:
        db.session.rollback()
        return error_response(f"File operation failed: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Upload document error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to upload document")


# ── POST /api/projects/<id>/delete-file ───────────────────────────────────────
@project_bp.route("/<int:project_id>/delete-file", methods=["POST"])
@jwt_required()
def delete_document(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        data = request.get_json(silent=True) or {}
        doc_type = data.get("doc_type", "").strip()

        if not doc_type:
            return error_response("Document type is required", status_code=400)

        col = DOC_MAP.get(doc_type)
        if not col:
            return error_response("Invalid document type", details=f"Document type '{doc_type}' not recognized", status_code=400)

        filename = getattr(project, col)
        if filename:
            path = os.path.join("uploads", "projects", str(project_id), filename)
            if os.path.exists(path):
                os.remove(path)
            setattr(project, col, None)
            db.session.commit()

        return success_response(message="File deleted successfully")
    except OSError as e:
        db.session.rollback()
        return error_response(f"File operation failed: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete document error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete document")


# ── GET /api/projects/<id>/staff-history ──────────────────────────────────────
@project_bp.route("/<int:project_id>/staff-history", methods=["GET"])
@jwt_required()
def get_staff_history(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        assignments = ProjectAssignment.query.filter_by(project_id=project_id).all()

        result = []
        for a in assignments:
            staff = Staff.query.get(a.staff_id)
            result.append({
                "id": a.id,
                "staff_id": a.staff_id,
                "staff_name": staff.name if staff else "Unknown",
                "staff_role": staff.role if staff else "",
                "assigned_on": a.assigned_on.strftime("%Y-%m-%d %H:%M") if a.assigned_on else None,
                "removed_on": a.removed_on.strftime("%Y-%m-%d %H:%M") if a.removed_on else None,
            })

        return success_response(result, "Staff history retrieved successfully")
    except Exception as e:
        logger.error(f"Get staff history error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve staff history")


# ── POST /api/projects/<id>/assign-staff ─────────────────────────────────────
@project_bp.route("/<int:project_id>/assign-staff", methods=["POST"])
@jwt_required()
def assign_staff(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        data = request.get_json(silent=True) or {}
        staff_id = data.get("staff_id")

        if not staff_id:
            return error_response("Staff ID is required", status_code=400)

        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff", details=f"No staff with ID {staff_id} found")

        existing = ProjectAssignment.query.filter_by(
            project_id=project_id, staff_id=staff_id, removed_on=None
        ).first()
        if existing:
            return error_response("Staff already assigned to this project", status_code=400)

        assignment = ProjectAssignment(project_id=project_id, staff_id=staff_id)
        db.session.add(assignment)

        history = ProjectStaffHistory(project_id=project_id, staff_id=staff_id)
        db.session.add(history)
        db.session.commit()

        result = {
            "id": assignment.id,
            "staff_id": staff_id,
            "staff_name": staff.name,
            "staff_role": staff.role,
            "assigned_on": assignment.assigned_on.strftime("%Y-%m-%d %H:%M"),
            "removed_on": None,
        }

        return success_response(result, "Staff assigned successfully", status_code=201)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Assign staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to assign staff")


# ── POST /api/projects/<id>/unassign-staff ────────────────────────────────────
@project_bp.route("/<int:project_id>/unassign-staff", methods=["POST"])
@jwt_required()
def unassign_staff(project_id):
    try:
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project", details=f"No project with ID {project_id} found")

        data = request.get_json(silent=True) or {}
        staff_id = data.get("staff_id")

        if not staff_id:
            return error_response("Staff ID is required", status_code=400)

        assignment = ProjectAssignment.query.filter_by(
            project_id=project_id, staff_id=staff_id, removed_on=None
        ).first()
        if not assignment:
            return not_found_response("Assignment", details="No active staff assignment found for this project")

        now = datetime.utcnow()
        assignment.removed_on = now

        history = ProjectStaffHistory.query.filter_by(
            project_id=project_id, staff_id=staff_id, unassigned_date=None
        ).first()
        if history:
            history.unassigned_date = now

        db.session.commit()
        return success_response(message="Staff unassigned successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unassign staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to unassign staff")


# ── GET /api/projects/<id>/staff ──────────────────────────────────────────────
@project_bp.route("/<int:project_id>/staff", methods=["GET"])
@jwt_required()
def get_project_staff(project_id):
    """Get all staff assigned to a project"""
    try:
        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            return not_found_response("Project not found")

        # Get all active staff assignments for this project
        assignments = ProjectAssignment.query.filter_by(
            project_id=project_id,
            removed_on=None
        ).all()

        # Get staff details for each assignment
        staff_list = []
        for assignment in assignments:
            staff = Staff.query.get(assignment.staff_id)
            if staff:
                staff_list.append({
                    'id': staff.id,
                    'staff_id': staff.id,
                    'first_name': staff.first_name,
                    'last_name': staff.last_name,
                    'email': staff.email,
                    'role': staff.role,
                    'department': staff.department,
                    'assigned_on': assignment.assigned_on.isoformat() if assignment.assigned_on else None,
                    'assignment_id': assignment.id
                })

        return success_response(
            data=staff_list,
            message="Project staff retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Get project staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve project staff")
