from extensions import db
from datetime import datetime

class ChartOfAccounts(db.Model):
    __tablename__ = 'chart_of_accounts'
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # asset, liability, equity, revenue, expense
    category = db.Column(db.String(100), nullable=False)  # Materials, Labor, Equipment, etc.
    description = db.Column(db.Text)
    parent_account_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id', ondelete='SET NULL'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id, 'account_code': self.account_code, 'name': self.name,
            'type': self.account_type, 'category': self.category, 'description': self.description,
            'is_active': self.is_active
        }
