from extensions import db
from datetime import datetime

class DriverVehicleAssignment(db.Model):
    """Track driver assignments to vehicles (soft-delete pattern: unassigned_date is NULL for active)"""
    __tablename__ = 'driver_vehicle_assignment'

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    assigned_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    unassigned_date = db.Column(db.DateTime, nullable=True)  # NULL = currently assigned, timestamp = unassigned

    notes = db.Column(db.String(500), nullable=True)

    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'driver_id': self.driver_id,
            'vehicle_id': self.vehicle_id,
            'company_id': self.company_id,
            'assigned_date': self.assigned_date.strftime('%Y-%m-%d %H:%M:%S') if self.assigned_date else None,
            'unassigned_date': self.unassigned_date.strftime('%Y-%m-%d %H:%M:%S') if self.unassigned_date else None,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by,
            'is_active': self.unassigned_date is None
        }

    def __repr__(self):
        return f'<DriverVehicleAssignment {self.id}>'
