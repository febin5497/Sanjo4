from extensions import db
from datetime import datetime


class ProjectStage(db.Model):
    """Project stage with billing percentage for stage-based invoicing"""
    __tablename__ = 'project_stages'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)

    # Stage details
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Progress and billing
    percentage_complete = db.Column(db.Float, default=0, nullable=False)
    billing_percentage = db.Column(db.Float, default=0, nullable=False)

    # Dates
    planned_start_date = db.Column(db.Date, nullable=True)
    planned_end_date = db.Column(db.Date, nullable=True)
    actual_start_date = db.Column(db.Date, nullable=True)
    actual_end_date = db.Column(db.Date, nullable=True)
    planned_invoice_date = db.Column(db.Date, nullable=True)
    actual_invoice_date = db.Column(db.Date, nullable=True)

    # Status
    status = db.Column(db.String(50), default='not_started', nullable=False)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)

    # Relationships
    project = db.relationship('Project', backref='stages')

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'percentage_complete': self.percentage_complete,
            'billing_percentage': self.billing_percentage,
            'planned_start_date': self.planned_start_date.isoformat() if self.planned_start_date else None,
            'planned_end_date': self.planned_end_date.isoformat() if self.planned_end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'planned_invoice_date': self.planned_invoice_date.isoformat() if self.planned_invoice_date else None,
            'actual_invoice_date': self.actual_invoice_date.isoformat() if self.actual_invoice_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'company_id': self.company_id,
        }
