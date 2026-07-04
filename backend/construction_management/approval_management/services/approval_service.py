"""
Unified Approval Service

Consolidates approval logic from Finance, Budget, and Attendance modules.
Provides a single API for:
- Creating approval requests
- Approving/rejecting requests
- Getting pending approvals
- Audit trail management
"""

from datetime import datetime
from extensions import db
from approval_management.models.approval import (
    ApprovalRequest,
    ApprovalHistory,
    ApprovalConfiguration
)
from constants import ApprovalStatus
from utils.response_formatter import error_response, success_response


class ApprovalService:
    """
    Service for managing approval workflows across all entities.

    Usage:
        approval = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=2
        )

        if approval['success']:
            request_id = approval['data']['id']
            approve_result = ApprovalService.approve(request_id, approver_id=20)
    """

    # ==================== Creation ====================

    @staticmethod
    def create_approval_request(
        entity_type,
        entity_id,
        company_id,
        created_by_id,
        total_levels=None,
        approval_type='sequential',
        required_approver_ids=None,
        metadata=None
    ):
        """
        Create a new approval request.

        Args:
            entity_type: Type of entity (invoice, purchase, budget, photo)
            entity_id: ID of the entity
            company_id: Company context
            created_by_id: User creating request
            total_levels: Number of approval levels (optional, uses config if not provided)
            approval_type: 'sequential' or 'parallel'
            required_approver_ids: List of user IDs who can approve
            metadata: Custom data for this approval

        Returns:
            dict: {'success': bool, 'data': ApprovalRequest, 'message': str}
        """
        try:
            # Get configuration if available
            if not total_levels:
                config = ApprovalConfiguration.query.filter_by(
                    company_id=company_id,
                    entity_type=entity_type,
                    is_active=True
                ).first()

                if config:
                    total_levels = config.total_levels
                    approval_type = config.approval_type
                else:
                    total_levels = 2  # Default

            # Create approval request
            approval = ApprovalRequest(
                entity_type=entity_type,
                entity_id=entity_id,
                company_id=company_id,
                created_by_id=created_by_id,
                total_levels=total_levels,
                approval_type=approval_type,
                required_approver_ids=required_approver_ids,
                approval_metadata=metadata
            )

            db.session.add(approval)
            db.session.commit()

            # Log creation
            ApprovalService._create_history(
                approval.id,
                'created',
                created_by_id,
                approval_level=1,
                notes='Approval request created'
            )

            return success_response(
                approval.to_dict(),
                f"Approval request created for {entity_type} {entity_id}",
                201
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    # ==================== Approval Actions ====================

    @staticmethod
    def approve(approval_id, approver_id, notes=""):
        """
        Approve a request and advance to next level.

        Args:
            approval_id: ID of approval request
            approver_id: User approving
            notes: Optional approval notes

        Returns:
            dict: {'success': bool, 'data': ApprovalRequest, 'message': str}
        """
        try:
            approval = ApprovalRequest.query.get(approval_id)

            if not approval:
                return error_response("Approval request not found", 404)

            if approval.status != ApprovalStatus.PENDING.value:
                return error_response(
                    f"Cannot approve request in {approval.status} status",
                    400
                )

            # Verify approver has permission
            if not approval.can_be_approved_by(approver_id):
                return error_response(
                    "User is not authorized to approve this request",
                    403
                )

            # Record approval
            approval.approve(approver_id, notes)

            # Check if we need to advance to next level or mark complete
            has_next_level = approval.advance_approval()

            if not has_next_level:
                # All levels complete
                approval.status = ApprovalStatus.APPROVED.value

            db.session.commit()

            # Log approval action
            ApprovalService._create_history(
                approval_id,
                'approved',
                approver_id,
                approval_level=approval.approval_level,
                notes=notes
            )

            message = (
                f"Approval level {approval.approval_level} completed. "
                f"Pending level {approval.approval_level + 1}"
                if has_next_level
                else "Request fully approved"
            )

            return success_response(approval.to_dict(), message)

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    @staticmethod
    def reject(approval_id, rejector_id, reason=""):
        """
        Reject an approval request.

        Args:
            approval_id: ID of approval request
            rejector_id: User rejecting
            reason: Reason for rejection

        Returns:
            dict: {'success': bool, 'data': ApprovalRequest, 'message': str}
        """
        try:
            approval = ApprovalRequest.query.get(approval_id)

            if not approval:
                return error_response("Approval request not found", 404)

            if approval.status != ApprovalStatus.PENDING.value:
                return error_response(
                    f"Cannot reject request in {approval.status} status",
                    400
                )

            approval.reject(rejector_id, reason)
            db.session.commit()

            # Log rejection
            ApprovalService._create_history(
                approval_id,
                'rejected',
                rejector_id,
                approval_level=approval.approval_level,
                notes=reason
            )

            return success_response(
                approval.to_dict(),
                f"Approval request rejected: {reason}"
            )

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    # ==================== Queries ====================

    @staticmethod
    def get_pending_approvals(company_id, approver_id=None, entity_type=None, page=1, per_page=10):
        """
        Get pending approval requests.

        Args:
            company_id: Company context
            approver_id: Filter by approver (optional)
            entity_type: Filter by entity type (optional)
            page: Page number
            per_page: Items per page

        Returns:
            dict: Paginated list of pending approvals
        """
        try:
            query = ApprovalRequest.query.filter_by(
                company_id=company_id,
                status=ApprovalStatus.PENDING.value
            )

            if entity_type:
                query = query.filter_by(entity_type=entity_type)

            if approver_id:
                query = query.filter(
                    (ApprovalRequest.assigned_approver_id == approver_id) |
                    (ApprovalRequest.required_approver_ids.contains(f'[{approver_id}'))
                )

            paginated = query.paginate(page=page, per_page=per_page)

            return success_response(
                [a.to_dict() for a in paginated.items],
                "Pending approvals retrieved",
                pagination={
                    'page': page,
                    'per_page': per_page,
                    'total': paginated.total,
                    'pages': paginated.pages
                }
            )

        except Exception as e:
            return error_response(str(e), 500)

    @staticmethod
    def get_approval_history(approval_id):
        """
        Get approval history for a request.

        Args:
            approval_id: ID of approval request

        Returns:
            dict: List of history entries
        """
        try:
            history = ApprovalHistory.query.filter_by(
                approval_request_id=approval_id
            ).order_by(ApprovalHistory.performed_at.desc()).all()

            return success_response(
                [h.to_dict() for h in history],
                "Approval history retrieved"
            )

        except Exception as e:
            return error_response(str(e), 500)

    @staticmethod
    def get_entity_approvals(entity_type, entity_id, company_id):
        """
        Get all approval requests for an entity.

        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            company_id: Company context

        Returns:
            dict: List of approval requests
        """
        try:
            approvals = ApprovalRequest.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id,
                company_id=company_id
            ).order_by(ApprovalRequest.created_at.desc()).all()

            return success_response(
                [a.to_dict() for a in approvals],
                f"Approvals for {entity_type} {entity_id} retrieved"
            )

        except Exception as e:
            return error_response(str(e), 500)

    # ==================== Configuration ====================

    @staticmethod
    def set_approval_config(company_id, entity_type, total_levels, approval_type='sequential',
                           approver_roles=None, amount_threshold=None, auto_approve_below=None):
        """
        Create or update approval configuration for entity type.

        Args:
            company_id: Company context
            entity_type: Type of entity
            total_levels: Number of approval levels
            approval_type: 'sequential' or 'parallel'
            approver_roles: Dict mapping levels to required roles
            amount_threshold: Amount requiring approval
            auto_approve_below: Amount for auto-approval

        Returns:
            dict: Configuration object
        """
        try:
            config = ApprovalConfiguration.query.filter_by(
                company_id=company_id,
                entity_type=entity_type
            ).first()

            if not config:
                config = ApprovalConfiguration(
                    company_id=company_id,
                    entity_type=entity_type
                )
                db.session.add(config)

            config.total_levels = total_levels
            config.approval_type = approval_type
            config.approver_roles = approver_roles
            config.amount_threshold = amount_threshold
            config.auto_approve_below = auto_approve_below

            db.session.commit()

            return success_response(config.to_dict(), "Configuration updated")

        except Exception as e:
            db.session.rollback()
            return error_response(str(e), 500)

    # ==================== Helpers ====================

    @staticmethod
    def _create_history(approval_request_id, action, user_id, approval_level, notes=None):
        """
        Create approval history entry (internal helper).

        Args:
            approval_request_id: ID of approval request
            action: Action type (approved, rejected, created, etc.)
            user_id: User performing action
            approval_level: Current approval level
            notes: Optional notes
        """
        try:
            history = ApprovalHistory(
                approval_request_id=approval_request_id,
                action=action,
                performed_by_id=user_id,
                approval_level=approval_level,
                notes=notes
            )
            db.session.add(history)
            db.session.commit()
        except Exception as e:
            print(f"Error creating approval history: {str(e)}")
