import logging
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from extensions import db
from finance_management.models.invoice import Invoice
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, not_found_response, server_error_response

logger = logging.getLogger(__name__)

retention_bp = Blueprint('retention', __name__)


@retention_bp.route('/retentions', methods=['GET'])
@jwt_required()
def get_retentions():
    """Get pending retentions"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        project_id = request.args.get('project_id', type=int)

        query = Invoice.query.filter(
            Invoice.company_id == user.company_id,
            Invoice.retention_status == 'pending',
            Invoice.retention_amount > 0
        )

        if project_id:
            query = query.filter_by(project_id=project_id)

        retentions = query.all()
        data = [inv.to_dict() for inv in retentions]

        return success_response(data, "Retentions retrieved")

    except Exception as e:
        logger.error(f"Error fetching retentions: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve retentions")


@retention_bp.route('/retentions/<int:invoice_id>/release', methods=['POST'])
@jwt_required()
def release_retention(invoice_id):
    """Release retained amount"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        invoice = Invoice.query.filter_by(
            id=invoice_id,
            company_id=user.company_id
        ).first()

        if not invoice:
            return not_found_response("Invoice")

        if invoice.retention_status == 'released':
            return error_response("Retention already released", 400)

        invoice.retention_status = 'released'
        invoice.retention_released_date = datetime.now().date()

        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            entity_type='Retention',
            entity_id=invoice_id,
            action='release',
            description=f'Released retention of ₹{invoice.retention_amount}'
        )

        return success_response(invoice.to_dict(), "Retention released")

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error releasing retention for invoice {invoice_id}: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to release retention")


@retention_bp.route('/reports/retention-schedule', methods=['GET'])
@jwt_required()
def get_retention_schedule():
    """Get retention payment schedule"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        project_id = request.args.get('project_id', type=int)

        query = Invoice.query.filter(
            Invoice.company_id == user.company_id,
            Invoice.retention_amount > 0
        )

        if project_id:
            query = query.filter_by(project_id=project_id)

        invoices = query.all()

        schedule = [
            {
                'invoice_id': inv.invoice_id,
                'amount': inv.total,
                'retention_percentage': inv.retention_percentage,
                'retention_amount': inv.retention_amount,
                'released': inv.retention_status == 'released',
                'release_date': inv.retention_released_date.isoformat() if inv.retention_released_date else None
            }
            for inv in invoices
        ]

        total_retained = sum(inv.retention_amount for inv in invoices if inv.retention_status == 'pending')
        total_released = sum(inv.retention_amount for inv in invoices if inv.retention_status == 'released')

        return success_response({
            'schedule': schedule,
            'total_retained': total_retained,
            'total_released': total_released
        }, "Retention schedule retrieved")

    except Exception as e:
        logger.error(f"Error fetching retention schedule: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve retention schedule")
