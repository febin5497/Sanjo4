from datetime import datetime
from extensions import db


class AttendanceRecord(db.Model):
    """
    Attendance record for staff punch-in and punch-out.
    Tracks daily attendance with status workflow (pending -> approved -> punch_out_pending -> completed)
    """
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)

    # Timestamps
    punch_in_time = db.Column(db.DateTime)
    punch_out_time = db.Column(db.DateTime)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now().date())

    # Photo tracking
    punch_in_type = db.Column(db.String(20), default='photo')  # 'photo' or 'button'
    punch_in_photo_id = db.Column(db.Integer, db.ForeignKey('attendance_photos.id'))

    # Location tracking (from mobile GPS)
    latitude = db.Column(db.Float)  # GPS latitude
    longitude = db.Column(db.Float)  # GPS longitude
    location_accuracy = db.Column(db.Float)  # Location accuracy in meters

    # Status workflow
    status = db.Column(db.String(30), default='pending')  # pending, approved, rejected, punch_out_pending, completed

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    staff = db.relationship('Staff', backref='attendance_records')
    photo = db.relationship('AttendancePhoto', backref='attendance_records', foreign_keys=[punch_in_photo_id])

    def to_dict(self):
        """Convert model to dictionary for JSON response"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'staff_name': self.staff.name if self.staff else None,
            'staff_role': self.staff.role if self.staff else None,
            'punch_in_time': self.punch_in_time.isoformat() if self.punch_in_time else None,
            'punch_out_time': self.punch_out_time.isoformat() if self.punch_out_time else None,
            'date': self.date.isoformat() if self.date else None,
            'punch_in_type': self.punch_in_type,
            'punch_in_photo_id': self.punch_in_photo_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_accuracy': self.location_accuracy,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
