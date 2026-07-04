from extensions import db
from datetime import datetime


class Supplier(db.Model):
    """Supplier/Vendor model for purchase tracking"""
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    bank_account = db.Column(db.String(100), nullable=True)

    # Contact person details
    contact_person = db.Column(db.String(100), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)

    # Enhanced vendor fields
    bank_name = db.Column(db.String(150), nullable=True)
    account_number = db.Column(db.String(50), nullable=True)
    ifsc_code = db.Column(db.String(20), nullable=True)  # Indian bank IFSC code
    gstin = db.Column(db.String(15), nullable=True)  # GST Identification Number
    payment_terms = db.Column(db.String(100), nullable=True)  # e.g., Net 30, Net 60
    credit_limit = db.Column(db.Float, default=0)  # Credit limit in rupees
    performance_score = db.Column(db.Float, default=0)  # 0-100 based on on-time delivery
    on_time_delivery_percentage = db.Column(db.Float, default=0)  # % of on-time deliveries

    # Status and timestamps
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # Note: Purchase model defines the supplier relationship with backref='purchases'
    # So we don't create a duplicate relationship here

    # Database Indexes for Performance
    __table_args__ = (
        db.Index('idx_supplier_name', 'name'),
        db.Index('idx_supplier_is_active', 'is_active'),
        db.Index('idx_supplier_gstin', 'gstin'),
    )

    def to_dict(self):
        """Serialize supplier to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "tax_id": self.tax_id,
            "bank_account": self.bank_account,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "bank_name": self.bank_name,
            "account_number": self.account_number,
            "ifsc_code": self.ifsc_code,
            "gstin": self.gstin,
            "payment_terms": self.payment_terms,
            "credit_limit": self.credit_limit,
            "performance_score": self.performance_score,
            "on_time_delivery_percentage": self.on_time_delivery_percentage,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Supplier {self.name}>"
