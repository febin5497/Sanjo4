from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from finance_management.models.invoice import Invoice
from extensions import db
from datetime import datetime
from user_management.models import User
from utils.response_formatter import (
    success_response, error_response, paginated_response,
    server_error_response, not_found_response
)

# Blueprint initialization
invoice_bp = Blueprint('invoice', __name__, url_prefix='/api/invoices')

def get_current_user():
    """Get current user from JWT token"""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))

# Create an invoice
@invoice_bp.route('/', methods=['POST'])
@jwt_required()
def create_invoice():
    """Create a new invoice"""
    user = get_current_user()
    if not user:
        return not_found_response("User")

    data = request.get_json()

    # Validate required fields
    errors = []
    if not data.get('client'):
        errors.append({"field": "client", "message": "Client name is required"})
    if not data.get('invoice_id'):
        errors.append({"field": "invoice_id", "message": "Invoice ID is required"})
    if not data.get('total'):
        errors.append({"field": "total", "message": "Total amount is required"})
    if not data.get('due_date'):
        errors.append({"field": "due_date", "message": "Due date is required"})

    if errors:
        return error_response("Validation failed", errors=errors, status_code=400)

    # Check if invoice_id already exists
    existing = Invoice.query.filter_by(invoice_id=data.get('invoice_id')).first()
    if existing:
        return error_response(
            "Invoice ID already exists",
            details=f"Invoice with ID {data.get('invoice_id')} already exists",
            status_code=400
        )

    try:
        # Parse due_date
        try:
            due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return error_response("Invalid due_date format. Use YYYY-MM-DD", status_code=400)

        # Create invoice
        invoice = Invoice(
            invoice_id=data.get('invoice_id'),
            client=data.get('client'),
            total=float(data.get('total')),
            due_date=due_date,
            status=data.get('status', 'draft'),
            description=data.get('description'),
            company_id=user.company_id
        )

        db.session.add(invoice)
        db.session.commit()

        return success_response(invoice.to_dict(), "Invoice created successfully", status_code=201)
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))

# Get all invoices
@invoice_bp.route('/', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get all invoices with pagination"""
    user = get_current_user()
    if not user:
        return not_found_response("User")

    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        if page < 1 or per_page < 1:
            return error_response("Page and per_page must be positive integers", status_code=400)

        # Filter by company
        query = Invoice.query.filter_by(company_id=user.company_id).order_by(Invoice.created_at.desc())
        paginated = query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[inv.to_dict() for inv in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Invoices retrieved successfully"
        )
    except Exception as e:
        return server_error_response(details=str(e))

# Get a single invoice
@invoice_bp.route('/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get a specific invoice by ID"""
    user = get_current_user()
    if not user:
        return not_found_response("User")

    try:
        invoice = Invoice.query.filter_by(id=invoice_id, company_id=user.company_id).first()
        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        return success_response(invoice.to_dict(), "Invoice retrieved successfully")
    except Exception as e:
        return server_error_response(details=str(e))

# Update an invoice
@invoice_bp.route('/<int:invoice_id>', methods=['PUT'])
@jwt_required()
def update_invoice(invoice_id):
    """Update an existing invoice"""
    user = get_current_user()
    if not user:
        return not_found_response("User")

    try:
        invoice = Invoice.query.filter_by(id=invoice_id, company_id=user.company_id).first()
        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        data = request.get_json()

        # Update fields
        if 'client' in data:
            invoice.client = data['client']
        if 'invoice_id' in data:
            # Check uniqueness
            existing = Invoice.query.filter(
                Invoice.invoice_id == data['invoice_id'],
                Invoice.id != invoice_id
            ).first()
            if existing:
                return error_response(
                    "Invoice ID already exists",
                    details=f"Invoice with ID {data.get('invoice_id')} already exists",
                    status_code=400
                )
            invoice.invoice_id = data['invoice_id']
        if 'total' in data:
            invoice.total = float(data['total'])
        if 'due_date' in data:
            try:
                invoice.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return error_response("Invalid due_date format. Use YYYY-MM-DD", status_code=400)
        if 'status' in data:
            invoice.status = data['status']
        if 'description' in data:
            invoice.description = data['description']

        db.session.commit()

        return success_response(invoice.to_dict(), "Invoice updated successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))

# Delete an invoice
@invoice_bp.route('/<int:invoice_id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(invoice_id):
    """Delete an invoice"""
    user = get_current_user()
    if not user:
        return not_found_response("User")

    try:
        invoice = Invoice.query.filter_by(id=invoice_id, company_id=user.company_id).first()
        if not invoice:
            return not_found_response("Invoice", details=f"No invoice with ID {invoice_id} found")

        db.session.delete(invoice)
        db.session.commit()

        return success_response(message="Invoice deleted successfully")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))

# Get invoice statistics
@invoice_bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_invoices_summary():
    """Get invoice statistics for current company"""
    user = get_current_user()
    if not user:
        return not_found_response("User")

    try:
        invoices = Invoice.query.filter_by(company_id=user.company_id).all()
        total_invoices = len(invoices)
        total_amount = sum(inv.total for inv in invoices)
        average_amount = total_amount / total_invoices if total_invoices > 0 else 0

        return success_response({
            'total_invoices': total_invoices,
            'total_amount': float(total_amount),
            'average_amount': float(average_amount),
            'by_status': {
                status: len([inv for inv in invoices if inv.status == status])
                for status in ['draft', 'sent', 'pending', 'paid', 'overdue']
            }
        }, "Invoice statistics retrieved")
    except Exception as e:
        return server_error_response(details=str(e))
