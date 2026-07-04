from extensions import db
from datetime import datetime


class PurchaseReturn(db.Model):
    """Purchase return document for tracking material returns"""
    __tablename__ = 'purchase_returns'

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    return_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending, approved, cancelled

    reason = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    items = db.relationship('PurchaseReturnItem', backref='return', lazy=True, cascade='all, delete-orphan')
    purchase = db.relationship('Purchase', backref='returns')

    def to_dict(self, include_items=False):
        data = {
            "id": self.id,
            "purchase_id": self.purchase_id,
            "user_id": self.user_id,
            "return_date": self.return_date.isoformat() if self.return_date else None,
            "total_amount": self.total_amount,
            "status": self.status,
            "reason": self.reason,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data


class PurchaseReturnItem(db.Model):
    """Individual items being returned"""
    __tablename__ = 'purchase_return_items'

    id = db.Column(db.Integer, primary_key=True)
    return_id = db.Column(db.Integer, db.ForeignKey('purchase_returns.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    material = db.relationship('Material')

    def to_dict(self):
        return {
            "id": self.id,
            "return_id": self.return_id,
            "material_id": self.material_id,
            "material_name": self.material.name if self.material else None,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total": self.total,
        }
