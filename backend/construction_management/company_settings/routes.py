
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from company_settings.models import Company, CompanySettings
from extensions import db

company_settings_bp = Blueprint("company_settings", __name__)


@company_settings_bp.route("", methods=["GET"])
@jwt_required()
def get_company():
    """Get company details."""
    try:
        company = Company.query.first()
        if not company:
            return jsonify({
                "success": False,
                "error": "Company not found"
            }), 404

        return jsonify({
            "success": True,
            "data": company.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@company_settings_bp.route("", methods=["PUT"])
@jwt_required()
def update_company():
    """Update company settings including tax and GST."""
    try:
        user_id = get_jwt_identity()
        company = Company.query.first()

        if not company:
            return jsonify({
                "success": False,
                "error": "Company not found"
            }), 404

        data = request.get_json()

        # Update fields if provided
        if "name" in data:
            company.name = data["name"]
        if "email" in data:
            company.email = data["email"]
        if "phone" in data:
            company.phone = data["phone"]
        if "address" in data:
            company.address = data["address"]
        if "logo_url" in data:
            company.logo_url = data["logo_url"]
        if "tax_percentage" in data:
            company.tax_percentage = float(data["tax_percentage"])
        if "gst_number" in data:
            company.gst_number = data["gst_number"]

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Company settings updated successfully",
            "data": company.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@company_settings_bp.route("/company_settings", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return jsonify({
        "module": "company_settings",
        "status": "working"
    })
