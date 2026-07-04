from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from user_management.models import User
from sales_management.models import Sale
from material_management.models import Material
from sales_returns.models import SaleReturn, SaleReturnItem

sales_return_bp = Blueprint('sales_returns', __name__, url_prefix='/api/sales-returns')


# ============================================
# GET ALL SALES RETURNS
# ============================================
@sales_return_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_sales_returns():
    """Get all sales returns for current company"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)

        query = SaleReturn.query

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(SaleReturn.return_date.desc())
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
# CREATE SALES RETURN
# ============================================
@sales_return_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_sales_return():
    """Create a sales return document"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate required fields
        if not data.get('sale_id'):
            return jsonify({"error": "Sale ID is required"}), 400
        if not data.get('reason'):
            return jsonify({"error": "Return reason is required"}), 400
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({"error": "At least one return item required"}), 400

        # Verify sale exists and is approved
        sale = Sale.query.filter_by(
            id=data['sale_id'],
            status='approved'
        ).first()

        if not sale:
            return jsonify({"error": "Sale not found or not approved"}), 404

        # Create return
        sales_return = SaleReturn(
            sale_id=sale.id,
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

            return_item = SaleReturnItem(
                material_id=item_data['material_id'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total
            )
            sales_return.items.append(return_item)
            total += item_total

        sales_return.total_amount = total

        db.session.add(sales_return)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Sales return created successfully",
            "data": sales_return.to_dict(include_items=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# APPROVE SALES RETURN (REVERSE INVENTORY)
# ============================================
@sales_return_bp.route('/<int:return_id>/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def approve_sales_return(return_id):
    """Approve return - increases inventory and creates negative income entry"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        sales_return = SaleReturn.query.filter_by(
            id=return_id
        ).first()

        if not sales_return:
            return jsonify({"error": "Return not found"}), 404

        if sales_return.status != 'pending':
            return jsonify({"error": "Can only approve pending returns"}), 400

        # Increase inventory (reverse the sale)
        for item in sales_return.items:
            material = Material.query.get(item.material_id)
            if material:
                material.quantity += item.quantity
                db.session.add(material)

        # Create reverse accounting transaction
        try:
            from finance_management.models.cash_transaction import CashTransaction
            # Negative transaction (reversal of sales income)
            transaction = CashTransaction(
                project_id=sales_return.sale.project_id,
                date=datetime.utcnow(),
                type='income',
                category='Sales Return',
                amount=-sales_return.total_amount,  # Negative = reversal/refund
                description=f"Sales return for Invoice: {sales_return.sale.invoice_number}",
                created_by=current_user_id
            )
            db.session.add(transaction)
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create accounting entry: {str(e)}"}), 500

        sales_return.status = 'approved'
        sales_return.approved_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Sales return approved. Inventory restored, accounting entry created.",
            "data": sales_return.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# DELETE SALES RETURN
# ============================================
@sales_return_bp.route('/<int:return_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_sales_return(return_id):
    """Delete pending return"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        sales_return = SaleReturn.query.filter_by(
            id=return_id
        ).first()

        if not sales_return:
            return jsonify({"error": "Return not found"}), 404

        if sales_return.status != 'pending':
            return jsonify({"error": "Can only delete pending returns"}), 400

        db.session.delete(sales_return)
        db.session.commit()

        return jsonify({"success": True, "message": "Return deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
