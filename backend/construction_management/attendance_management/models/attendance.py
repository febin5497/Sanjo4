from extensions import db
from datetime import date, datetime
from models.base import AuditMixin


class Attendance(db.Model, AuditMixin):
    """
    Unified Attendance model combining simple daily tracking with photo-based approval workflow.
    Handles both photo-based punch-in/out and manual attendance marking.
    """
    __tablename__ = 'attendance'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    # Attendance Status Fields (for reporting)
    present = db.Column(db.Boolean, default=False)
    half_day = db.Column(db.Boolean, default=False)
    night_shift = db.Column(db.Boolean, default=False)
    overtime_hours = db.Column(db.Float, default=0.0)
    leave_reason = db.Column(db.String(255), nullable=True)

    # Punch-in/out Times
    punch_in_time = db.Column(db.DateTime, nullable=True)
    punch_out_time = db.Column(db.DateTime, nullable=True)

    # Photo-based Workflow Fields
    punch_in_type = db.Column(db.String(20), default='photo')  # 'photo' or 'manual'
    punch_in_photo_id = db.Column(db.Integer, db.ForeignKey('attendance_photos.id'), nullable=True)
    status = db.Column(db.String(30), default='pending')  # pending, approved, rejected, punch_out_pending, completed

    # Photo Approval Information
    approved_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=True)  # Staff member who approved
    approved_at = db.Column(db.DateTime, nullable=True)  # When photo was approved
    rejection_reason = db.Column(db.String(255), nullable=True)  # Why photo was rejected
    approval_notes = db.Column(db.Text, nullable=True)  # Additional approval notes

    # Relationships
    staff = db.relationship('Staff', backref='attendance_records', foreign_keys=[staff_id])
    photo = db.relationship('AttendancePhoto', backref='attendance_records', foreign_keys=[punch_in_photo_id])
    approver = db.relationship('Staff', foreign_keys=[approved_by], backref='approved_attendances')

    def to_dict(self):
        return {
            "id": self.id,
            "staff_id": self.staff_id,
            "staff_name": self.staff.name if self.staff else None,
            "staff_role": self.staff.role if self.staff else None,
            "date": self.date.isoformat() if self.date else None,
            "present": self.present,
            "half_day": self.half_day,
            "night_shift": self.night_shift,
            "overtime_hours": self.overtime_hours,
            "leave_reason": self.leave_reason,
            "punch_in_time": self.punch_in_time.isoformat() if self.punch_in_time else None,
            "punch_out_time": self.punch_out_time.isoformat() if self.punch_out_time else None,
            "punch_in_type": self.punch_in_type,
            "punch_in_photo_id": self.punch_in_photo_id,
            "status": self.status,
            "approved_by": self.approved_by,
            "approver_name": self.approver.name if self.approver else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejection_reason": self.rejection_reason,
            "approval_notes": self.approval_notes,
            "company_id": self.company_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id,
            "updated_by_id": self.updated_by_id,
        }

    def hours_worked(self):
        """Calculate hours worked between punch-in and punch-out"""
        if self.punch_in_time and self.punch_out_time:
            delta = self.punch_out_time - self.punch_in_time
            return delta.total_seconds() / 3600  # Convert to hours
        return 0.0
