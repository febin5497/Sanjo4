from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from user_management.models import User
from supplier_management.models import Supplier
from material_management.models import Material
from purchase_management.models import Purchase, PurchaseItem
from admin_management.utils.activity_logger import log_entity_action

purchase_bp = Blueprint('purchases', __name__, url_prefix='/api/purchases')


def validate_purchase_data(data):
    """Validate purchase input data"""
    errors = []

    if not data.get('supplier_id'):
        errors.append("Supplier ID is required")

    if not data.get('items') or not isinstance(data['items'], list) or len(data['items']) == 0:
        errors.append("At least one purchase item is required")
    else:
        for idx, item in enumerate(data['items']):
            if not item.get('material_id'):
                errors.append(f"Item {idx + 1}: Material ID is required")
            if not item.get('quantity') or float(item['quantity']) <= 0:
                errors.append(f"Item {idx + 1}: Quantity must be greater than 0")
            if not item.get('unit_price') or float(item['unit_price']) < 0:
                errors.append(f"Item {idx + 1}: Unit price must be 0 or greater")

    return errors


def create_cash_transaction(purchase, transaction_type='expense'):
    """Create or update CashTransaction for purchase"""
    try:
        # Import here to avoid circular imports
        from finance_management.models.cash_transaction import CashTransaction

        # Create expense transaction for purchase
        transaction = CashTransaction(
            project_id=purchase.project_id,
            date=datetime.utcnow(),
            type='expense',
            category='Purchase',
            amount=purchase.grand_total,
            description=f"Purchase from {purchase.supplier.name if purchase.supplier else 'Unknown'} - PO: {purchase.po_number}",
            created_by=purchase.user_id
        )

        db.session.add(transaction)
        return True, transaction

    except Exception as e:
        return False, str(e)


