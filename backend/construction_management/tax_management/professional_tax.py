"""Professional Tax Management for Indian Tax Compliance"""
from extensions import db
from datetime import datetime


class ProfessionalTaxConfiguration(db.Model):
    """Professional Tax configuration by state"""
    __tablename__ = 'professional_tax_config'

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(50), unique=True, nullable=False)
    state_code = db.Column(db.String(2), nullable=False)  # State code like MH, KA, etc.
    monthly_amount = db.Column(db.Float, nullable=False)  # Monthly tax amount
    annual_amount = db.Column(db.Float, nullable=False)  # Annual amount
    effective_from = db.Column(db.Date, nullable=False)
    effective_to = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'state': self.state,
            'state_code': self.state_code,
            'monthly_amount': self.monthly_amount,
            'annual_amount': self.annual_amount,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'is_active': self.is_active
        }


class ProfessionalTaxDeduction(db.Model):
    """Monthly Professional Tax deductions for staff"""
    __tablename__ = 'professional_tax_deductions'

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(50), nullable=False)  # State where staff is working
    state_code = db.Column(db.String(2), nullable=False)

    month = db.Column(db.Integer, nullable=False)  # Month (1-12)
    year = db.Column(db.Integer, nullable=False)  # Financial year
    deduction_amount = db.Column(db.Float, nullable=False)
    salary_amount = db.Column(db.Float, nullable=False)  # Gross salary for reference

    deduction_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Paid
    government_receipt = db.Column(db.String(100), nullable=True)  # Government payment reference

    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'company_id': self.company_id,
            'state': self.state,
            'month': self.month,
            'year': self.year,
            'deduction_amount': self.deduction_amount,
            'salary_amount': self.salary_amount,
            'deduction_date': self.deduction_date.isoformat() if self.deduction_date else None,
            'payment_status': self.payment_status,
            'government_receipt': self.government_receipt,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
