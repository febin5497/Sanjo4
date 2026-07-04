from extensions import db
from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    make = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    registration_number = db.Column(db.String(100), nullable=False, unique=True)
    mileage = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # 'private', 'commercial', 'tipper'
    registration_date = db.Column(db.Date, nullable=True)
    pollution_date = db.Column(db.Date, nullable=True)
    insurance_date = db.Column(db.Date, nullable=True)
    tax_date = db.Column(db.Date, nullable=True)
    geology_certificate_date = db.Column(db.Date, nullable=True)
    emi_status = db.Column(db.Boolean, default=False)  # EMI status (True or False)
    emi_amount = db.Column(db.Float, nullable=True)  # EMI amount (if EMI status is True)

    # Relationships
    fuel_logs = db.relationship('FuelLog', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    maintenance_logs = db.relationship('MaintenanceLog', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    maintenance_schedules = db.relationship('MaintenanceSchedule', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    project_assignments = db.relationship('VehicleProjectAssignment', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    driver_assignments = db.relationship('DriverVehicleAssignment', backref='vehicle', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Vehicle {self.make} {self.model}>'

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'registration_number': self.registration_number,
            'mileage': self.mileage,
            'status': self.status,
            'type': self.type,
            'registration_date': self.registration_date,
            'pollution_date': self.pollution_date,
            'insurance_date': self.insurance_date,
            'tax_date': self.tax_date,
            'geology_certificate_date': self.geology_certificate_date,
            'emi_status': self.emi_status,
            'emi_amount': self.emi_amount
        }

    # Function to check if any certificates are expired
    def check_expired_certificates(self):
        expired_certificates = []
        current_date = datetime.utcnow().date()

        if self.registration_date and self.registration_date < current_date:
            expired_certificates.append('Registration')
        if self.pollution_date and self.pollution_date < current_date:
            expired_certificates.append('Pollution')
        if self.insurance_date and self.insurance_date < current_date:
            expired_certificates.append('Insurance')
        if self.tax_date and self.tax_date < current_date:
            expired_certificates.append('Tax')
        if self.geology_certificate_date and self.geology_certificate_date < current_date:
            expired_certificates.append('Geology Certificate')

        return expired_certificates

    # Function to renew expired certificates
    def renew_certificates(self, certificate_type):
        current_date = datetime.utcnow().date()

        if certificate_type == 'Registration':
            self.registration_date = current_date
        elif certificate_type == 'Pollution':
            self.pollution_date = current_date
        elif certificate_type == 'Insurance':
            self.insurance_date = current_date
        elif certificate_type == 'Tax':
            self.tax_date = current_date
        elif certificate_type == 'Geology Certificate':
            self.geology_certificate_date = current_date

        db.session.commit()
