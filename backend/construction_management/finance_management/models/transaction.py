from extensions import db
from datetime import datetime
from models.base import AuditMixin
from constants.statuses import TransactionStatus

class Transaction(db.Model, AuditMixin):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(db.String(100), nullable=False)  # Added: material, labor, vehicle, etc.
    date = db.Column(db.Date, nullable=False)  # Added: transaction date
    description = db.Column(db.String(255), nullable=True)
    project_id = db.Column(db.Integer, nullable=True)

    # Status and approval fields
    status = db.Column(db.String(20), default=TransactionStatus.PENDING.value, nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type,
            "category": self.category,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "project_id": self.project_id,
            "status": self.status,
            "approved_by_id": self.approved_by_id,
            "approval_notes": self.approval_notes,
            "rejection_reason": self.rejection_reason,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "company_id": self.company_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id,
            "updated_by_id": self.updated_by_id
        }
