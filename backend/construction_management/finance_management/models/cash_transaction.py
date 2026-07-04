from datetime import datetime
from extensions import db


class CashTransaction(db.Model):
    __tablename__ = 'cash_transactions'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=True)
    staff_id = db.Column(db.Integer, nullable=True)  # Link to staff member
    staff_name = db.Column(db.String(255), nullable=True)  # Denormalized staff name
    project_name = db.Column(db.String(255), nullable=True)  # Denormalized project name
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(100), nullable=False)
    account_code = db.Column(db.String(50), nullable=True)  # FK to chart_of_accounts.account_code
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, nullable=False)

    # Approval fields
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'staff_id': self.staff_id,
            'staff_name': self.staff_name,
            'date': self.date.isoformat(),
            'type': self.type,
            'category': self.category,
            'account_code': self.account_code,
            'amount': self.amount,
            'description': self.description,
            'created_by': self.created_by,
            'approved_by_id': self.approved_by_id,
            'approval_notes': self.approval_notes,
            'rejection_reason': self.rejection_reason,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }
