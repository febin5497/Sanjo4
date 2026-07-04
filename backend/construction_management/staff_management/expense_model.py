from extensions import db
from datetime import datetime

class Expense(db.Model):
    """Track daily expenses for site engineers and supervisors"""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    # Expense Details
    expense_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Materials, Labor, Equipment, Other
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    receipt_url = db.Column(db.String(200), nullable=True)

    # Approval Workflow
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_date = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # 2-Tier Approval System
    approval_tier = db.Column(db.String(10), default='Tier1')  # Tier1 (≤₹50K) or Tier2 (>₹50K)
    approvals_required = db.Column(db.Integer, default=1)  # 1 for Tier1, 2 for Tier2
    approvals_received = db.Column(db.Integer, default=0)  # Track number of approvals
    first_approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    first_approval_date = db.Column(db.DateTime, nullable=True)
    second_approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    second_approval_date = db.Column(db.DateTime, nullable=True)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = db.relationship('Project', backref='expenses')
    # Note: staff relationship is handled by Staff.expenses backref in Staff model
    approver = db.relationship('User', backref='approved_expenses', foreign_keys=[approved_by])
    first_approver = db.relationship('User', backref='first_approved_expenses', foreign_keys=[first_approver_id])
    second_approver = db.relationship('User', backref='second_approved_expenses', foreign_keys=[second_approver_id])

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'staff_id': self.staff_id,
            'staff_name': f"{self.staff.first_name} {self.staff.last_name}".strip() if self.staff else 'Unknown',
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else 'Unknown',
            'expense_date': self.expense_date.strftime('%Y-%m-%d') if self.expense_date else None,
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'receipt_url': self.receipt_url,
            'status': self.status,
            'approved_by': self.approved_by,
            'approved_date': self.approved_date.strftime('%Y-%m-%d %H:%M:%S') if self.approved_date else None,
            'rejection_reason': self.rejection_reason,
            'approval_tier': self.approval_tier,
            'approvals_required': self.approvals_required,
            'approvals_received': self.approvals_received,
            'first_approver_id': self.first_approver_id,
            'first_approval_date': self.first_approval_date.strftime('%Y-%m-%d %H:%M:%S') if self.first_approval_date else None,
            'second_approver_id': self.second_approver_id,
            'second_approval_date': self.second_approval_date.strftime('%Y-%m-%d %H:%M:%S') if self.second_approval_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }

    def __repr__(self):
        return f'<Expense {self.id} - {self.category}>'
