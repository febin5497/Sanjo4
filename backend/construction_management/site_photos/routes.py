
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

site_photos_bp = Blueprint("site_photos", __name__)


@site_photos_bp.route("/site_photos", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "site_photos",
        "status": "working"
    })
