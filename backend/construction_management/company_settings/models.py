
from extensions import db
from datetime import datetime


class Company(db.Model):
    """
    Company model for SaaS multi-tenancy support.
    Represents a tenant/organization in the system.
    """
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    logo_url = db.Column(db.String(255))

    # Tax and GST settings
    tax_percentage = db.Column(db.Float, default=0.0)  # Tax percentage for invoices
    gst_number = db.Column(db.String(50))  # GST/VAT registration number

    # Status: active, inactive, suspended
    status = db.Column(db.String(20), default='active')

    # Subscription fields
    subscription_plan = db.Column(db.String(50), default='free')  # free, pro, enterprise
    subscription_start_date = db.Column(db.DateTime)
    subscription_end_date = db.Column(db.DateTime)

    # Audit fields
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # Single-company system - no multi-tenancy relationships needed
    created_by = db.relationship("User", foreign_keys=[created_by_id], backref="companies_created")

    def to_dict(self):
        """Serialize company to JSON-friendly dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "logo_url": self.logo_url,
            "tax_percentage": self.tax_percentage,
            "gst_number": self.gst_number,
            "status": self.status,
            "subscription_plan": self.subscription_plan,
            "subscription_start_date": self.subscription_start_date.strftime("%Y-%m-%d") if self.subscription_start_date else None,
            "subscription_end_date": self.subscription_end_date.strftime("%Y-%m-%d") if self.subscription_end_date else None,
            "created_by_id": self.created_by_id,
            "created_by_name": self.created_by.username if self.created_by else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def get_default():
        """Get or create the single default company."""
        company = Company.query.first()
        if not company:
            company = Company(
                name='Default Company',
                status='active',
                subscription_plan='free',
                subscription_start_date=datetime.utcnow()
            )
            db.session.add(company)
            db.session.commit()
        return company

    def __repr__(self):
        return f"<Company {self.name} ({self.status})>"


class CompanySettings(db.Model):
    """
    CompanySettings model for managing company-specific configuration.
    Stores key-value pairs for company settings like timezone, fiscal year start, logo, etc.
    Replaces the simple working_hours/overtime_rate model with a flexible key-value store.
    """
    __tablename__ = "company_settings"

    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), nullable=False)  # e.g., "timezone", "fiscal_year_start", "working_hours"
    setting_value = db.Column(db.Text)  # Value can be string, json, etc.
    updated_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    updated_by = db.relationship("User", backref="company_settings_changes")

    # Unique constraint: only one value per setting key (single company system)
    __table_args__ = (db.UniqueConstraint("setting_key", name="unique_setting"),)

    def to_dict(self):
        """Serialize company setting to JSON-friendly dictionary."""
        return {
            "id": self.id,
            "setting_key": self.setting_key,
            "setting_value": self.setting_value,
            "updated_by_id": self.updated_by_id,
            "updated_by_name": self.updated_by.username if self.updated_by else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def __repr__(self):
        return f"<CompanySettings {self.setting_key}={self.setting_value}>"
