"""
Unified Approval Routes

Provides centralized endpoints for all approval operations.
Replaces separate endpoints in:
- finance_management/routes/approval_routes.py
- attendance_management/routes (photo approvals)
- finance_management/routes/budget_routes.py (approval endpoints)
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from user_management.models import User
from approval_management.models.approval import ApprovalRequest
from approval_management.services.approval_service import ApprovalService
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response

approval_bp = Blueprint('approval', __name__)


# ==================== Approval Management ====================

@approval_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_approvals():
    """
    Get all pending approval requests for the current user.

    Query params:
    - entity_type: Filter by entity type (optional)
    - page: Page number (default 1)
    - per_page: Items per page (default 10)
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        entity_type = request.args.get('entity_type', None, type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result = ApprovalService.get_pending_approvals(
            company_id=user.company_id,
            approver_id=current_user_id,
            entity_type=entity_type,
            page=page,
            per_page=per_page
        )

        return result

    except Exception as e:
        return error_response(str(e), 500)


@approval_bp.route('/<int:approval_id>/approve', methods=['POST'])
@jwt_required()
def approve_request(approval_id):
    """
    Approve a pending approval request.

    JSON body:
    - notes: Optional approval notes
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json() or {}

        notes = data.get('notes', '')

        result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=current_user_id,
            notes=notes
        )

        if result[1] == 200 or result[1] == 201:
            approval = result[0].json['data']
            log_entity_action(
                user_id=current_user_id,
                entity_type='ApprovalRequest',
                entity_id=approval_id,
                action='approve',
                description=f"Approved {approval['entity_type']} {approval['entity_id']}"
            )

        return result

    except Exception as e:
        return error_response(str(e), 500)


@approval_bp.route('/<int:approval_id>/reject', methods=['POST'])
@jwt_required()
def reject_request(approval_id):
    """
    Reject a pending approval request.

    JSON body:
    - reason: Reason for rejection
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json() or {}

        reason = data.get('reason', '')

        result = ApprovalService.reject(
            approval_id=approval_id,
            rejector_id=current_user_id,
            reason=reason
        )

        if result[1] == 200 or result[1] == 201:
            approval = result[0].json['data']
            log_entity_action(
                user_id=current_user_id,
                entity_type='ApprovalRequest',
                entity_id=approval_id,
                action='reject',
                description=f"Rejected {approval['entity_type']} {approval['entity_id']}: {reason}"
            )

        return result

    except Exception as e:
        return error_response(str(e), 500)


# ==================== History & Details ====================

@approval_bp.route('/<int:approval_id>', methods=['GET'])
@jwt_required()
def get_approval_details(approval_id):
    """Get details of a specific approval request."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        approval = ApprovalRequest.query.filter_by(
            id=approval_id,
            company_id=user.company_id
        ).first()

        if not approval:
            return error_response("Approval request not found", 404)

        return success_response(approval.to_dict(), "Approval request retrieved")

    except Exception as e:
        return error_response(str(e), 500)


@approval_bp.route('/<int:approval_id>/history', methods=['GET'])
@jwt_required()
def get_approval_history(approval_id):
    """Get approval history for a request."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        # Verify user has access to this approval
        approval = ApprovalRequest.query.filter_by(
            id=approval_id,
            company_id=user.company_id
        ).first()

        if not approval:
            return error_response("Approval request not found", 404)

        return ApprovalService.get_approval_history(approval_id)

    except Exception as e:
        return error_response(str(e), 500)


@approval_bp.route('/entity/<entity_type>/<int:entity_id>', methods=['GET'])
@jwt_required()
def get_entity_approvals(entity_type, entity_id):
    """Get all approval requests for a specific entity."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        return ApprovalService.get_entity_approvals(
            entity_type=entity_type,
            entity_id=entity_id,
            company_id=user.company_id
        )

    except Exception as e:
        return error_response(str(e), 500)


# ==================== Configuration ====================

@approval_bp.route('/config/<entity_type>', methods=['GET'])
@jwt_required()
def get_approval_config(entity_type):
    """Get approval configuration for entity type."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        from approval_management.models.approval import ApprovalConfiguration

        config = ApprovalConfiguration.query.filter_by(
            company_id=user.company_id,
            entity_type=entity_type,
            is_active=True
        ).first()

        if not config:
            return error_response(f"No configuration for {entity_type}", 404)

        return success_response(config.to_dict(), "Configuration retrieved")

    except Exception as e:
        return error_response(str(e), 500)


@approval_bp.route('/config/<entity_type>', methods=['POST'])
@jwt_required()
def set_approval_config(entity_type):
    """
    Create/update approval configuration.

    Requires admin role.

    JSON body:
    - total_levels: Number of approval levels
    - approval_type: 'sequential' or 'parallel'
    - approver_roles: Dict mapping levels to roles
    - amount_threshold: Amount requiring approval
    - auto_approve_below: Amount for auto-approval
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        # Check admin permission
        if user.role != 'admin':
            return error_response("Only admins can configure approvals", 403)

        data = request.get_json() or {}

        return ApprovalService.set_approval_config(
            company_id=user.company_id,
            entity_type=entity_type,
            total_levels=data.get('total_levels', 2),
            approval_type=data.get('approval_type', 'sequential'),
            approver_roles=data.get('approver_roles'),
            amount_threshold=data.get('amount_threshold'),
            auto_approve_below=data.get('auto_approve_below')
        )

    except Exception as e:
        return error_response(str(e), 500)


# ==================== Statistics ====================

@approval_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_approval_stats():
    """Get approval statistics for current user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        from sqlalchemy import func
        from constants import ApprovalStatus

        # Count by status
        pending = ApprovalRequest.query.filter_by(
            company_id=user.company_id,
            status=ApprovalStatus.PENDING.value
        ).count()

        approved = ApprovalRequest.query.filter_by(
            company_id=user.company_id,
            status=ApprovalStatus.APPROVED.value
        ).count()

        rejected = ApprovalRequest.query.filter_by(
            company_id=user.company_id,
            status=ApprovalStatus.REJECTED.value
        ).count()

        # Count by entity type
        by_type = db.session.query(
            ApprovalRequest.entity_type,
            func.count(ApprovalRequest.id)
        ).filter_by(
            company_id=user.company_id,
            status=ApprovalStatus.PENDING.value
        ).group_by(ApprovalRequest.entity_type).all()

        stats = {
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'total': pending + approved + rejected,
            'by_type': [{'type': t, 'count': c} for t, c in by_type]
        }

        return success_response(stats, "Approval statistics retrieved")

    except Exception as e:
        return error_response(str(e), 500)


# ==================== Batch Operations ====================

@approval_bp.route('/batch/create', methods=['POST'])
@jwt_required()
def batch_create_approvals():
    """
    Create multiple approval requests in one call.

    Useful for batch operations like invoice creation.

    JSON body:
    {
        "approvals": [
            {
                "entity_type": "invoice",
                "entity_id": 1,
                "total_levels": 2
            },
            ...
        ]
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json() or {}

        approvals_data = data.get('approvals', [])
        created_approvals = []

        for approval_data in approvals_data:
            result = ApprovalService.create_approval_request(
                entity_type=approval_data.get('entity_type'),
                entity_id=approval_data.get('entity_id'),
                company_id=user.company_id,
                created_by_id=current_user_id,
                total_levels=approval_data.get('total_levels'),
                approval_type=approval_data.get('approval_type', 'sequential'),
                metadata=approval_data.get('metadata')
            )

            if result[1] in (200, 201):
                created_approvals.append(result[0].json['data'])

        return success_response(
            created_approvals,
            f"Created {len(created_approvals)} approval requests"
        )

    except Exception as e:
        return error_response(str(e), 500)
