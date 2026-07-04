from datetime import datetime
from extensions import db

class ActivityLog(db.Model):
    """
    ActivityLog model to track all user actions for audit compliance.
    Logs Create, Update, Delete operations across all entities.
    """
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # What entity was changed
    entity_type = db.Column(db.String(50), nullable=False)  # e.g., "Staff", "Project", "Invoice", "User"
    entity_id = db.Column(db.Integer)  # ID of the entity that was changed
    entity_name = db.Column(db.String(255))  # Name/description of entity for easier reading

    # What action was performed
    action = db.Column(db.String(20), nullable=False)  # "CREATE", "UPDATE", "DELETE", "APPROVE", etc.

    # Change tracking (for updates)
    old_value = db.Column(db.Text)  # JSON string of old values
    new_value = db.Column(db.Text)  # JSON string of new values

    # Request information
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref='activity_logs')

    def to_dict(self, include_changes=True):
        """Serialize activity log to JSON-friendly dictionary."""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else 'Unknown',
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name,
            'action': self.action,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

        if include_changes and self.action in ['UPDATE', 'CREATE']:
            result['old_value'] = self.old_value
            result['new_value'] = self.new_value

        return result

    def __repr__(self):
        return f'<ActivityLog {self.action} {self.entity_type}#{self.entity_id} by user#{self.user_id}>'
