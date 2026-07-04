from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from user_management.models import User
from purchase_management.models import Purchase
from material_management.models import Material
from purchase_returns.models import PurchaseReturn, PurchaseReturnItem

purchase_return_bp = Blueprint('purchase_returns', __name__, url_prefix='/api/purchase-returns')


# ============================================
# GET ALL PURCHASE RETURNS
# ============================================
@purchase_return_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_purchase_returns():
    """Get all purchase returns for current company"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)

        query = PurchaseReturn.query

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(PurchaseReturn.return_date.desc())
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "success": True,
            "data": [r.to_dict() for r in paginated.items],
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
# CREATE PURCHASE RETURN
# ============================================
@purchase_return_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_purchase_return():
    """Create a purchase return document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        if not data.get('purchase_id'):
            return jsonify({"error": "Purchase ID is required"}), 400
        if not data.get('reason'):
            return jsonify({"error": "Return reason is required"}), 400
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({"error": "At least one return item required"}), 400

        # Verify purchase exists
        purchase = Purchase.query.filter_by(
            id=data['purchase_id'],
            status='approved'
        ).first()

        if not purchase:
            return jsonify({"error": "Purchase not found or not approved"}), 404

        # Create return
        purchase_return = PurchaseReturn(
            purchase_id=purchase.id,
            user_id=current_user_id,
            return_date=datetime.utcnow(),
            reason=data['reason'],
            notes=data.get('notes'),
            status='pending'
        )

        total = 0.0
        for item_data in data['items']:
            quantity = float(item_data['quantity'])
            unit_price = float(item_data['unit_price'])
            item_total = quantity * unit_price

            return_item = PurchaseReturnItem(
                material_id=item_data['material_id'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total
            )
            purchase_return.items.append(return_item)
            total += item_total

        purchase_return.total_amount = total

        db.session.add(purchase_return)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Purchase return created successfully",
            "data": purchase_return.to_dict(include_items=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# APPROVE PURCHASE RETURN (REVERSE INVENTORY)
# ============================================
@purchase_return_bp.route('/<int:return_id>/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def approve_purchase_return(return_id):
    """Approve return - decreases inventory and creates negative accounting entry"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        purchase_return = PurchaseReturn.query.filter_by(
            id=return_id
        ).first()

        if not purchase_return:
            return jsonify({"error": "Return not found"}), 404

        if purchase_return.status != 'pending':
            return jsonify({"error": f"Can only approve pending returns"}), 400

        # Decrease inventory (reverse the purchase)
        for item in purchase_return.items:
            material = Material.query.get(item.material_id)
            if material:
                material.quantity -= item.quantity
                db.session.add(material)

        # Create reverse accounting transaction
        try:
            from finance_management.models.cash_transaction import CashTransaction
            # Negative transaction (reversal of purchase expense)
            transaction = CashTransaction(
                project_id=purchase_return.purchase.project_id,
                date=datetime.utcnow(),
                type='expense',
                category='Purchase Return',
                amount=-purchase_return.total_amount,  # Negative = reversal/credit
                description=f"Purchase return for PO: {purchase_return.purchase.po_number}",
                created_by=current_user_id
            )
            db.session.add(transaction)
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create accounting entry: {str(e)}"}), 500

        purchase_return.status = 'approved'
        purchase_return.approved_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Purchase return approved. Inventory reversed, accounting entry created.",
            "data": purchase_return.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# DELETE PURCHASE RETURN
# ============================================
@purchase_return_bp.route('/<int:return_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_purchase_return(return_id):
    """Delete pending return"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        purchase_return = PurchaseReturn.query.filter_by(
            id=return_id
        ).first()

        if not purchase_return:
            return jsonify({"error": "Return not found"}), 404

        if purchase_return.status != 'pending':
            return jsonify({"error": "Can only delete pending returns"}), 400

        db.session.delete(purchase_return)
        db.session.commit()

        return jsonify({"success": True, "message": "Return deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
