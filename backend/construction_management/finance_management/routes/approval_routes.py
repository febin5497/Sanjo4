from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from extensions import db
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from finance_management.models.approval_request import ApprovalRequest
from finance_management.models.invoice import Invoice
from finance_management.models.transaction import Transaction
from finance_management.models.cash_transaction import CashTransaction
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, not_found_response, server_error_response, paginated_response
from constants.statuses import ApprovalStatus

logger = logging.getLogger(__name__)

approval_bp = Blueprint('approval', __name__)


# ✅ Get pending approvals for current user
@approval_bp.route('/pending-approvals', methods=['GET'])
@jwt_required()
def get_pending_approvals():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        entity_type = request.args.get('entity_type', None, type=str)

        query = ApprovalRequest.query.filter_by(
            current_approver_id=user_id,
            status=ApprovalStatus.PENDING.value
        )

        if entity_type:
            query = query.filter_by(entity_type=entity_type)

        total = query.count()
        approvals = query.paginate(page=page, per_page=per_page).items

        data = [approval.to_dict() for approval in approvals]

        return paginated_response(
            data,
            total,
            page,
            per_page,
            "Pending approvals retrieved"
        )
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get pending approvals error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve pending approvals")


# ✅ Get all approvals for a specific entity
@approval_bp.route('/approvals/<entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def get_approval_history(entity_type, entity_id):
    try:
        approvals = ApprovalRequest.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id
        ).order_by(ApprovalRequest.created_at.desc()).all()

        data = [approval.to_dict() for approval in approvals]
        return success_response(data, "Approval history retrieved", status_code=200)
    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get approval history error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve approval history")


# ✅ Approve a request
@approval_bp.route('/approve/<entity_type>/<int:entity_id>', methods=['POST'])
@jwt_required()
def approve_request(entity_type, entity_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        # Find approval request
        approval = ApprovalRequest.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            status=ApprovalStatus.PENDING.value
        ).first()

        if not approval:
            return not_found_response("Approval", details="No pending approval found")

        # Check if user can approve at current level
        if not approval.can_be_approved_by(user_id):
            return error_response("You are not authorized to approve this request", status_code=403)

        # Update approval
        approval.approval_notes = data.get('notes', '')
        approval.approved_by_id = user_id
        approval.approved_at = datetime.utcnow()

        # Advance to next level
        is_final = approval.advance_approval()

        # Update the actual entity
        entity = _get_entity(entity_type, entity_id)
        if entity:
            entity.approval_notes = data.get('notes', '')
            entity.approved_by_id = user_id
            entity.approved_at = datetime.utcnow()

            # If final approval, update status
            if is_final and hasattr(entity, 'status'):
                entity.status = ApprovalStatus.APPROVED.value

        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=user_id,
            company_id=user.company_id if user else None,
            entity_type='ApprovalRequest',
            entity_id=approval.id,
            action='APPROVE',
            new_values={
                'approval_level': approval.approval_level,
                'status': approval.status,
                'approved_by_id': user_id
            },
            entity_name=f"{entity_type} #{entity_id}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        response_msg = "Approved successfully" if is_final else f"Approved - Forwarded to level {approval.approval_level}"
        return success_response(approval.to_dict(), response_msg, status_code=200)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Approve request error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to approve request")


