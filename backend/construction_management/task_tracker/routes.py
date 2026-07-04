
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

task_tracker_bp = Blueprint("task_tracker", __name__)


@task_tracker_bp.route("/task_tracker", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "task_tracker",
        "status": "working"
    })
