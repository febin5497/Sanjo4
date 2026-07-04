from extensions import db
from datetime import datetime


class GoodsReceiptNote(db.Model):
    """Goods Receipt Note - tracks received materials"""
    __tablename__ = 'goods_receipt_notes'

    id = db.Column(db.Integer, primary_key=True)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)

    # Reference
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)

    # Receipt details
    receipt_date = db.Column(db.Date, nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=True)
    driver_name = db.Column(db.String(255), nullable=True)
    supplier_reference = db.Column(db.String(100), nullable=True)

    # Quality check
    quality_check_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, pass, fail, partial
    quality_check_notes = db.Column(db.Text, nullable=True)
    quality_checked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    quality_check_date = db.Column(db.DateTime, nullable=True)

    # Workflow
    status = db.Column(db.String(20), default='received', nullable=False)  # received, inspected, accepted, rejected
    accepted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)

    # Meta
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('GRNItem', cascade='all, delete-orphan', backref='grn')
    invoice_reconciliation = db.relationship('InvoiceReconciliation', uselist=False, backref='grn')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'grn_number': self.grn_number,
            'purchase_order_id': self.purchase_order_id,
            'company_id': self.company_id,
            'receipt_date': self.receipt_date.isoformat(),
            'vehicle_number': self.vehicle_number,
            'driver_name': self.driver_name,
            'supplier_reference': self.supplier_reference,
            'quality_check_status': self.quality_check_status,
            'quality_check_notes': self.quality_check_notes,
            'quality_checked_by_id': self.quality_checked_by_id,
            'quality_check_date': self.quality_check_date.isoformat() if self.quality_check_date else None,
            'status': self.status,
            'accepted_by_id': self.accepted_by_id,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data


class GRNItem(db.Model):
    """Individual items received in GRN"""
    __tablename__ = 'grn_items'

    id = db.Column(db.Integer, primary_key=True)
    grn_id = db.Column(db.Integer, db.ForeignKey('goods_receipt_notes.id'), nullable=False)
    po_item_id = db.Column(db.Integer, nullable=True)  # Reference to PurchaseItem

    # Item details
    description = db.Column(db.String(255), nullable=False)
    quantity_ordered = db.Column(db.Float, nullable=False)
    quantity_received = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))

    # Quality notes
    quality_remarks = db.Column(db.Text, nullable=True)
    is_damaged = db.Column(db.Boolean, default=False)
    damaged_quantity = db.Column(db.Float, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'grn_id': self.grn_id,
            'po_item_id': self.po_item_id,
            'description': self.description,
            'quantity_ordered': self.quantity_ordered,
            'quantity_received': self.quantity_received,
            'unit': self.unit,
            'quality_remarks': self.quality_remarks,
            'is_damaged': self.is_damaged,
            'damaged_quantity': self.damaged_quantity,
            'created_at': self.created_at.isoformat()
        }


class InvoiceReconciliation(db.Model):
    """Reconciliation between GRN and Invoice"""
    __tablename__ = 'invoice_reconciliations'

    id = db.Column(db.Integer, primary_key=True)
    grn_id = db.Column(db.Integer, db.ForeignKey('goods_receipt_notes.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)

    # Matching status
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, matched, discrepancy, resolved
    discrepancy_type = db.Column(db.String(50), nullable=True)  # qty_mismatch, rate_mismatch, date_mismatch, none

    # Details
    quantity_variance = db.Column(db.Float, default=0)
    amount_variance = db.Column(db.Float, default=0)
    notes = db.Column(db.Text, nullable=True)
    resolution = db.Column(db.Text, nullable=True)

    # Approval
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Meta
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'grn_id': self.grn_id,
            'invoice_id': self.invoice_id,
            'status': self.status,
            'discrepancy_type': self.discrepancy_type,
            'quantity_variance': self.quantity_variance,
            'amount_variance': self.amount_variance,
            'notes': self.notes,
            'resolution': self.resolution,
            'resolved_by_id': self.resolved_by_id,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
