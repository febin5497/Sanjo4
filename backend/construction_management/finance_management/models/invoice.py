from datetime import datetime
from extensions import db
from models.base import AuditMixin, ApprovalFieldsMixin
from constants import InvoiceStatus, RetentionStatus, GST_RATES

# Map enum values to database defaults
DEFAULT_INVOICE_STATUS = InvoiceStatus.DRAFT.value
DEFAULT_RETENTION_STATUS = RetentionStatus.PENDING.value
DEFAULT_GST_RATE = GST_RATES["eighteen"]


class Invoice(db.Model, AuditMixin, ApprovalFieldsMixin):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.String(50), unique=True, nullable=False)
    client = db.Column(db.String(120), nullable=False)
    subtotal = db.Column(db.Float, nullable=False, default=0)
    include_gst = db.Column(db.Boolean, default=True, nullable=False)
    gst_rate = db.Column(db.Float, default=DEFAULT_GST_RATE, nullable=False)
    gst_amount = db.Column(db.Float, default=0, nullable=False)
    discount = db.Column(db.Float, default=0, nullable=False)
    total = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default=DEFAULT_INVOICE_STATUS, nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Stage-based billing fields
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    stage_id = db.Column(db.Integer, db.ForeignKey('project_stages.id'), nullable=True)
    stage_percentage = db.Column(db.Float, default=100)

    # Retention handling fields
    retention_percentage = db.Column(db.Float, default=0)
    retention_amount = db.Column(db.Float, default=0)
    retention_released_date = db.Column(db.Date, nullable=True)
    retention_status = db.Column(db.String(20), default=DEFAULT_RETENTION_STATUS)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'client': self.client,
            'subtotal': self.subtotal,
            'include_gst': self.include_gst,
            'gst_rate': self.gst_rate,
            'gst_amount': self.gst_amount,
            'discount': self.discount,
            'total': self.total,
            'due_date': self.due_date.isoformat(),
            'status': self.status,
            'description': self.description,
            'company_id': self.company_id,
            'project_id': self.project_id,
            'stage_id': self.stage_id,
            'stage_percentage': self.stage_percentage,
            'retention_percentage': self.retention_percentage,
            'retention_amount': self.retention_amount,
            'retention_released_date': self.retention_released_date.isoformat() if self.retention_released_date else None,
            'retention_status': self.retention_status,
            'approved_by_id': self.approved_by_id,
            'approval_notes': self.approval_notes,
            'rejection_reason': self.rejection_reason,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
