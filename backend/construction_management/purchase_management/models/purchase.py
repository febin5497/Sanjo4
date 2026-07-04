from extensions import db
from datetime import datetime
from models.base import AuditMixin
from constants.statuses import PurchaseStatus


class Purchase(db.Model, AuditMixin):
    """Purchase order model for tracking material purchases"""
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    indent_id = db.Column(db.Integer, db.ForeignKey('purchase_indents.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    purchase_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery_date = db.Column(db.DateTime, nullable=True)

    # Basic amounts
    subtotal = db.Column(db.Float, default=0.0, nullable=False)  # Before tax

    # GST Breakdown (Indian Tax Compliance)
    cgst_rate = db.Column(db.Float, default=0.0, nullable=False)  # Central GST %
    sgst_rate = db.Column(db.Float, default=0.0, nullable=False)  # State GST %
    igst_rate = db.Column(db.Float, default=0.0, nullable=False)  # Integrated GST %
    cgst_amount = db.Column(db.Float, default=0.0, nullable=False)  # CGST amount
    sgst_amount = db.Column(db.Float, default=0.0, nullable=False)  # SGST amount
    igst_amount = db.Column(db.Float, default=0.0, nullable=False)  # IGST amount
    total_gst = db.Column(db.Float, default=0.0, nullable=False)  # Total GST (CGST+SGST+IGST)

    # TDS Information
    tds_rate = db.Column(db.Float, default=0.0, nullable=True)  # TDS % (if applicable)
    tds_amount = db.Column(db.Float, default=0.0, nullable=True)  # TDS amount calculated

    # Final totals
    grand_total = db.Column(db.Float, default=0.0, nullable=False)  # subtotal + total_gst - tds
    net_payable = db.Column(db.Float, default=0.0, nullable=False)  # After TDS

    # Supplier & Invoice Details
    supplier_gstin = db.Column(db.String(15), nullable=True)  # Supplier's GSTIN
    company_gstin = db.Column(db.String(15), nullable=True)  # Company's GSTIN
    reverse_charge = db.Column(db.Boolean, default=False, nullable=False)  # If reverse charge applies
    supply_type = db.Column(db.String(20), default='Intra-state', nullable=False)  # Intra-state or Inter-state

    # Status and metadata
    status = db.Column(db.String(20), default=PurchaseStatus.DRAFT.value, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    po_number = db.Column(db.String(50), nullable=True)

    # Relationships
    items = db.relationship('PurchaseItem', backref='purchase', lazy=True, cascade='all, delete-orphan')
    supplier = db.relationship('Supplier', backref='purchases', foreign_keys=[supplier_id])

    def to_dict(self, include_items=False):
        """Serialize purchase to dictionary with GST compliance"""
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier.name if self.supplier else None,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,

            # Amount breakdown (Indian GST format)
            "subtotal": self.subtotal,
            "cgst_rate": self.cgst_rate,
            "sgst_rate": self.sgst_rate,
            "igst_rate": self.igst_rate,
            "cgst_amount": self.cgst_amount,
            "sgst_amount": self.sgst_amount,
            "igst_amount": self.igst_amount,
            "total_gst": self.total_gst,
            "tds_rate": self.tds_rate,
            "tds_amount": self.tds_amount,
            "grand_total": self.grand_total,
            "net_payable": self.net_payable,

            # GST Compliance fields
            "supplier_gstin": self.supplier_gstin,
            "company_gstin": self.company_gstin,
            "reverse_charge": self.reverse_charge,
            "supply_type": self.supply_type,

            # Status and metadata
            "status": self.status,
            "notes": self.notes,
            "po_number": self.po_number,

            # Audit trail (from AuditMixin)
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id,
            "updated_by_id": self.updated_by_id,
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data

    def __repr__(self):
        return f"<Purchase {self.po_number}>"


class PurchaseItem(db.Model):
    """Individual line items in a purchase order"""
    __tablename__ = 'purchase_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='Units', nullable=False)  # Units, KG, Meter, etc.
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)  # quantity * unit_price

    # GST for this item
    hsn_code = db.Column(db.String(10), nullable=True)  # HSN Code for this material
    gst_rate = db.Column(db.Float, default=0.0, nullable=False)  # GST rate for this item
    gst_amount = db.Column(db.Float, default=0.0, nullable=False)  # Calculated GST for this item

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    material = db.relationship('Material', backref='purchase_items')

    def to_dict(self):
        """Serialize purchase item to dictionary with GST compliance"""
        return {
            "id": self.id,
            "purchase_id": self.purchase_id,
            "material_id": self.material_id,
            "material_name": self.material.name if self.material else None,
            "quantity": self.quantity,
            "unit": self.unit,
            "unit_price": self.unit_price,
            "total": self.total,
            "hsn_code": self.hsn_code,
            "gst_rate": self.gst_rate,
            "gst_amount": self.gst_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<PurchaseItem purchase={self.purchase_id} material={self.material_id}>"
