from datetime import datetime
from extensions import db
from models.base import AuditMixin


class AttendancePhoto(db.Model, AuditMixin):
    """
    Photo record for attendance verification.
    Stores metadata and path to uploaded photos.
    Inherits audit fields: created_by_id, updated_by_id, company_id, created_at, updated_at
    """
    __tablename__ = 'attendance_photos'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    # Photo file information
    photo_path = db.Column(db.String(255), nullable=False)  # Path relative to /uploads/attendance/
    photo_size = db.Column(db.Integer)  # File size in bytes
    photo_width = db.Column(db.Integer)  # Image width in pixels
    photo_height = db.Column(db.Integer)  # Image height in pixels

    # Location information (from mobile GPS)
    latitude = db.Column(db.Float)  # GPS latitude
    longitude = db.Column(db.Float)  # GPS longitude
    location_accuracy = db.Column(db.Float)  # Location accuracy in meters

    # Timestamps
    timestamp_captured = db.Column(db.DateTime, nullable=False)  # When user captured photo
    timestamp_submitted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # When uploaded to server

    # Approval workflow
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('staff.id'))  # Staff member who approved
    approved_at = db.Column(db.DateTime)  # When photo was approved
    rejected_by = db.Column(db.Integer, db.ForeignKey('staff.id'))  # Staff member who rejected
    rejected_at = db.Column(db.DateTime)  # When photo was rejected
    rejection_reason = db.Column(db.String(255))  # Why photo was rejected


    # Relationships
    staff = db.relationship('Staff', foreign_keys=[staff_id], backref='attendance_photos')
    approver = db.relationship('Staff', foreign_keys=[approved_by], backref='approved_photos')
    rejector = db.relationship('Staff', foreign_keys=[rejected_by], backref='rejected_photos')

    def to_dict(self):
        """Convert model to dictionary for JSON response"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'staff_name': self.staff.name if self.staff else None,
            'staff_role': self.staff.role if self.staff else None,
            'photo_path': self.photo_path,
            'photo_size': self.photo_size,
            'photo_width': self.photo_width,
            'photo_height': self.photo_height,
            'photo_url': f'/api/attendance/photos/{self.id}',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_accuracy': self.location_accuracy,
            'timestamp_captured': self.timestamp_captured.isoformat() if self.timestamp_captured else None,
            'timestamp_submitted': self.timestamp_submitted.isoformat() if self.timestamp_submitted else None,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approver_name': self.approver.name if self.approver else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_by': self.rejected_by,
            'rejector_name': self.rejector.name if self.rejector else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'rejection_reason': self.rejection_reason,
            'time_to_submit_seconds': self._calculate_time_to_submit(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def _calculate_time_to_submit(self):
        """Calculate time difference between capture and submission in seconds"""
        if self.timestamp_captured and self.timestamp_submitted:
            delta = self.timestamp_submitted - self.timestamp_captured
            return int(delta.total_seconds())
        return None
