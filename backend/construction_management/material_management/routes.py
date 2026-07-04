from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from material_management.models import Material
from utils.response_formatter import (
    success_response, error_response, paginated_response,
    server_error_response, not_found_response
)
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)

material_bp = Blueprint("material", __name__, url_prefix="/api/materials")


@material_bp.route("/material", methods=["GET"])
@jwt_required(optional=True)
def health_check():
    return success_response(
        {"module": "material_management", "status": "working"},
        "Material management module is operational"
    )


@material_bp.route("", methods=["GET"])
@jwt_required()
def get_all_materials():
    """Get all materials with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        materials = Material.query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[m.to_dict() for m in materials.items],
            total=materials.total,
            page=page,
            per_page=per_page,
            message="Materials retrieved successfully"
        )
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        logger.error(f"Get all materials error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve materials")


@material_bp.route("/<int:material_id>", methods=["GET"])
@jwt_required()
def get_material(material_id):
    """Get a single material by ID"""
    try:
        material = Material.query.get(material_id)
        if not material:
            return not_found_response("Material", details=f"No material with ID {material_id} found")

        return success_response(material.to_dict(), "Material retrieved successfully")
    except Exception as e:
        logger.error(f"Get material error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve material")


@material_bp.route("", methods=["POST"])
@jwt_required()
def create_material():
    """Create a new material"""
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        data = request.get_json()

        # Validate required fields
        errors = []
        if not data.get("name"):
            errors.append({"field": "name", "message": "Material name is required"})
        if not data.get("quantity"):
            errors.append({"field": "quantity", "message": "Quantity is required"})
        if not data.get("price"):
            errors.append({"field": "price", "message": "Price is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Create new material
        material = Material(
            name=data.get("name"),
            description=data.get("description"),
            quantity=float(data.get("quantity")),
            unit_of_measurement=data.get("unit_of_measurement"),
            price=float(data.get("price")),
            project_id=data.get("project_id")
        )

        db.session.add(material)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Material',
            entity_id=material.id,
            action='CREATE',
            new_values=material.to_dict(),
            entity_name=material.name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(material.to_dict(), "Material created successfully", status_code=201)
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create material error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create material")


@material_bp.route("/<int:material_id>", methods=["PUT"])
@jwt_required()
def update_material(material_id):
    """Update an existing material"""
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        material = Material.query.get(material_id)
        if not material:
            return not_found_response("Material", details=f"No material with ID {material_id} found")

        # Capture old values BEFORE update
        old_values = material.to_dict()

        data = request.get_json()

        # Update fields
        if "name" in data:
            material.name = data["name"]
        if "description" in data:
            material.description = data["description"]
        if "quantity" in data:
            material.quantity = float(data["quantity"])
        if "unit_of_measurement" in data:
            material.unit_of_measurement = data["unit_of_measurement"]
        if "price" in data:
            material.price = float(data["price"])
        if "project_id" in data:
            material.project_id = data["project_id"]

        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Material',
            entity_id=material.id,
            action='UPDATE',
            old_values=old_values,
            new_values=material.to_dict(),
            entity_name=material.name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(material.to_dict(), "Material updated successfully")
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Update material error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to update material")


@material_bp.route("/<int:material_id>", methods=["DELETE"])
@jwt_required()
def delete_material(material_id):
    """Delete a material"""
    try:
        from user_management.models import User
        from admin_management.utils.activity_logger import log_entity_action

        material = Material.query.get(material_id)
        if not material:
            return not_found_response("Material", details=f"No material with ID {material_id} found")

        # Capture data BEFORE delete
        deleted_data = material.to_dict()
        material_name = material.name

        db.session.delete(material)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(user_id),
            company_id=user.company_id if user else None,
            entity_type='Material',
            entity_id=material_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=material_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return success_response(message="Material deleted successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete material error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete material")


@material_bp.route("/use", methods=["POST"])
@jwt_required()
def use_material():
    """Record material usage/deduction"""
    try:
        data = request.get_json()
        material_id = data.get("material_id")
        quantity = data.get("quantity")

        # Validate required fields
        errors = []
        if not material_id:
            errors.append({"field": "material_id", "message": "Material ID is required"})
        if not quantity:
            errors.append({"field": "quantity", "message": "Quantity is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        material = Material.query.get(material_id)
        if not material:
            return not_found_response("Material", details=f"No material with ID {material_id} found")

        material.quantity -= float(quantity)
        db.session.commit()

        return success_response(material.to_dict(), "Material usage recorded successfully")
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Use material error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to record material usage")
