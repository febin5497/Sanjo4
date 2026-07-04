
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

document_bp = Blueprint("document", __name__)


@document_bp.route("/document", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "document_management",
        "status": "working"
    })
