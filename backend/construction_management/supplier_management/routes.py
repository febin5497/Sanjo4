from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from user_management.models import User
from supplier_management.models import Supplier

supplier_bp = Blueprint('suppliers', __name__, url_prefix='/api/suppliers')


def validate_supplier_data(data):
    """Validate supplier input data"""
    errors = []

    if not data.get('name') or len(data.get('name', '').strip()) == 0:
        errors.append("Supplier name is required")
    elif len(data['name']) > 150:
        errors.append("Supplier name must be less than 150 characters")

    if data.get('email'):
        if '@' not in data['email']:
            errors.append("Invalid email format")
        elif len(data['email']) > 100:
            errors.append("Email must be less than 100 characters")

    if data.get('phone') and len(data.get('phone', '')) > 20:
        errors.append("Phone number must be less than 20 characters")

    if data.get('tax_id') and len(data.get('tax_id', '')) > 50:
        errors.append("Tax ID must be less than 50 characters")

    return errors


# ============================================
# GET ALL SUPPLIERS
# ============================================
@supplier_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_suppliers():
    """Get all suppliers for current company with pagination and filtering"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.company_id:
            return jsonify({"error": "Unauthorized"}), 401

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', None, type=str)
        is_active = request.args.get('is_active', None, type=str)

        if page <= 0 or per_page <= 0:
            return jsonify({"error": "Page and per_page must be positive integers"}), 400

        query = Supplier.query

        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Supplier.name.ilike(f"%{search}%"),
                    Supplier.email.ilike(f"%{search}%"),
                    Supplier.phone.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)

        # Apply pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "success": True,
            "data": [s.to_dict() for s in paginated.items],
            "pagination": {
                "page": paginated.page,
                "per_page": paginated.per_page,
                "total": paginated.total,
                "pages": paginated.pages
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# GET SUPPLIER BY ID
# ============================================
@supplier_bp.route('/<int:supplier_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_supplier(supplier_id):
    """Get supplier by ID"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        supplier = Supplier.query.filter_by(id=supplier_id).first()

        if not supplier:
            return jsonify({"success": False, "error": "Supplier not found"}), 404

        return jsonify({"success": True, "data": supplier.to_dict()}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# CREATE SUPPLIER
# ============================================
@supplier_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_supplier():
    """Create a new supplier"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate input
        errors = validate_supplier_data(data)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # Create supplier
        supplier = Supplier(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            tax_id=data.get('tax_id'),
            bank_account=data.get('bank_account'),
            contact_person=data.get('contact_person'),
            contact_phone=data.get('contact_phone'),
            notes=data.get('notes'),
            is_active=data.get('is_active', True)
        )

        db.session.add(supplier)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Supplier created successfully",
            "data": supplier.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# UPDATE SUPPLIER
# ============================================
@supplier_bp.route('/<int:supplier_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_supplier(supplier_id):
    """Update supplier"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        supplier = Supplier.query.filter_by(id=supplier_id).first()

        if not supplier:
            return jsonify({"success": False, "error": "Supplier not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate if name is being updated
        if 'name' in data:
            errors = validate_supplier_data({'name': data['name']})
            if errors:
                return jsonify({"success": False, "errors": errors}), 400

        # Update fields
        supplier.name = data.get('name', supplier.name)
        supplier.email = data.get('email', supplier.email)
        supplier.phone = data.get('phone', supplier.phone)
        supplier.address = data.get('address', supplier.address)
        supplier.tax_id = data.get('tax_id', supplier.tax_id)
        supplier.bank_account = data.get('bank_account', supplier.bank_account)
        supplier.contact_person = data.get('contact_person', supplier.contact_person)
        supplier.contact_phone = data.get('contact_phone', supplier.contact_phone)
        supplier.notes = data.get('notes', supplier.notes)

        if 'is_active' in data:
            supplier.is_active = data['is_active']

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Supplier updated successfully",
            "data": supplier.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# DELETE SUPPLIER
# ============================================
@supplier_bp.route('/<int:supplier_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_supplier(supplier_id):
    """Delete supplier"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        supplier = Supplier.query.filter_by(id=supplier_id).first()

        if not supplier:
            return jsonify({"success": False, "error": "Supplier not found"}), 404

        # Check if supplier has purchases
        if len(supplier.purchases) > 0:
            return jsonify({
                "success": False,
                "error": "Cannot delete supplier with existing purchases. Mark as inactive instead."
            }), 400

        db.session.delete(supplier)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Supplier deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
