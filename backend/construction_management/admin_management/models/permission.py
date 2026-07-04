from datetime import datetime
from extensions import db

class Permission(db.Model):
    """
    Permission model for defining granular access control.
    Permissions are assigned to Roles.
    """
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # e.g., "create_project", "approve_invoice"
    category = db.Column(db.String(50), nullable=False)  # e.g., "Projects", "Staff", "Finance", "Admin"
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Serialize permission to JSON-friendly dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Permission {self.name}>'
