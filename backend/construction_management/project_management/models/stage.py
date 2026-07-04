from extensions import db
from datetime import datetime


class ProjectStage(db.Model):
    """Project stage/milestone for stage-based billing"""
    __tablename__ = 'project_stages'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)  # Foundation, Structure, Finishing, etc.
    description = db.Column(db.Text)
    percentage_complete = db.Column(db.Float, default=0)  # 0-100
    billing_percentage = db.Column(db.Float, default=0)  # % of project value to bill for this stage
    planned_start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_start_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    planned_invoice_date = db.Column(db.Date)
    actual_invoice_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    # Relationship to project
    project = db.relationship('Project', backref='stages')

    def to_dict(self):
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
            'status': self.status
        }
