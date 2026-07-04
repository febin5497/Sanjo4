from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from attendance_management.models.attendance_photo import AttendancePhoto
from staff_management.models import Staff
from attendance_management.services.photo_service import PhotoService
from attendance_management.utils.validators import PhotoValidator
from user_management.models import User
from utils.response_formatter import paginated_response
from datetime import datetime, timedelta
import os

# Lazy import for Attendance to avoid reload issues
def get_attendance_model():
    """Lazy load Attendance model to avoid circular import and reload issues"""
    from attendance_management.models import Attendance
    return Attendance

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/attendance")
attendance_bp.strict_slashes = False


# ============================================
# VALIDATION HELPERS
# ============================================
def validate_attendance_data(data):
    """Validate attendance input data"""
    errors = []

    if 'staff_id' not in data or data['staff_id'] is None:
        errors.append("Staff ID is required")
    else:
        try:
            staff_id = int(data['staff_id'])
            staff = Staff.query.get(staff_id)
            if not staff:
                errors.append("Staff member not found")
        except (ValueError, TypeError):
            errors.append("Staff ID must be a valid integer")

    if 'date' not in data or not data['date']:
        errors.append("Date is required")
    else:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date format. Use YYYY-MM-DD")

    if 'present' in data:
        if not isinstance(data['present'], bool):
            errors.append("Present must be a boolean value")

    if 'half_day' in data:
        if not isinstance(data['half_day'], bool):
            errors.append("Half day must be a boolean value")

    if 'night_shift' in data:
        if not isinstance(data['night_shift'], bool):
            errors.append("Night shift must be a boolean value")

    if 'overtime_hours' in data:
        try:
            overtime = float(data['overtime_hours'])
            if overtime < 0:
                errors.append("Overtime hours cannot be negative")
        except (ValueError, TypeError):
            errors.append("Overtime hours must be a valid number")

    return errors


