from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from planner_management.models import PlannerTask
from project_management.models.models import Project
from user_management.models import User

planner_bp = Blueprint("planner", __name__, url_prefix="/api/planner")


@planner_bp.route("/projects", methods=["GET"])
@jwt_required()
def list_projects():
    """Get all projects"""
    projects = Project.query.all()

    result = []
    for project in projects:
        result.append({
            "id": project.id,
            "name": project.name,
            "company_id": project.company_id,
            "client_id": project.client_id
        })

    return jsonify(result)


@planner_bp.route("/tasks/<int:project_id>", methods=["GET"])
@jwt_required()
def get_project_tasks(project_id):
    """Get all tasks for a specific project"""
    project = Project.query.get_or_404(project_id)

    tasks = PlannerTask.query.filter_by(project_id=project_id).all()
    return jsonify([task.to_dict() for task in tasks])


@planner_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    """Create a new task"""
    data = request.get_json(silent=True) or {}

    # Validation
    project_id = data.get("project_id")
    task_name = (data.get("task_name") or "").strip()

    if not project_id:
        return jsonify({"error": "project_id is required"}), 400
    if not task_name:
        return jsonify({"error": "task_name is required"}), 400

    # Verify project exists
    project = Project.query.get_or_404(project_id)

    # Parse dates
    try:
        start_date = datetime.fromisoformat(data.get("start_date", "").replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(data.get("end_date", "").replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DD)"}), 400

    if start_date > end_date:
        return jsonify({"error": "start_date must be before end_date"}), 400

    # Create task
    task = PlannerTask(
        project_id=project_id,
        task_name=task_name,
        start_date=start_date,
        end_date=end_date,
        status=data.get("status", "todo"),
        progress=data.get("progress", 0),
        dependencies=data.get("dependencies"),
        description=data.get("description")
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Task created successfully",
        "data": task.to_dict()
    }), 201


@planner_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    """Update an existing task"""
    task = PlannerTask.query.get_or_404(task_id)

    # Verify project exists
    project = Project.query.get_or_404(task.project_id)

    data = request.get_json(silent=True) or {}

    # Update fields if provided
    if "task_name" in data:
        task.task_name = (data["task_name"] or "").strip()

    if "start_date" in data:
        try:
            task.start_date = datetime.fromisoformat(data["start_date"].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({"error": "Invalid start_date format"}), 400

    if "end_date" in data:
        try:
            task.end_date = datetime.fromisoformat(data["end_date"].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return jsonify({"error": "Invalid end_date format"}), 400

    # Validate dates
    if task.start_date > task.end_date:
        return jsonify({"error": "start_date must be before end_date"}), 400

    if "status" in data:
        task.status = data["status"]

    if "progress" in data:
        task.progress = max(0, min(100, data["progress"]))  # Clamp to 0-100

    if "dependencies" in data:
        task.dependencies = data["dependencies"]

    if "description" in data:
        task.description = data["description"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Task updated successfully",
        "data": task.to_dict()
    })


@planner_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    task = PlannerTask.query.get_or_404(task_id)

    # Verify project exists
    project = Project.query.get_or_404(task.project_id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Task deleted successfully"
    })
