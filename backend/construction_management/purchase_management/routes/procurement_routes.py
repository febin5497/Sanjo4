from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
from purchase_management.models.purchase_indent import PurchaseIndent, PurchaseIndentItem
from purchase_management.models.grn import GoodsReceiptNote, GRNItem, InvoiceReconciliation
from purchase_management.models import Purchase, PurchaseItem
from finance_management.models.invoice import Invoice
from user_management.models import User
from project_management.models.models import Project
from material_management.models import Material
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, paginated_response
from constants.statuses import PurchaseIndentStatus, GRNStatus
import random
import string

procurement_bp = Blueprint('procurement', __name__)


def generate_unique_number(prefix):
    """Generate unique number like IND-2026-001"""
    random_suffix = ''.join(random.choices(string.digits, k=3))
    timestamp = datetime.utcnow().strftime('%Y')
    return f"{prefix}-{timestamp}-{random_suffix}"


# ================== PURCHASE INDENT ROUTES ==================

@procurement_bp.route('/indents', methods=['GET'])
@jwt_required()
def get_indents():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)
        project_id = request.args.get('project_id', None, type=int)

        query = PurchaseIndent.query.filter_by(company_id=user.company_id) if user else PurchaseIndent.query

        if status:
            query = query.filter_by(status=status)
        if project_id:
            query = query.filter_by(project_id=project_id)

        total = query.count()
        indents = query.order_by(PurchaseIndent.created_at.desc()).paginate(page=page, per_page=per_page).items

        data = [indent.to_dict(include_items=True) for indent in indents]
        return paginated_response(data, page, per_page, total, "Indents retrieved", status_code=200)
    except Exception as e:
        return error_response(f"Error fetching indents: {str(e)}", status_code=500)


