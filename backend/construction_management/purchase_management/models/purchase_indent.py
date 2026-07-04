from extensions import db
from datetime import datetime


class PurchaseIndent(db.Model):
    """Material request/indent for procurement"""
    __tablename__ = 'purchase_indents'

    id = db.Column(db.Integer, primary_key=True)
    indent_number = db.Column(db.String(50), unique=True, nullable=False)

    # Reference
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)

    # Content
    description = db.Column(db.Text, nullable=False)
    justification = db.Column(db.Text, nullable=True)

    # Workflow
    status = db.Column(db.String(20), default='draft', nullable=False)  # draft, submitted, approved, rejected, po_created, completed
    indent_date = db.Column(db.Date, nullable=False)
    required_by_date = db.Column(db.Date, nullable=False)

    # Approval
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Meta
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = db.relationship('PurchaseIndentItem', cascade='all, delete-orphan', backref='indent')
    purchase_order = db.relationship('Purchase', uselist=False, backref='indent', foreign_keys='Purchase.indent_id')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'indent_number': self.indent_number,
            'project_id': self.project_id,
            'company_id': self.company_id,
            'description': self.description,
            'justification': self.justification,
            'status': self.status,
            'indent_date': self.indent_date.isoformat(),
            'required_by_date': self.required_by_date.isoformat(),
            'approved_by_id': self.approved_by_id,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data


class PurchaseIndentItem(db.Model):
    """Individual items in a purchase indent"""
    __tablename__ = 'purchase_indent_items'

    id = db.Column(db.Integer, primary_key=True)
    indent_id = db.Column(db.Integer, db.ForeignKey('purchase_indents.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)

    # Item details
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), default='qty')  # qty, bag, meter, liter, etc.
    estimated_rate = db.Column(db.Float, nullable=True)
    estimated_cost = db.Column(db.Float, nullable=True)

    # Notes
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'indent_id': self.indent_id,
            'material_id': self.material_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'estimated_rate': self.estimated_rate,
            'estimated_cost': self.estimated_cost,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
