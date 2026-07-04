"""
Specialized Procurement Routers - Using BaseResourceRouter

Auto-generates CRUD endpoints for procurement entities:
- Purchase Indents
- Purchase Orders
- Goods Receipt Notes (GRN)

Consolidates explicit route implementations in:
- procurement_routes.py
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from base.base_resource_router import BaseResourceRouter
from purchase_management.models.purchase_indent import PurchaseIndent
from purchase_management.models.purchase import Purchase
from purchase_management.models.grn import GoodsReceiptNote
from user_management.models import User
from utils.response_formatter import success_response, error_response
from admin_management.utils.activity_logger import log_entity_action


# ==================== Purchase Indent Router ====================

class PurchaseIndentRouter(BaseResourceRouter):
    """Auto-generates Purchase Indent CRUD endpoints"""
    model = PurchaseIndent
    entity_name = "Purchase Indent"
    searchable_fields = ['indent_number', 'description']

    @classmethod
    def schema(cls, obj):
        """Schema for Purchase Indent responses"""
        return {
            'id': obj.id,
            'indent_number': obj.indent_number,
            'project_id': obj.project_id,
            'description': obj.description,
            'justification': obj.justification,
            'status': obj.status,
            'indent_date': obj.indent_date.isoformat(),
            'required_by_date': obj.required_by_date.isoformat(),
            'approved_by_id': obj.approved_by_id,
            'approved_at': obj.approved_at.isoformat() if obj.approved_at else None,
            'rejection_reason': obj.rejection_reason,
            'created_by_id': obj.created_by_id,
            'created_at': obj.created_at.isoformat(),
            'updated_at': obj.updated_at.isoformat()
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Purchase Indent creation"""
        errors = []
        if not data.get('description'):
            errors.append({'field': 'description', 'message': 'Description required'})
        if not data.get('required_by_date'):
            errors.append({'field': 'required_by_date', 'message': 'Required by date required'})
        if not data.get('items') or len(data.get('items', [])) == 0:
            errors.append({'field': 'items', 'message': 'At least one item required'})
        return errors


# ==================== Purchase Order Router ====================

class PurchaseOrderRouter(BaseResourceRouter):
    """Auto-generates Purchase Order CRUD endpoints"""
    model = Purchase
    entity_name = "Purchase Order"
    searchable_fields = ['po_number', 'supplier_id']

    @classmethod
    def schema(cls, obj):
        """Schema for Purchase Order responses"""
        return {
            'id': obj.id,
            'po_number': obj.po_number if hasattr(obj, 'po_number') else f"PO-{obj.id}",
            'supplier_id': obj.supplier_id if hasattr(obj, 'supplier_id') else None,
            'project_id': obj.project_id,
            'amount': float(obj.amount) if hasattr(obj, 'amount') else 0,
            'status': obj.status,
            'created_date': obj.created_date.isoformat() if hasattr(obj, 'created_date') and obj.created_date else None,
            'approved_by_id': obj.approved_by_id if hasattr(obj, 'approved_by_id') else None,
            'approved_at': obj.approved_at.isoformat() if hasattr(obj, 'approved_at') and obj.approved_at else None,
            'created_by_id': obj.created_by_id,
            'created_at': obj.created_at.isoformat()
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Purchase Order creation"""
        errors = []
        if not data.get('supplier_id'):
            errors.append({'field': 'supplier_id', 'message': 'Supplier ID required'})
        if not data.get('project_id'):
            errors.append({'field': 'project_id', 'message': 'Project ID required'})
        if not data.get('items') or len(data.get('items', [])) == 0:
            errors.append({'field': 'items', 'message': 'At least one item required'})
        return errors


# ==================== Goods Receipt Note Router ====================

class GRNRouter(BaseResourceRouter):
    """Auto-generates GRN CRUD endpoints"""
    model = GoodsReceiptNote
    entity_name = "Goods Receipt Note"
    searchable_fields = ['grn_number', 'po_number']

    @classmethod
    def schema(cls, obj):
        """Schema for GRN responses"""
        return {
            'id': obj.id,
            'grn_number': obj.grn_number if hasattr(obj, 'grn_number') else f"GRN-{obj.id}",
            'po_number': obj.po_number if hasattr(obj, 'po_number') else None,
            'purchase_order_id': obj.purchase_order_id if hasattr(obj, 'purchase_order_id') else None,
            'goods_date': obj.goods_date.isoformat() if hasattr(obj, 'goods_date') and obj.goods_date else None,
            'status': obj.status,
            'quality_check_status': obj.quality_check_status if hasattr(obj, 'quality_check_status') else None,
            'created_by_id': obj.created_by_id if hasattr(obj, 'created_by_id') else None,
            'created_at': obj.created_at.isoformat() if hasattr(obj, 'created_at') else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate GRN creation"""
        errors = []
        if not data.get('po_number') and not data.get('purchase_order_id'):
            errors.append({'field': 'po_number', 'message': 'PO number or ID required'})
        if not data.get('goods_date'):
            errors.append({'field': 'goods_date', 'message': 'Goods receipt date required'})
        if not data.get('items') or len(data.get('items', [])) == 0:
            errors.append({'field': 'items', 'message': 'At least one item required'})
        return errors


# ==================== Register Routers ====================

def register_procurement_routers(app):
    """Register all procurement routers with Flask app"""
    # Purchase Indents
    indent_bp = PurchaseIndentRouter.create_blueprint(url_prefix='/api/procurement/indents')
    app.register_blueprint(indent_bp)

    # Purchase Orders
    po_bp = PurchaseOrderRouter.create_blueprint(url_prefix='/api/procurement/purchase-orders')
    app.register_blueprint(po_bp)

    # Goods Receipt Notes
    grn_bp = GRNRouter.create_blueprint(url_prefix='/api/procurement/grn')
    app.register_blueprint(grn_bp)