# ============================================
# GET ALL ATTENDANCE (With Pagination & Filtering)
# ============================================
@attendance_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def get_attendance():
    """Get all attendance records with pagination and filtering"""
    try:
        Attendance = get_attendance_model()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        staff_id = request.args.get('staff_id', None, type=int)
        department = request.args.get('department', None, type=str)
        start_date = request.args.get('start_date', None, type=str)
        end_date = request.args.get('end_date', None, type=str)
        present_only = request.args.get('present_only', 'false', type=str).lower() == 'true'

        if page <= 0 or per_page <= 0:
            return jsonify({"error": "Page and per_page must be positive integers"}), 400

        query = Attendance.query

        # Apply filters
        if staff_id:
            query = query.filter(Attendance.staff_id == staff_id)

        if department:
            # Join with Staff table to filter by role/department
            query = query.join(Staff).filter(Staff.role == department)

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date >= start)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date <= end)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

        if present_only:
            query = query.filter(Attendance.present == True)

        # Order by date descending
        query = query.order_by(Attendance.date.desc())

        # Apply pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Enrich attendance data with staff information
        attendance_data = []
        for att in paginated.items:
            att_dict = att.to_dict()
            staff = Staff.query.get(att.staff_id)
            if staff:
                att_dict['staff_name'] = staff.name
                att_dict['staff_role'] = staff.role
            attendance_data.append(att_dict)

        return paginated_response(
            items=attendance_data,
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Attendance records retrieved successfully"
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# GET ATTENDANCE BY ID
# ============================================
@attendance_bp.route('/<int:attendance_id>', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def get_attendance_by_id(attendance_id):
    """Get attendance record by ID"""
    try:
        Attendance = get_attendance_model()
        attendance = Attendance.query.get(attendance_id)

        if not attendance:
            return jsonify({"success": False, "error": "Attendance record not found"}), 404

        att_dict = attendance.to_dict()
        staff = Staff.query.get(attendance.staff_id)
        if staff:
            att_dict['staff_name'] = staff.name
            att_dict['staff_role'] = staff.role

        return jsonify({"success": True, "data": att_dict}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# CREATE ATTENDANCE
# ============================================
@attendance_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_attendance():
    """Create new attendance record"""
    try:
        Attendance = get_attendance_model()
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Validate data
        errors = validate_attendance_data(data)
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        staff_id = int(data['staff_id'])
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Check for duplicate attendance on same date
        existing = Attendance.query.filter_by(
            staff_id=staff_id,
            date=date_obj
        ).first()
        if existing:
            return jsonify({"success": False, "error": "Attendance already marked for this date"}), 409

        # Create new attendance record
        attendance = Attendance(
            staff_id=staff_id,
            date=date_obj,
            present=data.get('present', False),
            half_day=data.get('half_day', False),
            night_shift=data.get('night_shift', False),
            overtime_hours=float(data.get('overtime_hours', 0)),
            project_id=data.get('project_id')
        )

        db.session.add(attendance)
        db.session.commit()

        att_dict = attendance.to_dict()
        staff = Staff.query.get(attendance.staff_id)
        if staff:
            att_dict['staff_name'] = staff.name
            att_dict['staff_role'] = staff.role

        return jsonify({
            "success": True,
            "message": "Attendance marked successfully",
            "data": att_dict
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# UPDATE ATTENDANCE
# ============================================
@attendance_bp.route('/<int:attendance_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_attendance(attendance_id):
    """Update attendance record"""
    try:
        Attendance = get_attendance_model()
        attendance = Attendance.query.get(attendance_id)

        if not attendance:
            return jsonify({"success": False, "error": "Attendance record not found"}), 404

        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Validate data if updating key fields
        if any(k in data for k in ['staff_id', 'date', 'present', 'half_day', 'night_shift', 'overtime_hours']):
            temp_data = {
                'staff_id': data.get('staff_id', attendance.staff_id),
                'date': data.get('date', attendance.date.isoformat()),
                'present': data.get('present', attendance.present),
                'half_day': data.get('half_day', attendance.half_day),
                'night_shift': data.get('night_shift', attendance.night_shift),
                'overtime_hours': data.get('overtime_hours', attendance.overtime_hours)
            }
            errors = validate_attendance_data(temp_data)
            if errors:
                return jsonify({"success": False, "errors": errors}), 400

        # Update fields
        if 'staff_id' in data:
            attendance.staff_id = int(data['staff_id'])
        if 'date' in data:
            attendance.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'present' in data:
            attendance.present = bool(data['present'])
        if 'half_day' in data:
            attendance.half_day = bool(data['half_day'])
        if 'night_shift' in data:
            attendance.night_shift = bool(data['night_shift'])
        if 'overtime_hours' in data:
            attendance.overtime_hours = float(data['overtime_hours'])

        db.session.commit()

        att_dict = attendance.to_dict()
        staff = Staff.query.get(attendance.staff_id)
        if staff:
            att_dict['staff_name'] = staff.name
            att_dict['staff_role'] = staff.role

        return jsonify({
            "success": True,
            "message": "Attendance updated successfully",
            "data": att_dict
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# DELETE ATTENDANCE
# ============================================
@attendance_bp.route('/<int:attendance_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_attendance(attendance_id):
    """Delete attendance record"""
    try:
        Attendance = get_attendance_model()
        attendance = Attendance.query.get(attendance_id)

        if not attendance:
            return jsonify({"success": False, "error": "Attendance record not found"}), 404

        db.session.delete(attendance)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Attendance record deleted successfully"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# GET ATTENDANCE STATISTICS
# ============================================
@attendance_bp.route('/stats/<int:staff_id>', methods=['GET'], strict_slashes=False)
@jwt_required(optional=True)
def get_attendance_stats(staff_id):
    """Get attendance statistics for a staff member"""
    try:
        Attendance = get_attendance_model()
        start_date = request.args.get('start_date', None, type=str)
        end_date = request.args.get('end_date', None, type=str)

        query = Attendance.query.filter(Attendance.staff_id == staff_id)

        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date >= start)
            except ValueError:
                return jsonify({"error": "Invalid start_date format"}), 400

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date <= end)
            except ValueError:
                return jsonify({"error": "Invalid end_date format"}), 400

        records = query.all()

        total_days = len(records)
        present_days = sum(1 for r in records if r.present and not r.half_day)
        half_days = sum(1 for r in records if r.half_day)
        absent_days = sum(1 for r in records if not r.present and not r.half_day)
        night_shifts = sum(1 for r in records if r.night_shift)
        total_overtime = sum(r.overtime_hours for r in records)

        return jsonify({
            "success": True,
            "data": {
                "staff_id": staff_id,
                "total_days": total_days,
                "present_days": present_days,
                "half_days": half_days,
                "absent_days": absent_days,
                "night_shifts": night_shifts,
                "total_overtime_hours": round(total_overtime, 2),
                "attendance_percentage": round((present_days + half_days * 0.5) / total_days * 100, 2) if total_days > 0 else 0
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# BULK MARK ATTENDANCE
# ============================================
@attendance_bp.route('/bulk/mark', methods=['POST'], strict_slashes=False)
@jwt_required()
def bulk_mark_attendance():
    """Bulk mark attendance for multiple staff"""
    try:
        Attendance = get_attendance_model()
        data = request.get_json()

        if not data or 'records' not in data:
            return jsonify({"success": False, "error": "No records provided"}), 400

        records = data['records']
        if not isinstance(records, list):
            return jsonify({"success": False, "error": "Records must be a list"}), 400

        created = 0
        errors = []

        for i, record in enumerate(records):
            try:
                # Validate each record
                record_errors = validate_attendance_data(record)
                if record_errors:
                    errors.append(f"Record {i+1}: {', '.join(record_errors)}")
                    continue

                staff_id = int(record['staff_id'])
                date_obj = datetime.strptime(record['date'], '%Y-%m-%d').date()

                # Check for duplicate
                existing = Attendance.query.filter_by(
                    staff_id=staff_id,
                    date=date_obj
                ).first()
                if existing:
                    errors.append(f"Record {i+1}: Attendance already exists for this date")
                    continue

                # Create attendance
                attendance = Attendance(
                    staff_id=staff_id,
                    date=date_obj,
                    present=record.get('present', False),
                    half_day=record.get('half_day', False),
                    night_shift=record.get('night_shift', False),
                    overtime_hours=float(record.get('overtime_hours', 0)),
                    project_id=record.get('project_id')
                )
                db.session.add(attendance)
                created += 1
            except Exception as e:
                errors.append(f"Record {i+1}: {str(e)}")

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{created} attendance records created",
            "created": created,
            "errors": errors if errors else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# PHOTO-BASED PUNCH IN
# ============================================
@attendance_bp.route('/punch-in-photo', methods=['POST'], strict_slashes=False)
@jwt_required()
def punch_in_photo():
    """Upload photo for attendance punch in"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()

        # Get user and their company
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Get staff record for current user
        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        # Check if photo file is present
        if 'photo' not in request.files:
            return jsonify({"success": False, "error": "No photo file provided"}), 400

        photo_file = request.files['photo']
        if not photo_file or photo_file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400

        # Get timestamp from request
        timestamp_captured = request.form.get('timestamp_captured')
        if not timestamp_captured:
            return jsonify({"success": False, "error": "Timestamp required"}), 400

        # Save photo using PhotoService
        result = PhotoService.save_photo(
            file_obj=photo_file,
            staff_id=staff.id,
            timestamp_captured=timestamp_captured
        )

        if not result.get('success'):
            return jsonify({"success": False, "error": result.get('error')}), 400

        # Auto-mark attendance as present for today
        today = datetime.utcnow().date()
        existing_attendance = Attendance.query.filter_by(
            staff_id=staff.id,
            date=today
        ).first()

        if not existing_attendance:
            # Create new attendance record as present
            attendance = Attendance(
                staff_id=staff.id,
                date=today,
                present=True,
                half_day=False,
                night_shift=False,
                overtime_hours=0
            )
            db.session.add(attendance)
            db.session.commit()

        return jsonify({
            "success": True,
            "message": "Photo submitted successfully. Waiting for approval.",
            "photo_id": result.get('photo_id'),
            "photo_data": result.get('photo_data')
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# GET PHOTO FILE
# ============================================
@attendance_bp.route('/photos/<int:photo_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_photo(photo_id):
    """Retrieve photo file by ID (requires JWT authentication)"""
    try:
        file_path, photo_record = PhotoService.get_photo_file(photo_id)

        if not file_path:
            return jsonify({"success": False, "error": "Photo not found"}), 404

        if not os.path.exists(file_path):
            return jsonify({"success": False, "error": "Photo file not found on server"}), 404

        return send_file(file_path, mimetype='image/jpeg', download_name=f"photo_{photo_id}.jpg")

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# GET TODAY'S ATTENDANCE STATUS
# ============================================
@attendance_bp.route('/today-status', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_today_status():
    """Get current user's attendance status for today"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()

        # Get staff record
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        today = datetime.utcnow().date()

        # Get today's attendance
        attendance = Attendance.query.filter_by(
            staff_id=staff.id,
            date=today
        ).first()

        # Get today's photo submissions
        photo = AttendancePhoto.query.filter(
            AttendancePhoto.staff_id == staff.id,
            AttendancePhoto.timestamp_captured >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).order_by(AttendancePhoto.created_at.desc()).first()

        return jsonify({
            "success": True,
            "data": {
                "staff_id": staff.id,
                "staff_name": staff.name,
                "date": today.isoformat(),
                "attendance_marked": attendance is not None,
                "attendance_status": attendance.to_dict() if attendance else None,
                "photo_submitted": photo is not None,
                "photo_status": photo.to_dict() if photo else None,
                "photo_approval_status": photo.approval_status if photo else None
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============================================
# GET ATTENDANCE REPORT (Date Range)
# ============================================
@attendance_bp.route('/report', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_attendance_report():
    """Get current user's attendance report for date range"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()
        start_date = request.args.get('start_date', None, type=str)
        end_date = request.args.get('end_date', None, type=str)

        # Get staff record
        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        # Build query
        query = Attendance.query.filter_by(staff_id=staff.id)

        # Apply date filters
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date >= start)
            except ValueError:
                return jsonify({"success": False, "error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Attendance.date <= end)
            except ValueError:
                return jsonify({"success": False, "error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

        records = query.order_by(Attendance.date.desc()).all()

        return jsonify({
            "success": True,
            "data": [{
                "staff_id": staff.id,
                "staff_name": staff.name,
                "records": [record.to_dict() for record in records]
            }]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# PUNCH OUT
# ============================================
@attendance_bp.route('/punch-out', methods=['POST'], strict_slashes=False)
@jwt_required()
def punch_out():
    """Record punch out for current user"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()
        today = datetime.utcnow().date()

        # Get staff record
        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        # Get today's attendance
        attendance = Attendance.query.filter_by(
            staff_id=staff.id,
            date=today
        ).first()

        if not attendance:
            return jsonify({"success": False, "error": "No punch in record found for today"}), 404

        # Update punch out time
        attendance.punch_out_time = datetime.utcnow().time()
        db.session.commit()

        return jsonify({
            "success": True,
            "data": attendance.to_dict(),
            "message": "Punch out recorded successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# MARK LEAVE
# ============================================
@attendance_bp.route('/mark-leave', methods=['POST'], strict_slashes=False)
@jwt_required()
def mark_leave():
    """Mark attendance as leave for current user"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()
        data = request.get_json()
        today = datetime.utcnow().date()

        # Get staff record
        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        # Get or create today's attendance
        attendance = Attendance.query.filter_by(
            staff_id=staff.id,
            date=today
        ).first()

        if not attendance:
            attendance = Attendance(
                staff_id=staff.id,
                date=today,
                present=False,
                half_day=False,
                night_shift=False,
                overtime_hours=0.0
            )
            db.session.add(attendance)

        # Mark as leave
        attendance.present = False
        attendance.leave_reason = data.get('leave_reason', '')
        db.session.commit()

        return jsonify({
            "success": True,
            "data": attendance.to_dict(),
            "message": "Leave marked successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# UPDATE OVERTIME
# ============================================
@attendance_bp.route('/update-overtime', methods=['POST'], strict_slashes=False)
@jwt_required()
def update_overtime():
    """Update overtime hours for current user's today's attendance"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()
        data = request.get_json()
        today = datetime.utcnow().date()

        # Validate overtime hours
        try:
            overtime_hours = float(data.get('overtime_hours', 0))
            if overtime_hours < 0:
                return jsonify({"success": False, "error": "Overtime hours cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Overtime hours must be a valid number"}), 400

        # Get staff record
        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        # Get today's attendance
        attendance = Attendance.query.filter_by(
            staff_id=staff.id,
            date=today
        ).first()

        if not attendance:
            return jsonify({"success": False, "error": "No attendance record found for today"}), 404

        # Update overtime
        attendance.overtime_hours = overtime_hours
        db.session.commit()

        return jsonify({
            "success": True,
            "data": attendance.to_dict(),
            "message": f"Overtime updated to {overtime_hours} hours"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# UPDATE NIGHT SHIFT
# ============================================
@attendance_bp.route('/update-night-shift', methods=['POST'], strict_slashes=False)
@jwt_required()
def update_night_shift():
    """Update night shift status for current user's today's attendance"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()
        data = request.get_json()
        today = datetime.utcnow().date()

        # Validate night shift
        night_shift = data.get('night_shift', False)
        if not isinstance(night_shift, bool):
            return jsonify({"success": False, "error": "Night shift must be a boolean value"}), 400

        # Get staff record
        staff = Staff.query.filter_by(user_id=user_id).first()
        if not staff:
            return jsonify({"success": False, "error": "Staff record not found"}), 404

        # Get today's attendance
        attendance = Attendance.query.filter_by(
            staff_id=staff.id,
            date=today
        ).first()

        if not attendance:
            return jsonify({"success": False, "error": "No attendance record found for today"}), 404

        # Update night shift
        attendance.night_shift = night_shift
        db.session.commit()

        return jsonify({
            "success": True,
            "data": attendance.to_dict(),
            "message": f"Night shift {'marked' if night_shift else 'unmarked'}"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# APPROVAL WORKFLOW ENDPOINTS
# ============================================

@attendance_bp.route('/approvals/pending', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_pending_approvals():
    """Get pending photo approvals (for HR/Managers)"""
    try:
        from attendance_management.services import ApprovalService

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        date_filter = request.args.get('date', None, type=str)

        result = ApprovalService.get_pending_approvals(
            date=datetime.strptime(date_filter, '%Y-%m-%d').date() if date_filter else None,
            limit=per_page,
            offset=(page - 1) * per_page
        )

        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/approvals/stats', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_approval_stats():
    """Get approval statistics (pending, approved, rejected, completed counts)"""
    try:
        from attendance_management.services import ApprovalService

        date_filter = request.args.get('date', None, type=str)

        result = ApprovalService.get_approval_stats(
            date=datetime.strptime(date_filter, '%Y-%m-%d').date() if date_filter else None
        )

        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/approvals/<int:photo_id>/approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def approve_photo(photo_id):
    """Approve a pending attendance photo"""
    try:
        from attendance_management.services import ApprovalService

        user_id = get_jwt_identity()
        data = request.get_json() or {}

        # Approver is the current user
        approver_id = user_id
        notes = data.get('notes', None)

        result = ApprovalService.approve_photo(
            photo_id=photo_id,
            approver_id=approver_id,
            notes=notes
        )

        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/approvals/<int:photo_id>/reject', methods=['POST'], strict_slashes=False)
@jwt_required()
def reject_photo(photo_id):
    """Reject a pending attendance photo"""
    try:
        from attendance_management.services import ApprovalService

        user_id = get_jwt_identity()
        data = request.get_json() or {}

        rejection_reason = data.get('rejection_reason', 'No reason provided')

        result = ApprovalService.reject_photo(
            photo_id=photo_id,
            approver_id=user_id,
            rejection_reason=rejection_reason
        )

        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/approvals/bulk-approve', methods=['POST'], strict_slashes=False)
@jwt_required()
def bulk_approve_photos():
    """Approve multiple photos at once"""
    try:
        from attendance_management.services import ApprovalService

        user_id = get_jwt_identity()
        data = request.get_json() or {}
        photo_ids = data.get('photo_ids', [])

        if not photo_ids:
            return jsonify({"success": False, "error": "No photo IDs provided"}), 400

        result = ApprovalService.bulk_approve(
            photo_ids=photo_ids,
            approver_id=user_id
        )

        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route('/approvals/bulk-reject', methods=['POST'], strict_slashes=False)
@jwt_required()
def bulk_reject_photos():
    """Reject multiple photos at once"""
    try:
        from attendance_management.services import ApprovalService

        user_id = get_jwt_identity()
        data = request.get_json() or {}
        photo_ids = data.get('photo_ids', [])
        reason = data.get('reason', 'Rejected')

        if not photo_ids:
            return jsonify({"success": False, "error": "No photo IDs provided"}), 400

        result = ApprovalService.bulk_reject(
            photo_ids=photo_ids,
            approver_id=user_id,
            reason=reason
        )

        return jsonify(result), 200 if result.get('success') else 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================
# MANUAL PUNCH IN/OUT ENDPOINTS
# ============================================

@attendance_bp.route('/manual-punch', methods=['POST'], strict_slashes=False)
@jwt_required()
def manual_punch_in():
    """Manually record punch in/out (for HR/Admin)"""
    try:
        Attendance = get_attendance_model()
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Required fields
        if 'staff_id' not in data or 'date' not in data:
            return jsonify({"success": False, "error": "staff_id and date are required"}), 400

        staff_id = int(data['staff_id'])
        date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()

        # Check if staff exists
        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({"success": False, "error": "Staff member not found"}), 404

        # Get or create attendance record
        attendance = Attendance.query.filter_by(
            staff_id=staff_id,
            date=date_obj
        ).first()

        if not attendance:
            attendance = Attendance(
                staff_id=staff_id,
                date=date_obj,
                punch_in_type='manual',
                present=True,
                half_day=False,
                night_shift=False,
                overtime_hours=0.0
            )
            db.session.add(attendance)

        # Update fields if provided
        if 'punch_in_time' in data:
            try:
                punch_in = datetime.fromisoformat(data['punch_in_time'].replace('Z', '+00:00'))
                attendance.punch_in_time = punch_in
            except:
                return jsonify({"success": False, "error": "Invalid punch_in_time format"}), 400

        if 'punch_out_time' in data:
            try:
                punch_out = datetime.fromisoformat(data['punch_out_time'].replace('Z', '+00:00'))
                attendance.punch_out_time = punch_out
            except:
                return jsonify({"success": False, "error": "Invalid punch_out_time format"}), 400

        if 'overtime_hours' in data:
            attendance.overtime_hours = float(data.get('overtime_hours', 0))

        if 'night_shift' in data:
            attendance.night_shift = bool(data.get('night_shift', False))

        if 'present' in data:
            attendance.present = bool(data.get('present', True))

        # Set approval status if saving without approval
        if data.get('save_and_approve', False):
            attendance.status = 'approved'
            attendance.approved_by = user_id
            attendance.approved_at = datetime.utcnow()
        else:
            attendance.status = 'pending'

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Manual punch recorded successfully",
            "data": attendance.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
