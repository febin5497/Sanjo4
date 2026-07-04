from extensions import db
from datetime import datetime


class Sale(db.Model):
    """Sales transaction model with GST compliance"""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    sale_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Amount breakdown
    subtotal = db.Column(db.Float, default=0.0, nullable=False)

    # GST Breakdown (Indian Tax Compliance)
    cgst_rate = db.Column(db.Float, default=0.0, nullable=False)
    sgst_rate = db.Column(db.Float, default=0.0, nullable=False)
    igst_rate = db.Column(db.Float, default=0.0, nullable=False)
    cgst_amount = db.Column(db.Float, default=0.0, nullable=False)
    sgst_amount = db.Column(db.Float, default=0.0, nullable=False)
    igst_amount = db.Column(db.Float, default=0.0, nullable=False)
    total_gst = db.Column(db.Float, default=0.0, nullable=False)

    grand_total = db.Column(db.Float, default=0.0, nullable=False)

    # GST Compliance fields
    customer_gstin = db.Column(db.String(15), nullable=True)
    company_gstin = db.Column(db.String(15), nullable=True)
    reverse_charge = db.Column(db.Boolean, default=False, nullable=False)
    supply_type = db.Column(db.String(20), default='Intra-state', nullable=False)

    status = db.Column(db.String(20), default='pending', nullable=False)
    notes = db.Column(db.Text, nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_items=False):
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "customer_id": self.customer_id,
            "user_id": self.user_id,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,

            # Amount breakdown
            "subtotal": self.subtotal,
            "cgst_rate": self.cgst_rate,
            "sgst_rate": self.sgst_rate,
            "igst_rate": self.igst_rate,
            "cgst_amount": self.cgst_amount,
            "sgst_amount": self.sgst_amount,
            "igst_amount": self.igst_amount,
            "total_gst": self.total_gst,
            "grand_total": self.grand_total,

            # GST Compliance
            "customer_gstin": self.customer_gstin,
            "company_gstin": self.company_gstin,
            "reverse_charge": self.reverse_charge,
            "supply_type": self.supply_type,

            "status": self.status,
            "notes": self.notes,
            "invoice_number": self.invoice_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data


class SaleItem(db.Model):
    """Individual line items in a sale"""
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='Units', nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    # GST for this item
    hsn_sac_code = db.Column(db.String(10), nullable=True)  # HSN or SAC code
    gst_rate = db.Column(db.Float, default=0.0, nullable=False)
    gst_amount = db.Column(db.Float, default=0.0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship('Material')

    def to_dict(self):
        return {
            "id": self.id,
            "sale_id": self.sale_id,
            "material_id": self.material_id,
            "material_name": self.material.name if self.material else None,
            "quantity": self.quantity,
            "unit": self.unit,
            "unit_price": self.unit_price,
            "total": self.total,
            "hsn_sac_code": self.hsn_sac_code,
            "gst_rate": self.gst_rate,
            "gst_amount": self.gst_amount,
        }