# ✅ Reject a request
@approval_bp.route('/reject/<entity_type>/<int:entity_id>', methods=['POST'])
@jwt_required()
def reject_request(entity_type, entity_id):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        # Find approval request
        approval = ApprovalRequest.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            status=ApprovalStatus.PENDING.value
        ).first()

        if not approval:
            return not_found_response("Approval", details="No pending approval found")

        # Check if user can approve at current level
        if not approval.can_be_approved_by(user_id):
            return error_response("You are not authorized to reject this request", status_code=403)

        # Update approval
        approval.status = ApprovalStatus.REJECTED.value
        approval.rejection_reason = data.get('reason', '')
        approval.rejected_by_id = user_id
        approval.rejected_at = datetime.utcnow()

        # Update the actual entity
        entity = _get_entity(entity_type, entity_id)
        if entity:
            entity.rejection_reason = data.get('reason', '')
            if hasattr(entity, 'status'):
                entity.status = ApprovalStatus.REJECTED.value

        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=user_id,
            company_id=user.company_id if user else None,
            entity_type='ApprovalRequest',
            entity_id=approval.id,
            action='REJECT',
            new_values={
                'status': 'rejected',
                'rejection_reason': data.get('reason', ''),
                'rejected_by_id': user_id
            },
            entity_name=f"{entity_type} #{entity_id}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(approval.to_dict(), "Request rejected", status_code=200)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Reject request error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to reject request")


# ✅ Create approval request for entity
@approval_bp.route('/create-approval-request', methods=['POST'])
@jwt_required()
def create_approval_request():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json(silent=True) or {}

        # Validation
        errors = []
        if not data.get('entity_type'):
            errors.append({"field": "entity_type", "message": "Entity type is required"})
        if not data.get('entity_id'):
            errors.append({"field": "entity_id", "message": "Entity ID is required"})
        if not data.get('required_approvers'):
            errors.append({"field": "required_approvers", "message": "Required approvers list is required"})

        if errors:
            return error_response("Validation failed", errors=errors, status_code=400)

        # Get first approver
        approvers = data.get('required_approvers', [])
        first_approver_id = approvers[0].get('user_id') if approvers else None

        # Create approval request
        approval = ApprovalRequest(
            entity_type=data.get('entity_type'),
            entity_id=data.get('entity_id'),
            total_levels=len(approvers),
            current_approver_id=first_approver_id,
            created_by_id=user_id,
            company_id=user.company_id if user else None,
            submitted_at=datetime.utcnow()
        )
        approval.set_required_approvers(approvers)

        db.session.add(approval)
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=user_id,
            company_id=user.company_id if user else None,
            entity_type='ApprovalRequest',
            entity_id=approval.id,
            action='CREATE',
            new_values={
                'entity_type': approval.entity_type,
                'entity_id': approval.entity_id,
                'total_levels': approval.total_levels
            },
            entity_name=f"{approval.entity_type} #{approval.entity_id}",
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )

        return success_response(approval.to_dict(), "Approval request created", status_code=201)

    except ValueError as e:
        db.session.rollback()
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        db.session.rollback()
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create approval request error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to create approval request")


# ✅ Get approval statistics
@approval_bp.route('/approval-stats', methods=['GET'])
@jwt_required()
def get_approval_stats():
    try:
        user_id = get_jwt_identity()

        pending_count = ApprovalRequest.query.filter_by(
            current_approver_id=user_id,
            status=ApprovalStatus.PENDING.value
        ).count()

        approved_count = ApprovalRequest.query.filter_by(
            approved_by_id=user_id,
            status=ApprovalStatus.APPROVED.value
        ).count()

        rejected_count = ApprovalRequest.query.filter_by(
            rejected_by_id=user_id,
            status=ApprovalStatus.REJECTED.value
        ).count()

        stats = {
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count,
            'total': pending_count + approved_count + rejected_count
        }

        return success_response(stats, "Approval statistics", status_code=200)

    except ValueError as e:
        return error_response(f"Invalid input: {str(e)}", status_code=400)
    except IntegrityError as e:
        return error_response("Database constraint violation", status_code=400)
    except Exception as e:
        logger.error(f"Get approval stats error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve approval statistics")


# ✅ Helper function to get entity object
def _get_entity(entity_type, entity_id):
    """Get the actual entity being approved"""
    if entity_type == 'Invoice':
        return Invoice.query.get(entity_id)
    elif entity_type == 'Transaction':
        return Transaction.query.get(entity_id)
    elif entity_type == 'CashTransaction':
        return CashTransaction.query.get(entity_id)
    # Add more entity types as needed
    return None