@procurement_bp.route('/indents', methods=['POST'])
@jwt_required()
def create_indent():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        errors = []
        if not data.get('description'):
            errors.append({"field": "description", "message": "Description is required"})
        if not data.get('required_by_date'):
            errors.append({"field": "required_by_date", "message": "Required by date is required"})
        if not data.get('items') or len(data.get('items', [])) == 0:
            errors.append({"field": "items", "message": "At least one item is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        indent = PurchaseIndent(
            indent_number=generate_unique_number('IND'),
            project_id=data.get('project_id'),
            company_id=user.company_id if user else None,
            description=data.get('description'),
            justification=data.get('justification'),
            indent_date=datetime.utcnow().date(),
            required_by_date=datetime.strptime(data['required_by_date'], '%Y-%m-%d').date(),
            created_by_id=user_id,
            status=PurchaseIndentStatus.DRAFT.value
        )

        for item_data in data.get('items', []):
            item = PurchaseIndentItem(
                description=item_data.get('description'),
                quantity=item_data.get('quantity'),
                unit=item_data.get('unit', 'qty'),
                estimated_rate=item_data.get('estimated_rate'),
                estimated_cost=item_data.get('estimated_cost'),
                material_id=item_data.get('material_id'),
                notes=item_data.get('notes')
            )
            indent.items.append(item)

        db.session.add(indent)
        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='PurchaseIndent', entity_id=indent.id, action='CREATE',
            new_values={'indent_number': indent.indent_number, 'status': indent.status},
            entity_name=indent.indent_number,
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(indent.to_dict(include_items=True), "Indent created", status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating indent: {str(e)}", status_code=500)


@procurement_bp.route('/indents/<int:indent_id>/submit', methods=['POST'])
@jwt_required()
def submit_indent(indent_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        indent = PurchaseIndent.query.get(indent_id)
        if not indent:
            return error_response("Indent not found", status_code=404)

        if indent.status != PurchaseIndentStatus.DRAFT.value:
            return error_response("Only draft indents can be submitted", status_code=400)

        indent.status = PurchaseIndentStatus.SUBMITTED.value
        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='PurchaseIndent', entity_id=indent.id, action='UPDATE',
            new_values={'status': PurchaseIndentStatus.SUBMITTED.value},
            entity_name=indent.indent_number,
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(indent.to_dict(include_items=True), "Indent submitted", status_code=200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error submitting indent: {str(e)}", status_code=500)


@procurement_bp.route('/indents/<int:indent_id>/approve', methods=['POST'])
@jwt_required()
def approve_indent(indent_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        indent = PurchaseIndent.query.get(indent_id)
        if not indent:
            return error_response("Indent not found", status_code=404)

        if indent.status != PurchaseIndentStatus.SUBMITTED.value:
            return error_response("Only submitted indents can be approved", status_code=400)

        indent.status = PurchaseIndentStatus.APPROVED.value
        indent.approved_by_id = user_id
        indent.approved_at = datetime.utcnow()
        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='PurchaseIndent', entity_id=indent.id, action='APPROVE',
            new_values={'status': 'approved'},
            entity_name=indent.indent_number,
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(indent.to_dict(include_items=True), "Indent approved", status_code=200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error approving indent: {str(e)}", status_code=500)


# ================== GRN ROUTES ==================

@procurement_bp.route('/grns', methods=['GET'])
@jwt_required()
def get_grns():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None, type=str)

        query = GoodsReceiptNote.query.filter_by(company_id=user.company_id) if user else GoodsReceiptNote.query

        if status:
            query = query.filter_by(status=status)

        total = query.count()
        grns = query.order_by(GoodsReceiptNote.created_at.desc()).paginate(page=page, per_page=per_page).items

        data = [grn.to_dict(include_items=True) for grn in grns]
        return paginated_response(data, page, per_page, total, "GRNs retrieved", status_code=200)
    except Exception as e:
        return error_response(f"Error fetching GRNs: {str(e)}", status_code=500)


@procurement_bp.route('/grns', methods=['POST'])
@jwt_required()
def create_grn():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        errors = []
        if not data.get('purchase_order_id'):
            errors.append({"field": "purchase_order_id", "message": "Purchase Order ID is required"})
        if not data.get('receipt_date'):
            errors.append({"field": "receipt_date", "message": "Receipt date is required"})
        if not data.get('items') or len(data.get('items', [])) == 0:
            errors.append({"field": "items", "message": "At least one item is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        po = Purchase.query.get(data.get('purchase_order_id'))
        if not po:
            return error_response("Purchase Order not found", status_code=404)

        grn = GoodsReceiptNote(
            grn_number=generate_unique_number('GRN'),
            purchase_order_id=data.get('purchase_order_id'),
            company_id=user.company_id if user else None,
            receipt_date=datetime.strptime(data['receipt_date'], '%Y-%m-%d').date(),
            vehicle_number=data.get('vehicle_number'),
            driver_name=data.get('driver_name'),
            supplier_reference=data.get('supplier_reference'),
            created_by_id=user_id
        )

        for item_data in data.get('items', []):
            item = GRNItem(
                description=item_data.get('description'),
                quantity_ordered=item_data.get('quantity_ordered'),
                quantity_received=item_data.get('quantity_received'),
                unit=item_data.get('unit'),
                quality_remarks=item_data.get('quality_remarks'),
                is_damaged=item_data.get('is_damaged', False),
                damaged_quantity=item_data.get('damaged_quantity', 0),
                po_item_id=item_data.get('po_item_id')
            )
            grn.items.append(item)

        db.session.add(grn)
        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='GoodsReceiptNote', entity_id=grn.id, action='CREATE',
            new_values={'grn_number': grn.grn_number, 'po_id': grn.purchase_order_id},
            entity_name=grn.grn_number,
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(grn.to_dict(include_items=True), "GRN created", status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error creating GRN: {str(e)}", status_code=500)


@procurement_bp.route('/grns/<int:grn_id>/quality-check', methods=['POST'])
@jwt_required()
def quality_check_grn(grn_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        grn = GoodsReceiptNote.query.get(grn_id)
        if not grn:
            return error_response("GRN not found", status_code=404)

        grn.quality_check_status = data.get('status', 'pass')  # pass, fail, partial
        grn.quality_check_notes = data.get('notes')
        grn.quality_checked_by_id = user_id
        grn.quality_check_date = datetime.utcnow()
        grn.status = 'inspected'

        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='GoodsReceiptNote', entity_id=grn.id, action='UPDATE',
            new_values={'quality_status': grn.quality_check_status},
            entity_name=grn.grn_number,
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(grn.to_dict(include_items=True), "Quality check completed", status_code=200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error in quality check: {str(e)}", status_code=500)


@procurement_bp.route('/grns/<int:grn_id>/accept', methods=['POST'])
@jwt_required()
def accept_grn(grn_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        grn = GoodsReceiptNote.query.get(grn_id)
        if not grn:
            return error_response("GRN not found", status_code=404)

        if grn.quality_check_status == 'fail':
            return error_response("Cannot accept GRN with failed quality check", status_code=400)

        grn.status = 'accepted'
        grn.accepted_by_id = user_id
        grn.accepted_at = datetime.utcnow()

        # Update material quantities if materials exist
        po = grn.purchase_order
        if po:
            for grn_item in grn.items:
                # Find corresponding material and update quantity
                if grn_item.po_item_id:
                    po_item = PurchaseItem.query.get(grn_item.po_item_id)
                    if po_item and po_item.material_id:
                        material = Material.query.get(po_item.material_id)
                        if material:
                            material.quantity += grn_item.quantity_received

        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='GoodsReceiptNote', entity_id=grn.id, action='UPDATE',
            new_values={'status': 'accepted'},
            entity_name=grn.grn_number,
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(grn.to_dict(include_items=True), "GRN accepted", status_code=200)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error accepting GRN: {str(e)}", status_code=500)


# ================== INVOICE RECONCILIATION ==================

@procurement_bp.route('/reconcile-invoice', methods=['POST'])
@jwt_required()
def reconcile_invoice():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        grn = GoodsReceiptNote.query.get(data.get('grn_id'))
        invoice = Invoice.query.get(data.get('invoice_id'))

        if not grn or not invoice:
            return error_response("GRN or Invoice not found", status_code=404)

        # Calculate variances
        grn_total_qty = sum(item.quantity_received for item in grn.items)
        invoice_total = invoice.total

        reconciliation = InvoiceReconciliation(
            grn_id=data.get('grn_id'),
            invoice_id=data.get('invoice_id'),
            status='matched',
            discrepancy_type='none'
        )

        # Check for discrepancies (simplified)
        if abs(invoice_total - invoice.subtotal) > 0.01:
            reconciliation.discrepancy_type = 'rate_mismatch'
            reconciliation.status = 'discrepancy'
            reconciliation.amount_variance = invoice_total - invoice.subtotal

        db.session.add(reconciliation)
        db.session.commit()

        log_entity_action(
            user_id=user_id, company_id=user.company_id if user else None,
            entity_type='InvoiceReconciliation', entity_id=reconciliation.id, action='CREATE',
            new_values={'status': reconciliation.status},
            entity_name=f"GRN-{grn.grn_number}-INV-{invoice.invoice_id}",
            ip_address=request.remote_addr, user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(reconciliation.to_dict(), "Invoice reconciled", status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error reconciling invoice: {str(e)}", status_code=500)


# ================== PROCUREMENT PIPELINE SUMMARY ==================

@procurement_bp.route('/pipeline', methods=['GET'])
@jwt_required()
def get_procurement_pipeline():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        project_id = request.args.get('project_id', None, type=int)

        query_filter = {'company_id': user.company_id} if user else {}
        if project_id:
            query_filter['project_id'] = project_id

        indents = PurchaseIndent.query.filter_by(**query_filter).count()
        approved_indents = PurchaseIndent.query.filter_by(status=PurchaseIndentStatus.APPROVED.value, **query_filter).count()
        grns = GoodsReceiptNote.query.filter_by(**query_filter).count()
        pending_grns = GoodsReceiptNote.query.filter_by(status='received', **query_filter).count()

        pipeline = {
            'indents': {
                'total': indents,
                'approved': approved_indents,
                'pending_approval': indents - approved_indents
            },
            'grns': {
                'total': grns,
                'pending_inspection': pending_grns
            },
            'status': 'healthy' if pending_grns < indents else 'warning'
        }

        return success_response(pipeline, "Pipeline status retrieved", status_code=200)
    except Exception as e:
        return error_response(f"Error fetching pipeline: {str(e)}", status_code=500)


# ================== ENHANCED PROCUREMENT ROUTES ==================

@procurement_bp.route('/indents/<int:indent_id>/convert-to-po', methods=['POST'])
@jwt_required()
def convert_indent_to_po(indent_id):
    """Auto-convert approved indent to purchase order"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        indent = PurchaseIndent.query.get(indent_id)
        if not indent:
            return error_response("Indent not found", status_code=404)

        if indent.status != PurchaseIndentStatus.APPROVED.value:
            return error_response(f"Indent must be approved before converting to PO. Current status: {indent.status}", status_code=400)

        # Create new purchase order from indent
        po = Purchase(
            project_id=indent.project_id,
            supplier_id=indent.supplier_id,
            purchase_indent_id=indent_id,
            status='draft',
            total_amount=indent.get_total_amount() if hasattr(indent, 'get_total_amount') else 0,
            created_by_id=user_id,
            company_id=user.company_id if user else None
        )

        db.session.add(po)
        db.session.flush()  # Get PO ID without committing

        # Copy items from indent to PO
        for indent_item in indent.items:
            po_item = PurchaseItem(
                purchase_id=po.id,
                material_id=indent_item.material_id,
                quantity=indent_item.quantity,
                unit_price=indent_item.unit_price if hasattr(indent_item, 'unit_price') else 0,
                description=indent_item.description if hasattr(indent_item, 'description') else None
            )
            db.session.add(po_item)

        db.session.commit()

        log_entity_action(user_id, 'Purchase', po.id, 'CREATE', f"Created PO from indent: {indent_id}")
        log_entity_action(user_id, 'PurchaseIndent', indent_id, 'UPDATE', f"Converted indent to PO: {po.id}")

        return success_response(
            {
                'po_id': po.id,
                'indent_id': indent_id,
                'message': f'Successfully converted indent to PO'
            },
            "Indent converted to PO",
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error converting indent to PO: {str(e)}", status_code=500)


@procurement_bp.route('/grns/<int:grn_id>/quality-check/complete', methods=['POST'])
@jwt_required()
def complete_quality_check(grn_id):
    """Complete quality check workflow and update status"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        grn = GoodsReceiptNote.query.get(grn_id)
        if not grn:
            return error_response("GRN not found", status_code=404)

        quality_status = data.get('quality_status')  # 'pass', 'fail', 'partial'
        quality_notes = data.get('quality_notes', '')

        if quality_status not in ['pass', 'fail', 'partial']:
            return error_response("Invalid quality_status. Must be: pass, fail, or partial", status_code=400)

        grn.quality_status = quality_status
        grn.quality_notes = quality_notes
        grn.quality_checked_by_id = user_id
        grn.quality_checked_at = datetime.utcnow()

        if quality_status == 'pass':
            grn.status = GRNStatus.ACCEPTED.value if hasattr(GRNStatus, 'ACCEPTED') else 'accepted'

            # Update material inventory if GRN is accepted
            for grn_item in grn.items:
                material = Material.query.get(grn_item.material_id)
                if material:
                    # Add received quantity to inventory
                    if hasattr(material, 'quantity_on_hand'):
                        material.quantity_on_hand = (material.quantity_on_hand or 0) + grn_item.quantity_received
                    db.session.add(material)

        elif quality_status == 'fail':
            grn.status = GRNStatus.REJECTED.value if hasattr(GRNStatus, 'REJECTED') else 'rejected'

        elif quality_status == 'partial':
            grn.status = GRNStatus.PARTIAL.value if hasattr(GRNStatus, 'PARTIAL') else 'partial'

        db.session.commit()

        log_entity_action(user_id, 'GoodsReceiptNote', grn_id, 'UPDATE', f"Completed quality check: {quality_status}")

        return success_response(
            grn.to_dict() if hasattr(grn, 'to_dict') else {'id': grn.id, 'status': grn.status},
            f"Quality check completed: {quality_status}",
            status_code=200
        )
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error completing quality check: {str(e)}", status_code=500)


@procurement_bp.route('/procurement/pipeline/metrics', methods=['GET'])
@jwt_required()
def get_procurement_metrics():
    """Get enhanced procurement pipeline metrics"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        project_id = request.args.get('project_id', None, type=int)

        query_filter = {'company_id': user.company_id} if user else {}
        if project_id:
            query_filter['project_id'] = project_id

        # Indent metrics
        total_indents = PurchaseIndent.query.filter_by(**query_filter).count()
        approved_indents = PurchaseIndent.query.filter_by(status=PurchaseIndentStatus.APPROVED.value, **query_filter).count()
        pending_indents = total_indents - approved_indents
        indent_approval_rate = (approved_indents / total_indents * 100) if total_indents > 0 else 0

        # GRN metrics
        total_grns = GoodsReceiptNote.query.filter_by(**query_filter).count()
        accepted_grns = GoodsReceiptNote.query.filter_by(status='accepted', **query_filter).count()
        pending_grns = GoodsReceiptNote.query.filter_by(status='received', **query_filter).count()
        grn_acceptance_rate = (accepted_grns / total_grns * 100) if total_grns > 0 else 0

        # Invoice reconciliation metrics
        total_reconciliations = InvoiceReconciliation.query.filter_by(**query_filter).count()
        matched_reconciliations = InvoiceReconciliation.query.filter_by(status='matched', **query_filter).count()
        discrepancy_reconciliations = InvoiceReconciliation.query.filter_by(status='discrepancy', **query_filter).count()
        reconciliation_rate = (matched_reconciliations / total_reconciliations * 100) if total_reconciliations > 0 else 0

        # Calculate efficiency score
        efficiency_score = (indent_approval_rate + grn_acceptance_rate + reconciliation_rate) / 3

        metrics = {
            'indents': {
                'total': total_indents,
                'approved': approved_indents,
                'pending': pending_indents,
                'approval_rate_percent': round(indent_approval_rate, 2)
            },
            'grns': {
                'total': total_grns,
                'accepted': accepted_grns,
                'pending_inspection': pending_grns,
                'acceptance_rate_percent': round(grn_acceptance_rate, 2)
            },
            'invoice_reconciliation': {
                'total': total_reconciliations,
                'matched': matched_reconciliations,
                'discrepancies': discrepancy_reconciliations,
                'matching_rate_percent': round(reconciliation_rate, 2)
            },
            'overall_efficiency_score': round(efficiency_score, 2),
            'pipeline_health': 'healthy' if efficiency_score > 80 else 'warning' if efficiency_score > 50 else 'critical'
        }

        return success_response(metrics, "Procurement metrics retrieved", status_code=200)
    except Exception as e:
        return error_response(f"Error fetching metrics: {str(e)}", status_code=500)
