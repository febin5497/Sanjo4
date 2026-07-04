from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'attendance', 'project', 'staff', 'system', etc.

    related_model = db.Column(db.String(50))  # 'attendance', 'project', 'staff', etc.
    related_id = db.Column(db.Integer)  # ID of the related object

    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # For mobile push notifications
    fcm_token = db.Column(db.String(500))  # Firebase Cloud Messaging token
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.notification_type,
            'relatedModel': self.related_model,
            'relatedId': self.related_id,
            'isRead': self.is_read,
            'readAt': self.read_at.isoformat() if self.read_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'isSent': self.is_sent,
            'sentAt': self.sent_at.isoformat() if self.sent_at else None,
        }

    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
