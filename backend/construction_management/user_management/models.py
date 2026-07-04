from extensions import db, bcrypt
from datetime import datetime


class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    name = db.Column(db.String(255), nullable=True)

    email = db.Column(db.String(120), unique=True, nullable=True)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), default="worker")

    # Company relationship for multi-tenant support
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=True)
    company = db.relationship("Company", foreign_keys=[company_id])

    # Password change requirement (for first-time logins)
    password_change_required = db.Column(db.Boolean, default=False)

    # Account status
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Database Indexes for Performance
    __table_args__ = (
        db.Index('idx_user_company', 'company_id'),
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_username', 'username'),
        db.Index('idx_user_is_active', 'is_active'),
    )

    # Relationship to UserRole (created via backref in UserRole model)
    # user_roles property is automatically available through backref

    def set_password(self, raw_password):
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password, raw_password)

    def get_roles(self):
        """Get all roles for this user."""
        from admin_management.models import UserRole
        user_roles = UserRole.query.filter_by(user_id=self.id).all()
        return [ur.role for ur in user_roles]

    def get_permissions(self):
        """Get all permissions for this user."""
        from admin_management.models import UserRole
        user_roles = UserRole.query.filter_by(user_id=self.id).all()

        # Collect all permissions from all roles
        permissions = set()
        for user_role in user_roles:
            for permission in user_role.role.permissions:
                permissions.add(permission.name)

        return list(permissions)

    def has_permission(self, permission_name):
        """Check if user has a specific permission."""
        permissions = self.get_permissions()
        return permission_name in permissions

    def has_role(self, role_name):
        """Check if user has a specific role."""
        roles = self.get_roles()
        role_names = [r.name for r in roles]
        return role_name in role_names

    def change_password(self, new_password):
        """Change user password and mark password change as completed."""
        self.password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        self.password_change_required = False
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """Serialize user to JSON-friendly dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'company_id': self.company_id,
            'is_active': self.is_active,
            'password_change_required': self.password_change_required,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }