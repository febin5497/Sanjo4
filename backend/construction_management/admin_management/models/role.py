from datetime import datetime
from extensions import db

# Many-to-many junction table for Role-Permission
role_permission_association = db.Table(
    'role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):
    """
    Role model for defining role-based access control.
    Roles contain multiple permissions which define what users in that role can do.
    """
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_system_role = db.Column(db.Boolean, default=False)  # Cannot be deleted if True
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    permissions = db.relationship(
        'Permission',
        secondary=role_permission_association,
        backref='roles',
        lazy=True
    )

    def to_dict(self):
        """Serialize role to JSON-friendly dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_system_role': self.is_system_role,
            'permission_count': len(self.permissions),
            'permissions': [p.to_dict() for p in self.permissions],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<Role {self.name}>'