# ============================================
# GET ALL PURCHASES
# ============================================
@purchase_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_purchases():
    """Get all purchases for current company with pagination and filtering"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)
        supplier_id = request.args.get('supplier_id', None, type=int)
        project_id = request.args.get('project_id', None, type=int)

        query = Purchase.query

        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if supplier_id:
            query = query.filter_by(supplier_id=supplier_id)
        if project_id:
            query = query.filter_by(project_id=project_id)

        # Order by most recent first
        query = query.order_by(Purchase.purchase_date.desc())

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "success": True,
            "data": [p.to_dict() for p in paginated.items],
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
# GET PURCHASE BY ID (WITH ITEMS)
# ============================================
@purchase_bp.route('/<int:purchase_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_purchase(purchase_id):
    """Get purchase details including all line items"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        purchase = Purchase.query.filter_by(id=purchase_id).first()

        if not purchase:
            return jsonify({"success": False, "error": "Purchase not found"}), 404

        return jsonify({
            "success": True,
            "data": purchase.to_dict(include_items=True)
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# CREATE PURCHASE
# ============================================
@purchase_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_purchase():
    """Create a new purchase order"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate input
        errors = validate_purchase_data(data)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # Verify supplier exists
        supplier = Supplier.query.filter_by(
            id=data['supplier_id']
        ).first()

        if not supplier:
            return jsonify({"success": False, "error": "Supplier not found"}), 404

        # Verify all materials exist
        items_data = data.get('items', [])
        materials = {}

        for item in items_data:
            material = Material.query.get(item['material_id'])
            if not material:
                return jsonify({
                    "success": False,
                    "error": f"Material ID {item['material_id']} not found"
                }), 404
            materials[item['material_id']] = material

        # Create purchase
        purchase = Purchase(
            project_id=data.get('project_id'),
            supplier_id=supplier.id,
            user_id=current_user_id,
            purchase_date=datetime.fromisoformat(data['purchase_date']) if data.get('purchase_date') else datetime.utcnow(),
            expected_delivery_date=datetime.fromisoformat(data['expected_delivery_date']) if data.get('expected_delivery_date') else None,
            po_number=data.get('po_number'),
            notes=data.get('notes'),
            status='pending'  # Starts as pending, needs approval
        )

        # Add items and calculate totals
        total = 0.0
        for item_data in items_data:
            quantity = float(item_data['quantity'])
            unit_price = float(item_data['unit_price'])
            item_total = quantity * unit_price

            purchase_item = PurchaseItem(
                material_id=item_data['material_id'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total
            )

            purchase.items.append(purchase_item)
            total += item_total

        # Set totals
        purchase.total = total
        purchase.tax = float(data.get('tax', 0.0))
        purchase.grand_total = total + purchase.tax

        db.session.add(purchase)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Purchase',
            entity_id=purchase.id,
            action='CREATE',
            new_values=purchase.to_dict(include_items=True),
            entity_name=purchase.po_number if purchase.po_number else f"Purchase #{purchase.id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({
            "success": True,
            "message": "Purchase created successfully. Awaiting approval.",
            "data": purchase.to_dict(include_items=True)
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# UPDATE PURCHASE
# ============================================
@purchase_bp.route('/<int:purchase_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_purchase(purchase_id):
    """Update purchase (only if pending)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        purchase = Purchase.query.filter_by(id=purchase_id).first()

        if not purchase:
            return jsonify({"success": False, "error": "Purchase not found"}), 404

        if purchase.status != 'pending':
            return jsonify({
                "success": False,
                "error": f"Cannot update purchase with status '{purchase.status}'"
            }), 400

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Capture old values BEFORE update
        old_values = purchase.to_dict(include_items=True)

        # Update basic fields
        purchase.po_number = data.get('po_number', purchase.po_number)
        purchase.notes = data.get('notes', purchase.notes)
        purchase.expected_delivery_date = (
            datetime.fromisoformat(data['expected_delivery_date'])
            if data.get('expected_delivery_date')
            else purchase.expected_delivery_date
        )

        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Purchase',
            entity_id=purchase.id,
            action='UPDATE',
            old_values=old_values,
            new_values=purchase.to_dict(include_items=True),
            entity_name=purchase.po_number if purchase.po_number else f"Purchase #{purchase.id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({
            "success": True,
            "message": "Purchase updated successfully",
            "data": purchase.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# APPROVE PURCHASE (UPDATE STATUS + INVENTORY + ACCOUNTING)
# ============================================
@purchase_bp.route('/<int:purchase_id>/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def approve_purchase(purchase_id):
    """Approve purchase - triggers inventory update and accounting transaction"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        purchase = Purchase.query.filter_by(id=purchase_id).first()

        if not purchase:
            return jsonify({"success": False, "error": "Purchase not found"}), 404

        if purchase.status != 'pending':
            return jsonify({
                "success": False,
                "error": f"Can only approve pending purchases, current status: {purchase.status}"
            }), 400

        # Update inventory for each purchased material
        for item in purchase.items:
            if item.material:
                item.material.quantity += item.quantity
                db.session.add(item.material)

        # Create accounting transaction
        success, result = create_cash_transaction(purchase)
        if not success:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": f"Failed to create accounting entry: {result}"
            }), 500

        # Update purchase status
        old_status = purchase.status
        purchase.status = 'approved'
        purchase.approved_at = datetime.utcnow()

        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Purchase',
            entity_id=purchase.id,
            action='APPROVE',
            old_values={'status': old_status},
            new_values={'status': 'approved'},
            entity_name=purchase.po_number if purchase.po_number else f"Purchase #{purchase.id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({
            "success": True,
            "message": f"Purchase approved. Inventory updated (+{len(purchase.items)} items), accounting entry created.",
            "data": purchase.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# DELETE PURCHASE
# ============================================
@purchase_bp.route('/<int:purchase_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_purchase(purchase_id):
    """Delete purchase (only if pending)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        purchase = Purchase.query.filter_by(id=purchase_id).first()

        if not purchase:
            return jsonify({"success": False, "error": "Purchase not found"}), 404

        if purchase.status != 'pending':
            return jsonify({
                "success": False,
                "error": f"Can only delete pending purchases, current status: {purchase.status}"
            }), 400

        # Capture data BEFORE delete
        deleted_data = purchase.to_dict(include_items=True)
        purchase_name = purchase.po_number if purchase.po_number else f"Purchase #{purchase.id}"

        db.session.delete(purchase)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Purchase',
            entity_id=purchase_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=purchase_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({
            "success": True,
            "message": "Purchase deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
