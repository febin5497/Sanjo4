"""TDS (Tax Deducted at Source) Management for Indian Tax Compliance"""
from extensions import db
from datetime import datetime


class TDSConfiguration(db.Model):
    """TDS Configuration for different payment types"""
    __tablename__ = 'tds_configuration'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(20), nullable=False)  # e.g., 194C, 194J, 194D
    section_name = db.Column(db.String(100), nullable=False)  # e.g., "Construction Services"
    tds_rate = db.Column(db.Float, nullable=False)  # TDS rate in percentage
    threshold_amount = db.Column(db.Float, nullable=True)  # Amount above which TDS is applicable
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'section': self.section,
            'section_name': self.section_name,
            'tds_rate': self.tds_rate,
            'threshold_amount': self.threshold_amount,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TDSPayment(db.Model):
    """Track TDS payments made by the company"""
    __tablename__ = 'tds_payments'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    payment_id = db.Column(db.Integer, nullable=False)  # Reference to purchase/payment
    payment_type = db.Column(db.String(20), nullable=False)  # Purchase, Payment to contractor, etc.
    vendor_name = db.Column(db.String(255), nullable=False)
    vendor_gstin = db.Column(db.String(15), nullable=True)
    vendor_pan = db.Column(db.String(10), nullable=True)

    tds_section = db.Column(db.String(20), nullable=False)  # 194C, 194J, etc.
    payment_amount = db.Column(db.Float, nullable=False)  # Gross payment amount
    tds_rate = db.Column(db.Float, nullable=False)  # TDS rate applied
    tds_amount = db.Column(db.Float, nullable=False)  # Calculated TDS
    net_amount = db.Column(db.Float, nullable=False)  # After TDS deduction

    payment_date = db.Column(db.Date, nullable=False)
    financial_year = db.Column(db.String(10), nullable=False)  # e.g., "2023-24"
    quarter = db.Column(db.Integer, nullable=True)  # Q1, Q2, Q3, Q4

    tds_deposited = db.Column(db.Boolean, default=False, nullable=False)
    deposit_date = db.Column(db.Date, nullable=True)
    challan_number = db.Column(db.String(50), nullable=True)  # Government challan number

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'payment_id': self.payment_id,
            'payment_type': self.payment_type,
            'vendor_name': self.vendor_name,
            'vendor_gstin': self.vendor_gstin,
            'vendor_pan': self.vendor_pan,
            'tds_section': self.tds_section,
            'payment_amount': self.payment_amount,
            'tds_rate': self.tds_rate,
            'tds_amount': self.tds_amount,
            'net_amount': self.net_amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'financial_year': self.financial_year,
            'quarter': self.quarter,
            'tds_deposited': self.tds_deposited,
            'deposit_date': self.deposit_date.isoformat() if self.deposit_date else None,
            'challan_number': self.challan_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TDSCertificate(db.Model):
    """TDS Certificate for vendors (for their records)"""
    __tablename__ = 'tds_certificates'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    vendor_name = db.Column(db.String(255), nullable=False)
    vendor_pan = db.Column(db.String(10), nullable=False)
    vendor_address = db.Column(db.Text, nullable=True)

    financial_year = db.Column(db.String(10), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)

    total_payments = db.Column(db.Float, nullable=False)
    total_tds = db.Column(db.Float, nullable=False)

    certificate_date = db.Column(db.Date, nullable=False)
    certificate_pdf_path = db.Column(db.String(255), nullable=True)

    issued = db.Column(db.Boolean, default=False, nullable=False)
    issued_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'vendor_name': self.vendor_name,
            'vendor_pan': self.vendor_pan,
            'vendor_address': self.vendor_address,
            'financial_year': self.financial_year,
            'certificate_number': self.certificate_number,
            'total_payments': self.total_payments,
            'total_tds': self.total_tds,
            'certificate_date': self.certificate_date.isoformat() if self.certificate_date else None,
            'issued': self.issued,
            'issued_date': self.issued_date.isoformat() if self.issued_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
