from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from user_management.models import User
from material_management.models import Material
from sales_management.models import Sale, SaleItem
from admin_management.utils.activity_logger import log_entity_action

sales_bp = Blueprint('sales', __name__, url_prefix='/api/sales')


def validate_sale_data(data):
    """Validate sale input data"""
    errors = []

    if not data.get('items') or not isinstance(data['items'], list) or len(data['items']) == 0:
        errors.append("At least one sale item is required")
    else:
        for idx, item in enumerate(data['items']):
            if not item.get('material_id'):
                errors.append(f"Item {idx + 1}: Material ID is required")
            if not item.get('quantity') or float(item['quantity']) <= 0:
                errors.append(f"Item {idx + 1}: Quantity must be greater than 0")
            if not item.get('unit_price') or float(item['unit_price']) <= 0:
                errors.append(f"Item {idx + 1}: Unit price must be greater than 0")

    return errors


# ============================================
# GET ALL SALES
# ============================================
@sales_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_sales():
    """Get all sales for current company"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)
        project_id = request.args.get('project_id', None, type=int)

        query = Sale.query

        if status:
            query = query.filter_by(status=status)
        if project_id:
            query = query.filter_by(project_id=project_id)

        query = query.order_by(Sale.sale_date.desc())
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
# GET SALE BY ID
# ============================================
@sales_bp.route('/<int:sale_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_sale(sale_id):
    """Get sale details"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        sale = Sale.query.filter_by(id=sale_id).first()

        if not sale:
            return jsonify({"error": "Sale not found"}), 404

        return jsonify({
            "success": True,
            "data": sale.to_dict(include_items=True)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# CREATE SALE
# ============================================
@sales_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_sale():
    """Create a new sale"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate input
        errors = validate_sale_data(data)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # Check inventory availability
        items_data = data.get('items', [])
        for item in items_data:
            material = Material.query.get(item['material_id'])
            if not material:
                return jsonify({"error": f"Material {item['material_id']} not found"}), 404

            # Note: We don't prevent sales of out-of-stock items,
            # but tracking purposes may require this later
            # if material.quantity < float(item['quantity']):
            #     return jsonify({"error": f"Insufficient {material.name} (have {material.quantity}, need {item['quantity']})"}), 400

        # Create sale
        sale = Sale(
            project_id=data.get('project_id'),
            customer_id=data.get('customer_id'),
            user_id=current_user_id,
            sale_date=datetime.fromisoformat(data['sale_date']) if data.get('sale_date') else datetime.utcnow(),
            invoice_number=data.get('invoice_number'),
            notes=data.get('notes'),
            status='pending'
        )

        # Add items
        total = 0.0
        for item_data in items_data:
            quantity = float(item_data['quantity'])
            unit_price = float(item_data['unit_price'])
            item_total = quantity * unit_price

            sale_item = SaleItem(
                material_id=item_data['material_id'],
                quantity=quantity,
                unit_price=unit_price,
                total=item_total
            )
            sale.items.append(sale_item)
            total += item_total

        sale.total = total
        sale.tax = float(data.get('tax', 0.0))
        sale.grand_total = total + sale.tax

        db.session.add(sale)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Sale',
            entity_id=sale.id,
            action='CREATE',
            new_values=sale.to_dict(include_items=True),
            entity_name=sale.invoice_number if sale.invoice_number else f"Sale #{sale.id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({
            "success": True,
            "message": "Sale created successfully. Awaiting approval.",
            "data": sale.to_dict(include_items=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# APPROVE SALE (UPDATE INVENTORY + ACCOUNTING)
# ============================================
@sales_bp.route('/<int:sale_id>/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def approve_sale(sale_id):
    """Approve sale - decreases inventory and creates income transaction"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        sale = Sale.query.filter_by(id=sale_id).first()

        if not sale:
            return jsonify({"error": "Sale not found"}), 404

        if sale.status != 'pending':
            return jsonify({"error": f"Can only approve pending sales"}), 400

        # Check inventory
        for item in sale.items:
            material = Material.query.get(item.material_id)
            if material and material.quantity < item.quantity:
                return jsonify({
                    "error": f"Insufficient {material.name} (have {material.quantity}, need {item.quantity})"
                }), 400

        # Decrease inventory
        for item in sale.items:
            material = Material.query.get(item.material_id)
            if material:
                material.quantity -= item.quantity
                db.session.add(material)

        # Create accounting transaction
        try:
            from finance_management.models.cash_transaction import CashTransaction
            transaction = CashTransaction(
                project_id=sale.project_id,
                date=datetime.utcnow(),
                type='income',
                category='Sales',
                amount=sale.grand_total,
                description=f"Sales transaction - Invoice: {sale.invoice_number}",
                created_by=current_user_id
            )
            db.session.add(transaction)
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to create accounting entry: {str(e)}"}), 500

        old_status = sale.status
        sale.status = 'approved'
        sale.approved_at = datetime.utcnow()

        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Sale',
            entity_id=sale.id,
            action='APPROVE',
            old_values={'status': old_status},
            new_values={'status': 'approved'},
            entity_name=sale.invoice_number if sale.invoice_number else f"Sale #{sale.id}",
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({
            "success": True,
            "message": "Sale approved. Inventory decreased, income transaction created.",
            "data": sale.to_dict(include_items=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# DELETE SALE
# ============================================
@sales_bp.route('/<int:sale_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_sale(sale_id):
    """Delete pending sale"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        sale = Sale.query.filter_by(id=sale_id).first()

        if not sale:
            return jsonify({"error": "Sale not found"}), 404

        if sale.status != 'pending':
            return jsonify({"error": "Can only delete pending sales"}), 400

        # Capture data BEFORE delete
        deleted_data = sale.to_dict(include_items=True)
        sale_name = sale.invoice_number if sale.invoice_number else f"Sale #{sale.id}"

        db.session.delete(sale)
        db.session.commit()

        # ✅ LOG ACTIVITY
        user = User.query.get(int(current_user_id))
        ip_address = request.remote_addr or request.headers.get('X-Forwarded-For', '').split(',')[0]
        user_agent = request.headers.get('User-Agent', '')

        log_entity_action(
            user_id=int(current_user_id),
            company_id=user.company_id if user else None,
            entity_type='Sale',
            entity_id=sale_id,
            action='DELETE',
            old_values=deleted_data,
            entity_name=sale_name,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return jsonify({"success": True, "message": "Sale deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
