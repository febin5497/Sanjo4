
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

location_mapping_bp = Blueprint("location_mapping", __name__)


@location_mapping_bp.route("/location_mapping", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "location_mapping",
        "status": "working"
    })
