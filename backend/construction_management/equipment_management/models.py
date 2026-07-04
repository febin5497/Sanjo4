from extensions import db
from datetime import datetime
import json

class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Basic Information
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Machinery, Tools, Vehicles, etc.
    equipment_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

    # Financial Information
    purchase_date = db.Column(db.DateTime)
    purchase_cost = db.Column(db.Float, default=0.0)
    current_value = db.Column(db.Float, default=0.0)
    depreciation_rate = db.Column(db.Float, default=0.1)  # Per year, 10% default

    # Status & Location
    condition = db.Column(db.String(50), default='Good')  # Excellent, Good, Fair, Poor, Under Repair
    location = db.Column(db.String(200))  # Warehouse, Site Name, etc.
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier = db.relationship('Supplier', backref='equipment_items')

    # Additional Info
    specifications = db.Column(db.JSON)  # Store custom specs as JSON
    image_url = db.Column(db.String(500))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Relationships
    maintenance_logs = db.relationship('EquipmentMaintenanceLog', backref='equipment', lazy=True, cascade='all, delete-orphan')
    usage_records = db.relationship('EquipmentUsage', backref='equipment', lazy=True, cascade='all, delete-orphan')

    def calculate_depreciated_value(self):
        """Calculate current value based on depreciation"""
        if not self.purchase_date or not self.purchase_cost:
            return self.current_value

        years_owned = (datetime.utcnow() - self.purchase_date).days / 365.25
        depreciated = self.purchase_cost * ((1 - self.depreciation_rate) ** years_owned)
        return max(0, depreciated)

    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'equipmentCode': self.equipment_code,
            'description': self.description,
            'purchaseDate': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchaseCost': self.purchase_cost,
            'currentValue': self.current_value,
            'depreciationRate': self.depreciation_rate,
            'condition': self.condition,
            'location': self.location,
            'isActive': self.is_active,
            'supplierId': self.supplier_id,
            'imageUrl': self.image_url,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_details:
            data['maintenanceLogs'] = [log.to_dict() for log in self.maintenance_logs]
            data['usageRecords'] = [usage.to_dict() for usage in self.usage_records]
            data['depreciatedValue'] = self.calculate_depreciated_value()

        return data

    def __repr__(self):
        return f'<Equipment {self.id}: {self.name}>'


class EquipmentMaintenanceLog(db.Model):
    __tablename__ = 'equipment_maintenance_logs'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Maintenance Details
    maintenance_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    maintenance_type = db.Column(db.String(100), nullable=False)  # Service, Repair, Inspection, etc.
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float, default=0.0)

    # Scheduling
    next_due_date = db.Column(db.DateTime)

    # Who performed it
    performed_by = db.Column(db.String(150))
    notes = db.Column(db.Text)

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'equipmentId': self.equipment_id,
            'maintenanceDate': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'maintenanceType': self.maintenance_type,
            'description': self.description,
            'cost': self.cost,
            'nextDueDate': self.next_due_date.isoformat() if self.next_due_date else None,
            'performedBy': self.performed_by,
            'notes': self.notes,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<EquipmentMaintenanceLog {self.id}: {self.maintenance_type}>'


class EquipmentUsage(db.Model):
    __tablename__ = 'equipment_usage'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Assignment Details
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    returned_date = db.Column(db.DateTime)

    # Usage Tracking
    hours_used = db.Column(db.Float, default=0.0)
    days_used = db.Column(db.Integer, default=0)

    # Condition Tracking
    condition_on_return = db.Column(db.String(50))  # Excellent, Good, Fair, Poor, Damaged
    return_notes = db.Column(db.Text)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    # Audit Fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = db.relationship('Project', backref='equipment_used')
    staff = db.relationship('Staff', backref='equipment_used')

    @property
    def is_active(self):
        """Check if equipment is still in use"""
        return self.returned_date is None

    def to_dict(self):
        return {
            'id': self.id,
            'equipmentId': self.equipment_id,
            'projectId': self.project_id,
            'assignedDate': self.assigned_date.isoformat() if self.assigned_date else None,
            'returnedDate': self.returned_date.isoformat() if self.returned_date else None,
            'hoursUsed': self.hours_used,
            'daysUsed': self.days_used,
            'conditionOnReturn': self.condition_on_return,
            'returnNotes': self.return_notes,
            'staffId': self.staff_id,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<EquipmentUsage {self.id}: Equipment {self.equipment_id} on Project {self.project_id}>'
