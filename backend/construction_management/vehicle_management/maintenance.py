from extensions import db
from datetime import datetime

class MaintenanceLog(db.Model):
    """Track maintenance history and costs for vehicles"""
    __tablename__ = 'maintenance_logs'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(100), nullable=False)  # e.g., 'Service', 'Repair', 'Inspection', 'Parts Replacement'
    cost = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    service_center = db.Column(db.String(255), nullable=True)
    mileage_at_service = db.Column(db.Float, nullable=True)  # Mileage when service was performed

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Link to Finance CashTransaction (if auto-created)
    transaction_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'company_id': self.company_id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'type': self.type,
            'cost': self.cost,
            'description': self.description,
            'service_center': self.service_center,
            'mileage_at_service': self.mileage_at_service,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by,
            'transaction_id': self.transaction_id
        }

    def __repr__(self):
        return f'<MaintenanceLog {self.id}>'


class MaintenanceSchedule(db.Model):
    """Track preventive maintenance schedules for vehicles"""
    __tablename__ = 'maintenance_schedules'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    maintenance_type = db.Column(db.String(100), nullable=False)  # e.g., 'Oil Change', 'Tire Rotation', 'Filter Replacement'
    interval_km = db.Column(db.Float, nullable=True)  # Service every X km
    interval_days = db.Column(db.Integer, nullable=True)  # Service every X days

    last_done_km = db.Column(db.Float, nullable=True)  # Last service mileage
    last_done_date = db.Column(db.Date, nullable=True)  # Last service date

    next_due_km = db.Column(db.Float, nullable=True)  # Next service due at this mileage
    next_due_date = db.Column(db.Date, nullable=True)  # Next service due on this date

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'company_id': self.company_id,
            'maintenance_type': self.maintenance_type,
            'interval_km': self.interval_km,
            'interval_days': self.interval_days,
            'last_done_km': self.last_done_km,
            'last_done_date': self.last_done_date.strftime('%Y-%m-%d') if self.last_done_date else None,
            'next_due_km': self.next_due_km,
            'next_due_date': self.next_due_date.strftime('%Y-%m-%d') if self.next_due_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by
        }

    def __repr__(self):
        return f'<MaintenanceSchedule {self.id}>'

    def is_due_by_km(self, current_mileage):
        """Check if maintenance is due based on mileage"""
        if not self.next_due_km:
            return False
        return current_mileage >= self.next_due_km

    def is_due_by_date(self):
        """Check if maintenance is due based on date"""
        if not self.next_due_date:
            return False
        return datetime.utcnow().date() >= self.next_due_date

    def is_due(self, current_mileage):
        """Check if maintenance is due (by km or date)"""
        return self.is_due_by_km(current_mileage) or self.is_due_by_date()
