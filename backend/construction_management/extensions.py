# extensions.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail


# Initialize the extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()


class SoftDeleteMixin:
    """
    Mixin to add soft-delete functionality to all SQLAlchemy models.
    Adds is_deleted, deleted_at, deleted_by columns plus soft_delete/restore methods.
    """
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by = db.Column(db.Integer, nullable=True)

    def soft_delete(self, user_id=None):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id
        db.session.add(self)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        db.session.add(self)

    @classmethod
    def get_active(cls, id):
        return cls.query.filter_by(id=id, is_deleted=False).first()

    @classmethod
    def get_all_active(cls):
        return cls.query.filter_by(is_deleted=False)


# Patch db.Model to include SoftDeleteMixin so ALL models automatically get it
class AppModel(db.Model, SoftDeleteMixin):
    __abstract__ = True
db.Model = AppModel
