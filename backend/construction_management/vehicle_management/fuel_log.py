from extensions import db
from datetime import datetime

class FuelLog(db.Model):
    """Track fuel consumption and costs for vehicles"""
    __tablename__ = 'fuel_logs'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # Optional - fuel may be general
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Liters
    cost = db.Column(db.Float, nullable=False)  # Total fuel cost
    notes = db.Column(db.String(255), nullable=True)

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
            'project_id': self.project_id,
            'company_id': self.company_id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'amount': self.amount,  # Liters
            'cost': self.cost,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_by': self.created_by,
            'transaction_id': self.transaction_id
        }

    def __repr__(self):
        return f'<FuelLog {self.id}>'
