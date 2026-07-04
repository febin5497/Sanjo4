from extensions import db
from datetime import datetime
from models.base import AuditMixin
from constants.statuses import BudgetStatus, ApprovalStatus
import json


class Budget(db.Model, AuditMixin):
    """Project-level budget tracking with category breakdowns"""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    # Budget details
    total_budget = db.Column(db.Float, nullable=False)  # Total budget amount
    status = db.Column(db.String(20), default=BudgetStatus.ACTIVE.value, nullable=False)  # active, inactive, locked

    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)

    # Description and notes
    description = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Approval
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    categories = db.relationship('BudgetCategory', cascade='all, delete-orphan', backref='budget')

    def get_total_allocated(self):
        """Get total allocated across all categories"""
        return sum(cat.allocated_amount for cat in self.categories)

    def get_total_spent(self):
        """Get total spent across all categories"""
        return sum(cat.used_amount for cat in self.categories)

    def get_variance(self):
        """Get budget variance (allocated - spent)"""
        return self.get_total_allocated() - self.get_total_spent()

    def get_utilization_percent(self):
        """Get budget utilization percentage"""
        allocated = self.get_total_allocated()
        if allocated == 0:
            return 0
        spent = self.get_total_spent()
        return (spent / allocated) * 100

    def to_dict(self, include_categories=False):
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'total_budget': self.total_budget,
            'status': self.status,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'notes': self.notes,
            'approved_by_id': self.approved_by_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_by_id': self.created_by_id,
            'company_id': self.company_id,
            'total_allocated': self.get_total_allocated(),
            'total_spent': self.get_total_spent(),
            'variance': self.get_variance(),
            'utilization_percent': self.get_utilization_percent(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_categories:
            data['categories'] = [cat.to_dict() for cat in self.categories]

        return data


class BudgetCategory(db.Model):
    """Budget breakdown by cost category (material, labor, etc.)"""
    __tablename__ = 'budget_categories'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)

    # Category details
    category = db.Column(db.String(100), nullable=False)  # material, labor, transport, etc.
    allocated_amount = db.Column(db.Float, nullable=False)

    # Tracking (calculated from transactions)
    used_amount = db.Column(db.Float, default=0, nullable=False)

    # Alerts
    warning_threshold = db.Column(db.Float, default=80, nullable=False)  # % of budget before warning

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def get_remaining(self):
        """Get remaining budget for this category"""
        return self.allocated_amount - self.used_amount

    def get_utilization_percent(self):
        """Get utilization percentage"""
        if self.allocated_amount == 0:
            return 0
        return (self.used_amount / self.allocated_amount) * 100

    def is_warning_level(self):
        """Check if category is at warning threshold"""
        return self.get_utilization_percent() >= self.warning_threshold

    def is_exceeded(self):
        """Check if budget exceeded"""
        return self.used_amount > self.allocated_amount

    def to_dict(self):
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'category': self.category,
            'allocated_amount': self.allocated_amount,
            'used_amount': self.used_amount,
            'remaining': self.get_remaining(),
            'utilization_percent': self.get_utilization_percent(),
            'warning_threshold': self.warning_threshold,
            'is_warning_level': self.is_warning_level(),
            'is_exceeded': self.is_exceeded(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class BudgetApprovalRequest(db.Model, AuditMixin):
    """Multi-level approval for budget changes"""
    __tablename__ = 'budget_approval_requests'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)

    # Type of change
    request_type = db.Column(db.String(20), nullable=False)  # create, modify, increase, decrease

    # Proposed changes
    proposed_changes = db.Column(db.Text, nullable=True)  # JSON of changes

    # Approval workflow
    status = db.Column(db.String(20), default=ApprovalStatus.PENDING.value, nullable=False)  # pending, approved, rejected
    approval_level = db.Column(db.Integer, default=1, nullable=False)
    total_levels = db.Column(db.Integer, default=1, nullable=False)

    # Approvers
    current_approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Meta
    requested_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved_at = db.Column(db.DateTime, nullable=True)

    def get_proposed_changes(self):
        """Parse JSON proposed changes"""
        if self.proposed_changes:
            return json.loads(self.proposed_changes)
        return {}

    def set_proposed_changes(self, changes):
        """Set proposed changes as JSON"""
        self.proposed_changes = json.dumps(changes, default=str)

    def to_dict(self):
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'request_type': self.request_type,
            'proposed_changes': self.get_proposed_changes(),
            'status': self.status,
            'approval_level': self.approval_level,
            'total_levels': self.total_levels,
            'current_approver_id': self.current_approver_id,
            'approved_by_id': self.approved_by_id,
            'approval_notes': self.approval_notes,
            'rejection_reason': self.rejection_reason,
            'requested_by_id': self.requested_by_id,
            'company_id': self.company_id,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }
