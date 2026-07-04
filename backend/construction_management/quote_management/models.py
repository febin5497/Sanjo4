from extensions import db
from datetime import datetime, timedelta

class Quote(db.Model):
    __tablename__ = 'quotes'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    # Quote Information
    quote_number = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))

    # Who created it
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))

    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_date = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)

    # Financial Information
    subtotal = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)  # Tax percentage
    tax_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)

    # Status Workflow
    status = db.Column(db.String(50), default='Draft')  # Draft, Sent, Accepted, Rejected, Expired, Converted

    # Additional Info
    notes = db.Column(db.Text)
    terms_and_conditions = db.Column(db.Text)

    # Relationships
    client = db.relationship('Client', backref='quotes')
    supplier = db.relationship('Supplier', backref='quotes')
    user = db.relationship('User', backref='quotes')
    project = db.relationship('Project', backref='quotes')
    items = db.relationship('QuoteItem', backref='quote', lazy=True, cascade='all, delete-orphan')

    def calculate_totals(self):
        """Recalculate totals based on items"""
        self.subtotal = sum(item.total for item in self.items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'quoteNumber': self.quote_number,
            'clientId': self.client_id,
            'supplierId': self.supplier_id,
            'userId': self.user_id,
            'projectId': self.project_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'sentDate': self.sent_date.isoformat() if self.sent_date else None,
            'validUntil': self.valid_until.isoformat() if self.valid_until else None,
            'subtotal': self.subtotal,
            'taxRate': self.tax_rate,
            'taxAmount': self.tax_amount,
            'total': self.total,
            'status': self.status,
            'notes': self.notes,
            'termsAndConditions': self.terms_and_conditions,
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
            data['itemCount'] = len(self.items)

        return data

    def __repr__(self):
        return f'<Quote {self.id}: {self.quote_number}>'


class QuoteItem(db.Model):
    __tablename__ = 'quote_items'

    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)

    # Item Reference (can be material_id or custom description)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    description = db.Column(db.String(500), nullable=False)

    # Pricing
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_of_measure = db.Column(db.String(50), default='Unit')  # Unit, Meter, Sq.Ft, etc.
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    material = db.relationship('Material', backref='quote_items')

    def calculate_total(self):
        """Calculate line total"""
        self.total = self.quantity * self.unit_price

    def to_dict(self):
        return {
            'id': self.id,
            'quoteId': self.quote_id,
            'materialId': self.material_id,
            'description': self.description,
            'quantity': self.quantity,
            'unitOfMeasure': self.unit_of_measure,
            'unitPrice': self.unit_price,
            'total': self.total,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<QuoteItem {self.id}: {self.description}>'


class QuoteTemplate(db.Model):
    __tablename__ = 'quote_templates'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    template_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    is_default = db.Column(db.Boolean, default=False)

    # Template Content
    notes = db.Column(db.Text)
    terms_and_conditions = db.Column(db.Text)
    tax_rate = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='quote_templates')
    items = db.relationship('TemplateItem', backref='template', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'templateName': self.template_name,
            'description': self.description,
            'isDefault': self.is_default,
            'notes': self.notes,
            'termsAndConditions': self.terms_and_conditions,
            'taxRate': self.tax_rate,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_items:
            data['items'] = [item.to_dict() for item in self.items]

        return data

    def __repr__(self):
        return f'<QuoteTemplate {self.id}: {self.template_name}>'


class TemplateItem(db.Model):
    __tablename__ = 'template_items'

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('quote_templates.id'), nullable=False)

    # Item Reference
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    description = db.Column(db.String(500), nullable=False)

    # Default Values
    quantity_default = db.Column(db.Float, default=1.0)
    unit_of_measure = db.Column(db.String(50), default='Unit')
    unit_price = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    material = db.relationship('Material', backref='template_items')

    def to_dict(self):
        return {
            'id': self.id,
            'templateId': self.template_id,
            'materialId': self.material_id,
            'description': self.description,
            'quantityDefault': self.quantity_default,
            'unitOfMeasure': self.unit_of_measure,
            'unitPrice': self.unit_price,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<TemplateItem {self.id}: {self.description}>'
