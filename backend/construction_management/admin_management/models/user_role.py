from datetime import datetime
from extensions import db

class UserRole(db.Model):
    """
    UserRole junction model to assign roles to users.
    Supports multi-tenancy with company_id.
    A user can have multiple roles within the same company.
    """
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Who assigned this role

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='user_roles')
    role = db.relationship('Role', backref='user_assignments')
    # assigned_by references the User who assigned this role (optional)
    assigned_by = db.relationship('User', foreign_keys=[assigned_by_id], backref='roles_assigned_by', viewonly=True)

    # Unique constraint: user cannot have same role twice
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),)

    def to_dict(self):
        """Serialize user role assignment to JSON-friendly dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'assigned_at': self.assigned_at.strftime('%Y-%m-%d %H:%M:%S') if self.assigned_at else None,
            'assigned_by_id': self.assigned_by_id,
            'assigned_by_name': self.assigned_by.username if self.assigned_by else None
        }

    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'
