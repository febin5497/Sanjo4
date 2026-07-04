from extensions import db
from datetime import datetime

class VehicleProjectAssignment(db.Model):
    """Track active vehicle assignments to projects (soft-delete pattern: removed_on is NULL for active)"""
    __tablename__ = 'vehicle_project_assignment'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    assigned_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    removed_on = db.Column(db.DateTime, nullable=True)  # NULL = currently active, timestamp = removed

    notes = db.Column(db.String(500), nullable=True)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    project = db.relationship('Project', foreign_keys=[project_id])

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'vehicle_id': self.vehicle_id,
            'company_id': self.company_id,
            'assigned_on': self.assigned_on.strftime('%Y-%m-%d %H:%M:%S') if self.assigned_on else None,
            'removed_on': self.removed_on.strftime('%Y-%m-%d %H:%M:%S') if self.removed_on else None,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by,
            'is_active': self.removed_on is None
        }

    def __repr__(self):
        return f'<VehicleProjectAssignment {self.id}>'


class VehicleProjectHistory(db.Model):
    """Immutable audit trail of all vehicle-project assignments"""
    __tablename__ = 'vehicle_project_history'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    assigned_date = db.Column(db.DateTime, nullable=False)
    unassigned_date = db.Column(db.DateTime, nullable=True)

    notes = db.Column(db.String(500), nullable=True)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    project = db.relationship('Project', foreign_keys=[project_id])

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'vehicle_id': self.vehicle_id,
            'company_id': self.company_id,
            'assigned_date': self.assigned_date.strftime('%Y-%m-%d %H:%M:%S') if self.assigned_date else None,
            'unassigned_date': self.unassigned_date.strftime('%Y-%m-%d %H:%M:%S') if self.unassigned_date else None,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_by': self.created_by,
            'duration_days': (self.unassigned_date - self.assigned_date).days if self.unassigned_date else (datetime.utcnow() - self.assigned_date).days
        }

    def __repr__(self):
        return f'<VehicleProjectHistory {self.id}>'
