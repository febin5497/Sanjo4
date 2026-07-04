"""
Specialized Attendance Management Routers - Using BaseResourceRouter

Auto-generates CRUD endpoints for attendance entities:
- Attendance Records
- Attendance Photos

Also registers explicit route implementations for photo submission.
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from base.base_resource_router import BaseResourceRouter
from attendance_management.models.attendance import Attendance
from attendance_management.models.attendance_photo import AttendancePhoto
# Import the explicit attendance routes for photo submission
from attendance_management.routes.attendance_routes import attendance_bp as explicit_attendance_bp


# ==================== Attendance Router ====================

class AttendanceRouter(BaseResourceRouter):
    """Auto-generates Attendance CRUD endpoints"""
    model = Attendance
    entity_name = "Attendance"
    searchable_fields = ['staff_id', 'date']

    @classmethod
    def schema(cls, obj):
        """Schema for Attendance responses"""
        return {
            'id': obj.id,
            'staff_id': obj.staff_id,
            'date': obj.date.isoformat(),
            'present': obj.present,
            'half_day': obj.half_day,
            'night_shift': obj.night_shift,
            'overtime_hours': float(obj.overtime_hours) if obj.overtime_hours else 0,
            'leave_reason': obj.leave_reason,
            'punch_in_time': obj.punch_in_time.isoformat() if obj.punch_in_time else None,
            'punch_out_time': obj.punch_out_time.isoformat() if obj.punch_out_time else None,
            'punch_in_type': obj.punch_in_type,
            'punch_in_photo_id': obj.punch_in_photo_id,
            'status': obj.status,
            'approved_by': obj.approved_by,
            'approved_at': obj.approved_at.isoformat() if obj.approved_at else None,
            'rejection_reason': obj.rejection_reason,
            'approval_notes': obj.approval_notes,
            'created_at': obj.created_at.isoformat()
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Attendance creation"""
        errors = []
        if not data.get('staff_id'):
            errors.append({'field': 'staff_id', 'message': 'Staff ID required'})
        if not data.get('date'):
            errors.append({'field': 'date', 'message': 'Date required'})
        return errors


# ==================== Attendance Photo Router ====================

class AttendancePhotoRouter(BaseResourceRouter):
    """Auto-generates Attendance Photo CRUD endpoints"""
    model = AttendancePhoto
    entity_name = "Attendance Photo"
    searchable_fields = ['staff_id']

    @classmethod
    def schema(cls, obj):
        """Schema for Attendance Photo responses"""
        return {
            'id': obj.id,
            'staff_id': obj.staff_id if hasattr(obj, 'staff_id') else None,
            'photo_path': obj.photo_path if hasattr(obj, 'photo_path') else None,
            'photo_type': obj.photo_type if hasattr(obj, 'photo_type') else None,
            'captured_at': obj.captured_at.isoformat() if hasattr(obj, 'captured_at') and obj.captured_at else None,
            'status': obj.status if hasattr(obj, 'status') else None,
            'approved_by': obj.approved_by if hasattr(obj, 'approved_by') else None,
            'approved_at': obj.approved_at.isoformat() if hasattr(obj, 'approved_at') and obj.approved_at else None,
            'rejection_reason': obj.rejection_reason if hasattr(obj, 'rejection_reason') else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Attendance Photo creation"""
        errors = []
        if not data.get('staff_id'):
            errors.append({'field': 'staff_id', 'message': 'Staff ID required'})
        if not data.get('photo_path'):
            errors.append({'field': 'photo_path', 'message': 'Photo file path required'})
        if not data.get('photo_type'):
            errors.append({'field': 'photo_type', 'message': 'Photo type required (punch_in/punch_out)'})
        return errors


# ==================== Register Routers ====================

def register_attendance_routers(app):
    """Register all attendance management routers with Flask app"""
    # Register explicit attendance routes first (photo submission, punch-in, approvals)
    # This blueprint is defined in attendance_routes.py and uses the '/api/attendance' prefix
    app.register_blueprint(explicit_attendance_bp)

    # Attendance Photos CRUD (BaseResourceRouter for listing/filtering/pagination)
    # Note: This uses a different model approach and specific endpoints
    photo_bp = AttendancePhotoRouter.create_blueprint(url_prefix='/api/attendance/photos')
    app.register_blueprint(photo_bp)
