"""HSN/SAC Code Management for Indian GST Compliance"""
from extensions import db
from datetime import datetime


class HSNCode(db.Model):
    """HSN (Harmonized System of Nomenclature) Codes for goods"""
    __tablename__ = 'hsn_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # e.g., Construction Materials
    gst_rate = db.Column(db.Float, nullable=False)  # GST rate in percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'category': self.category,
            'gst_rate': self.gst_rate
        }


class SACCode(db.Model):
    """SAC (Service Accounting Code) for services"""
    __tablename__ = 'sac_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)  # e.g., Construction Services
    gst_rate = db.Column(db.Float, nullable=False)  # GST rate in percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'category': self.category,
            'gst_rate': self.gst_rate
        }


class GSTConfiguration(db.Model):
    """Company-specific GST configuration"""
    __tablename__ = 'gst_configuration'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, unique=True, nullable=False)
    gstin = db.Column(db.String(15), unique=True, nullable=False)  # 15-digit GSTIN
    company_name = db.Column(db.String(255), nullable=False)
    company_email = db.Column(db.String(120), nullable=True)
    company_phone = db.Column(db.String(20), nullable=True)
    company_address = db.Column(db.Text, nullable=True)
    state_code = db.Column(db.String(2), nullable=False)  # State code for GSTIN
    registration_type = db.Column(db.String(20), nullable=False)  # Regular, Composition, Casual
    gst_effective_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'gstin': self.gstin,
            'company_name': self.company_name,
            'company_email': self.company_email,
            'company_phone': self.company_phone,
            'company_address': self.company_address,
            'state_code': self.state_code,
            'registration_type': self.registration_type,
            'gst_effective_date': self.gst_effective_date.isoformat() if self.gst_effective_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
