from extensions import db
from datetime import datetime
import json


class ApprovalRequest(db.Model):
    """
    Multi-level approval workflow tracking.
    Supports complex approval chains with threshold-based rules.
    """
    __tablename__ = 'approval_requests'

    id = db.Column(db.Integer, primary_key=True)

    # Entity reference
    entity_type = db.Column(db.String(50), nullable=False)  # Purchase, Invoice, Budget, etc.
    entity_id = db.Column(db.Integer, nullable=False)

    # Approval status
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, rejected, cancelled

    # Approval chain info
    approval_level = db.Column(db.Integer, default=1, nullable=False)  # Current level in chain
    total_levels = db.Column(db.Integer, default=1, nullable=False)  # Total levels needed

    # Approver tracking
    current_approver_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    required_approvers = db.Column(db.Text, nullable=True)  # JSON list of {level, user_id, required}

    # Approval details
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)

    # User references (keep history - RESTRICT on created_by, SET NULL on others)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='RESTRICT'), nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    rejected_by_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)

    # Company reference
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)

    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='approval_requests_created')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approval_requests_approved')
    rejected_by = db.relationship('User', foreign_keys=[rejected_by_id], backref='approval_requests_rejected')
    current_approver = db.relationship('User', foreign_keys=[current_approver_id], backref='pending_approvals')

    def get_required_approvers(self):
        """Parse JSON required approvers"""
        if self.required_approvers:
            return json.loads(self.required_approvers)
        return []

    def set_required_approvers(self, approvers):
        """Set required approvers as JSON"""
        self.required_approvers = json.dumps(approvers, default=str)

    def can_be_approved_by(self, user_id):
        """Check if user can approve at current level"""
        approvers = self.get_required_approvers()
        current_level_approvers = [a for a in approvers if a.get('level') == self.approval_level]
        return any(a.get('user_id') == user_id for a in current_level_approvers)

    def advance_approval(self):
        """Move to next approval level"""
        self.approval_level += 1
        if self.approval_level > self.total_levels:
            self.approval_level = self.total_levels
            self.status = 'approved'
            self.approved_at = datetime.utcnow()
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'status': self.status,
            'approval_level': self.approval_level,
            'total_levels': self.total_levels,
            'current_approver_id': self.current_approver_id,
            'approval_notes': self.approval_notes,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'created_by_id': self.created_by_id,
            'approved_by_id': self.approved_by_id,
            'rejected_by_id': self.rejected_by_id,
            'company_id': self.company_id,
            'required_approvers': self.get_required_approvers()
        }
