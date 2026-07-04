"""
Unified Approval Framework

Consolidates all approval workflow logic from:
- Finance approvals (ApprovalRequest)
- Budget approvals (BudgetApprovalRequest)
- Attendance photo approvals (ApprovalService)

Into a single, reusable approval system.
"""

from datetime import datetime
from extensions import db
from constants import ApprovalStatus


class ApprovalRequest(db.Model):
    """
    Unified multi-level approval request for any entity.

    Replaces separate approval implementations across Finance, Budget, and Attendance modules.
    Supports:
    - Multi-level approvals (sequential or parallel)
    - Conditional approvals based on amount/type
    - Role-based approval requirements
    - Audit trail of all approval actions
    """

    __tablename__ = 'approval_requests'

    id = db.Column(db.Integer, primary_key=True)

    # Entity Reference
    entity_type = db.Column(db.String(50), nullable=False)  # 'invoice', 'purchase', 'budget', 'photo'
    entity_id = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    # Approval Status
    status = db.Column(
        db.String(20),
        default=ApprovalStatus.PENDING.value,
        nullable=False
    )

    # Approval Levels
    approval_level = db.Column(db.Integer, default=1, nullable=False)  # Current level (1, 2, 3, ...)
    total_levels = db.Column(db.Integer, nullable=False)  # Total levels required
    approval_type = db.Column(
        db.String(20),
        default='sequential',  # sequential or parallel
        nullable=False
    )

    # Approval Details
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Audit
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Required Approvers (JSON array of user IDs that can approve)
    required_approver_ids = db.Column(db.JSON, nullable=True)  # [1, 2, 3]
    assigned_approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Metadata
    approval_metadata = db.Column(db.JSON, nullable=True)  # Custom data per entity type

    def __repr__(self):
        return f"<ApprovalRequest {self.entity_type}:{self.entity_id} status={self.status}>"

    def to_dict(self):
        """Serialize approval request"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'status': self.status,
            'approval_level': self.approval_level,
            'total_levels': self.total_levels,
            'approved_by_id': self.approved_by_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'approval_notes': self.approval_notes,
            'rejection_reason': self.rejection_reason,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat(),
            'required_approver_ids': self.required_approver_ids,
            'assigned_approver_id': self.assigned_approver_id,
        }

    # Approval Workflow Methods

    def can_be_approved_by(self, user_id):
        """
        Check if user can approve this request.

        Args:
            user_id: User attempting to approve

        Returns:
            bool: True if user can approve
        """
        # Check if user is assigned approver
        if self.assigned_approver_id:
            return self.assigned_approver_id == user_id

        # Check if user is in required approvers list
        if self.required_approver_ids:
            return user_id in self.required_approver_ids

        return False

    def approve(self, user_id, notes=""):
        """
        Mark approval request as approved.

        Args:
            user_id: User approving
            notes: Optional approval notes
        """
        self.status = ApprovalStatus.APPROVED.value
        self.approved_by_id = user_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes
        self.updated_at = datetime.utcnow()

    def reject(self, user_id, reason=""):
        """
        Reject approval request.

        Args:
            user_id: User rejecting
            reason: Reason for rejection
        """
        self.status = ApprovalStatus.REJECTED.value
        self.approved_by_id = user_id
        self.approved_at = datetime.utcnow()
        self.rejection_reason = reason
        self.updated_at = datetime.utcnow()

    def advance_approval(self):
        """
        Advance to next approval level (for sequential approvals).

        Returns:
            bool: True if advanced to next level, False if all levels complete
        """
        if self.approval_level < self.total_levels:
            self.approval_level += 1
            self.assigned_approver_id = None  # Clear assignment for next level
            return True
        return False

    def is_fully_approved(self):
        """
        Check if all approval levels are complete.

        Returns:
            bool: True if fully approved
        """
        return (self.status == ApprovalStatus.APPROVED.value and
                self.approval_level >= self.total_levels)

    def is_pending(self):
        """Check if still pending approval"""
        return self.status == ApprovalStatus.PENDING.value

    def is_rejected(self):
        """Check if was rejected"""
        return self.status == ApprovalStatus.REJECTED.value


class ApprovalHistory(db.Model):
    """
    Complete audit trail of all approval actions.

    Provides complete history of who approved/rejected and when.
    """

    __tablename__ = 'approval_history'

    id = db.Column(db.Integer, primary_key=True)
    approval_request_id = db.Column(
        db.Integer,
        db.ForeignKey('approval_requests.id'),
        nullable=False
    )

    # Action details
    action = db.Column(db.String(20), nullable=False)  # 'approved', 'rejected', 'created', 'reassigned'
    performed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    performed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Details of action
    approval_level = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """Serialize history entry"""
        return {
            'id': self.id,
            'approval_request_id': self.approval_request_id,
            'action': self.action,
            'performed_by_id': self.performed_by_id,
            'performed_at': self.performed_at.isoformat(),
            'approval_level': self.approval_level,
            'notes': self.notes,
        }


class ApprovalConfiguration(db.Model):
    """
    Configuration for approval workflows by entity type.

    Defines rules like:
    - How many levels of approval needed
    - Who can approve (roles)
    - Thresholds (e.g., > $50k needs approval)
    """

    __tablename__ = 'approval_configurations'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # 'invoice', 'purchase', 'budget'

    # Approval Rules
    total_levels = db.Column(db.Integer, default=2, nullable=False)
    approval_type = db.Column(db.String(20), default='sequential')  # sequential or parallel

    # Role-based approvers
    approver_roles = db.Column(db.JSON)  # {'level_1': ['manager'], 'level_2': ['director']}

    # Amount-based thresholds
    amount_threshold = db.Column(db.Float, nullable=True)  # If amount > threshold, approval required
    auto_approve_below = db.Column(db.Float, nullable=True)  # Auto-approve if < this amount

    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Serialize configuration"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'total_levels': self.total_levels,
            'approval_type': self.approval_type,
            'approver_roles': self.approver_roles,
            'amount_threshold': self.amount_threshold,
            'auto_approve_below': self.auto_approve_below,
            'is_active': self.is_active,
        }
