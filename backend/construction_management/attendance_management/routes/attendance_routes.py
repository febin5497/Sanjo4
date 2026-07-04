from flask import Blueprint, request, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from extensions import db
from user_management.models import User
from staff_management.models import Staff
from attendance_management.services import PhotoService, ApprovalService
from attendance_management.utils import PhotoValidator, TimestampValidator

# Import Attendance models from canonical location
from attendance_management.models import Attendance, AttendanceRecord, AttendancePhoto

# Create blueprint
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/attendance')


# ============================================================================
# SITE STAFF ENDPOINTS - Photo Submission and Status
# ============================================================================

@attendance_bp.route('/punch-in-photo', methods=['POST'])
@jwt_required()
def punch_in_photo():
    """
    Upload punch-in photo from site staff.

    Required:
    - photo: File (JPEG/PNG only)
    - timestamp_captured: ISO 8601 datetime

    Returns:
    - photo_id, status, record_id
    """
    current_user_id = get_jwt_identity()

    try:
        # Get current user
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Get staff record for this user
        staff = Staff.query.filter_by(user_id=current_user_id).first()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff record not found'}), 404

        # Check if file is present
        if 'photo' not in request.files:
            return jsonify({'success': False, 'error': 'No photo provided'}), 400

        photo_file = request.files['photo']
        if not photo_file or photo_file.filename == '':
            return jsonify({'success': False, 'error': 'Invalid photo file'}), 400

        # Get timestamp
        timestamp_captured = request.form.get('timestamp_captured')
        if not timestamp_captured:
            return jsonify({'success': False, 'error': 'timestamp_captured is required'}), 400

        # Get location data (optional)
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        location_accuracy = request.form.get('location_accuracy')
        project_id = request.form.get('project_id')

        # Convert to float if provided
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
            location_accuracy = float(location_accuracy) if location_accuracy else None
            project_id = int(project_id) if project_id else None
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid location coordinates or project_id'}), 400

        # Save photo with location data and audit fields
        result = PhotoService.save_photo(
            photo_file, staff.id, timestamp_captured,
            latitude, longitude, location_accuracy,
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
            company_id=user.company_id
        )
        if not result['success']:
            return jsonify(result), 400

        # Create or update attendance record
        photo_data = result['photo_data']
        photo_id = result['photo_id']

        # Check if record exists for today
        today = datetime.utcnow().date()
        attendance_record = AttendanceRecord.query.filter_by(
            staff_id=staff.id,
            date=today,
        ).first()

        if not attendance_record:
            attendance_record = AttendanceRecord(
                staff_id=staff.id,
                punch_in_type='photo',
                punch_in_photo_id=photo_id,
                status='pending',
                date=today,
                project_id=project_id,
                created_by_id=current_user_id,
                updated_by_id=current_user_id,
                company_id=user.company_id,
            )
            db.session.add(attendance_record)
        else:
            attendance_record.punch_in_type = 'photo'
            attendance_record.punch_in_photo_id = photo_id
            attendance_record.status = 'pending'
            attendance_record.project_id = project_id
            attendance_record.updated_by_id = current_user_id

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Photo submitted for approval',
            'record_id': attendance_record.id,
            'photo_id': photo_id,
            'status': 'pending',
            'submitted_at': datetime.utcnow().isoformat() + 'Z',
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/today-status', methods=['GET'])
@jwt_required()
def get_today_status():
    """
    Get attendance status for today.

    Returns:
    - punch_in status, punch_out availability, messages
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        staff = Staff.query.filter_by(user_id=current_user_id).first()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff record not found'}), 404

        today = datetime.utcnow().date()
        attendance_record = AttendanceRecord.query.filter_by(
            staff_id=staff.id,
            date=today,
        ).first()

        # Prepare response
        status = {
            'punch_in': None,
            'punch_out_enabled': False,
            'message': 'No punch-in yet',
        }

        if attendance_record:
            # Get photo if exists
            photo = None
            if attendance_record.punch_in_photo_id:
                photo = AttendancePhoto.query.get(attendance_record.punch_in_photo_id)

            status['punch_in'] = {
                'status': attendance_record.status,
                'punch_in_time': attendance_record.punch_in_time.isoformat() if attendance_record.punch_in_time else None,
                'submitted_at': photo.timestamp_submitted.isoformat() if photo else None,
                'photo_id': attendance_record.punch_in_photo_id,
            }

            if attendance_record.status == 'approved':
                status['punch_out_enabled'] = True
                status['message'] = 'Ready to punch out'
            elif attendance_record.status == 'rejected' and photo:
                status['message'] = f'Photo rejected: {photo.rejection_reason}'
                status['can_retake'] = True
            elif attendance_record.status == 'pending':
                status['message'] = 'Waiting for office approval...'

        if attendance_record and attendance_record.punch_out_time:
            status['punch_out'] = {
                'punch_out_time': attendance_record.punch_out_time.isoformat(),
                'hours_worked': attendance_record._calculate_hours_worked(),
            }

        return jsonify({
            'success': True,
            'date': today.isoformat(),
            'staff_name': staff.name,
            **status,
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/punch-out', methods=['POST'])
@jwt_required()
def punch_out():
    """
    Record punch-out time (only after punch-in approval).
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        staff = Staff.query.filter_by(user_id=current_user_id).first()
        if not staff:
            return jsonify({'success': False, 'error': 'Staff record not found'}), 404

        today = datetime.utcnow().date()
        attendance_record = AttendanceRecord.query.filter_by(
            staff_id=staff.id,
            date=today,
        ).first()

        if not attendance_record:
            return jsonify({'success': False, 'error': 'No punch-in found for today'}), 404

        if attendance_record.status != 'approved':
            return jsonify({'success': False, 'error': 'Punch-in must be approved before punch-out'}), 400

        if attendance_record.punch_out_time:
            return jsonify({'success': False, 'error': 'Already punched out today'}), 400

        # Record punch-out
        attendance_record.punch_out_time = datetime.utcnow()
        attendance_record.status = 'completed'
        db.session.commit()

        # Calculate hours
        if attendance_record.punch_in_time:
            hours_worked = (attendance_record.punch_out_time - attendance_record.punch_in_time).total_seconds() / 3600
            hours_str = f"{int(hours_worked)}h {int((hours_worked % 1) * 60)}m"
        else:
            hours_str = "N/A"

        return jsonify({
            'success': True,
            'punch_out_time': attendance_record.punch_out_time.isoformat() + 'Z',
            'hours_worked': hours_str,
            'message': f'Punch-out recorded. Hours worked: {hours_str}',
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# OFFICE STAFF ENDPOINTS - Approval Workflow
# ============================================================================

@attendance_bp.route('/approvals/pending', methods=['GET'])
@jwt_required()
def get_pending_approvals():
    """
    Get pending photo approvals for office staff.

    Query params:
    - date: Optional date filter (YYYY-MM-DD)
    - limit: Results per page (default 20)
    - offset: Pagination offset (default 0)
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Check permissions: User.role OR Staff.role
        allowed_user_roles = ['admin', 'super_admin']
        allowed_staff_roles = ['hr manager', 'admin', 'site manager']
        
        has_access = False
        if user.role and user.role.lower() in allowed_user_roles:
            has_access = True
        else:
            staff = Staff.query.filter_by(user_id=current_user_id).first()
            if staff and staff.role and staff.role.lower() in allowed_staff_roles:
                has_access = True
        
        if not has_access:
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        # Get pagination params
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        date_str = request.args.get('date')

        date_filter = None
        if date_str:
            try:
                date_filter = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        result = ApprovalService.get_pending_approvals(date=date_filter, limit=limit, offset=offset)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/approvals/stats', methods=['GET'])
@jwt_required()
def get_approval_stats():
    """
    Get approval statistics for dashboard.

    Query params:
    - date: Optional date filter (YYYY-MM-DD)

    Returns:
    - pending, approved, rejected, total counts
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Check permissions: User.role OR Staff.role
        allowed_user_roles = ['admin', 'super_admin']
        allowed_staff_roles = ['hr manager', 'admin', 'site manager']
        
        has_access = False
        if user.role and user.role.lower() in allowed_user_roles:
            has_access = True
        else:
            staff = Staff.query.filter_by(user_id=current_user_id).first()
            if staff and staff.role and staff.role.lower() in allowed_staff_roles:
                has_access = True
        
        if not has_access:
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        date_str = request.args.get('date')
        date_filter = None
        if date_str:
            try:
                date_filter = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        result = ApprovalService.get_approval_stats(date=date_filter)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/stats/<int:staff_id>', methods=['GET'])
@jwt_required()
def get_staff_attendance_stats(staff_id):
    """
    Get attendance statistics for a specific staff member.

    Query params:
    - start_date: Start date (YYYY-MM-DD, optional - defaults to 30 days ago)
    - end_date: End date (YYYY-MM-DD, optional - defaults to today)

    Returns:
    - present_days, absent_days, half_days, night_shifts, total_overtime_hours, attendance_percentage
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Get start and end dates
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not start_date_str:
            start_date = datetime.now().date() - timedelta(days=30)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        if not end_date_str:
            end_date = datetime.now().date()
        else:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Get attendance records for this staff member in the date range
        records = Attendance.query.filter(
            Attendance.staff_id == staff_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date,
        ).all()

        # Calculate statistics
        total_days = len(records)
        present_days = sum(1 for r in records if r.present and not r.half_day and not r.night_shift)
        absent_days = sum(1 for r in records if not r.present)
        half_days = sum(1 for r in records if r.half_day)
        night_shifts = sum(1 for r in records if r.night_shift)
        total_overtime_hours = sum(r.overtime_hours or 0 for r in records)

        # Calculate attendance percentage
        if total_days > 0:
            attendance_percentage = round((present_days / total_days) * 100, 2)
        else:
            attendance_percentage = 0

        return jsonify({
            'success': True,
            'data': {
                'staff_id': staff_id,
                'period': f'{start_date} to {end_date}',
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'half_days': half_days,
                'night_shifts': night_shifts,
                'total_overtime_hours': total_overtime_hours,
                'attendance_percentage': attendance_percentage,
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/approvals/<int:photo_id>/approve', methods=['POST'])
@jwt_required()
def approve_photo(photo_id):
    """
    Approve a pending photo.

    Body:
    - notes: Optional approval notes
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Check permissions: User.role OR Staff.role
        allowed_user_roles = ['admin', 'super_admin']
        allowed_staff_roles = ['hr manager', 'admin', 'site manager']
        
        has_access = False
        staff = None
        if user.role and user.role.lower() in allowed_user_roles:
            has_access = True
            staff = Staff.query.filter_by(user_id=current_user_id).first()
        else:
            staff = Staff.query.filter_by(user_id=current_user_id).first()
            if staff and staff.role and staff.role.lower() in allowed_staff_roles:
                has_access = True
        
        if not has_access:
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        # Check photo belongs to same company
        photo = AttendancePhoto.query.get(photo_id)
        if not photo:
            return jsonify({'success': False, 'error': 'Photo not found'}), 404

        notes = request.json.get('notes') if request.json else None

        # Use staff.id if available, otherwise None (for admin users without Staff record)
        approver_id = staff.id if staff else None

        result = ApprovalService.approve_photo(photo_id, approver_id, notes)
        status_code = 200 if result['success'] else 400

        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/approvals/<int:photo_id>/reject', methods=['POST'])
@jwt_required()
def reject_photo(photo_id):
    """
    Reject a pending photo.

    Body:
    - rejection_reason: Reason for rejection (required)
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Check permissions: User.role OR Staff.role
        allowed_user_roles = ['admin', 'super_admin']
        allowed_staff_roles = ['hr manager', 'admin', 'site manager']
        
        has_access = False
        staff = None
        if user.role and user.role.lower() in allowed_user_roles:
            has_access = True
            staff = Staff.query.filter_by(user_id=current_user_id).first()
        else:
            staff = Staff.query.filter_by(user_id=current_user_id).first()
            if staff and staff.role and staff.role.lower() in allowed_staff_roles:
                has_access = True
        
        if not has_access:
            return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

        photo = AttendancePhoto.query.get(photo_id)
        if not photo:
            return jsonify({'success': False, 'error': 'Photo not found'}), 404

        data = request.get_json()
        rejection_reason = data.get('rejection_reason') if data else None

        if not rejection_reason:
            return jsonify({'success': False, 'error': 'rejection_reason is required'}), 400

        # Use staff.id if available, otherwise None (for admin users without Staff record)
        approver_id = staff.id if staff else None

        result = ApprovalService.reject_photo(photo_id, approver_id, rejection_reason)
        status_code = 200 if result['success'] else 400

        return jsonify(result), status_code

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/photos/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    """
    Retrieve photo file (accepts JWT via header or ?token= query param for <img> tags).
    """
    try:
        from flask_jwt_extended import verify_jwt_in_request, decode_token
        token = request.args.get('token', '')
        if token:
            try:
                decode_token(token)
            except Exception:
                return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        else:
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({'success': False, 'error': 'Authorization required'}), 401

        file_path, photo = PhotoService.get_photo_file(photo_id)

        if not photo:
            return jsonify({'success': False, 'error': 'Photo not found'}), 404

        if not file_path:
            return jsonify({'success': False, 'error': 'Photo file not found'}), 404

        return send_file(file_path, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# OFFICE STAFF ENDPOINTS - Manual Punch & Reports
# ============================================================================

@attendance_bp.route('/manual-punch', methods=['POST'])
@jwt_required()
def manual_punch():
    """
    Manual punch-in/out by office staff.

    Body:
    - staff_id: Target staff ID (required)
    - punch_type: 'in' or 'out' (required)
    - timestamp: ISO 8601 timestamp (optional, defaults to now)
    - notes: Reason for manual punch (optional)
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        approver = Staff.query.filter_by(user_id=current_user_id).first()
        allowed_user_roles = ['admin', 'super_admin']
        allowed_staff_roles = ['hr manager', 'admin']
        
        has_access = False
        if user.role and user.role.lower() in allowed_user_roles:
            has_access = True
        elif approver and approver.role and approver.role.lower() in allowed_staff_roles:
            has_access = True
        
        if not has_access:
            return jsonify({'success': False, 'error': 'Only HR/Admin can perform manual punches'}), 403

        data = request.get_json()
        staff_id = data.get('staff_id')
        punch_type = data.get('punch_type')
        timestamp_str = data.get('timestamp')
        notes = data.get('notes')

        if not staff_id or not punch_type:
            return jsonify({'success': False, 'error': 'staff_id and punch_type are required'}), 400

        if punch_type not in ['in', 'out']:
            return jsonify({'success': False, 'error': 'punch_type must be "in" or "out"'}), 400

        # Parse timestamp
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                if timestamp.tzinfo:
                    timestamp = timestamp.replace(tzinfo=None)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid timestamp format'}), 400
        else:
            timestamp = datetime.utcnow()

        staff = Staff.query.get(staff_id)
        if not staff:
            return jsonify({'success': False, 'error': 'Staff not found'}), 404

        date = timestamp.date()
        attendance_record = AttendanceRecord.query.filter_by(
            staff_id=staff_id,
            date=date,
        ).first()

        if not attendance_record:
            if punch_type == 'out':
                return jsonify({'success': False, 'error': 'Cannot punch out without punch in'}), 400

            attendance_record = AttendanceRecord(
                staff_id=staff_id,
                punch_in_time=timestamp,
                punch_in_type='button',
                status='approved',
                date=date,
            )
            db.session.add(attendance_record)
        else:
            if punch_type == 'in':
                if attendance_record.punch_in_time:
                    return jsonify({'success': False, 'error': 'Already punched in'}), 400
                attendance_record.punch_in_time = timestamp
                attendance_record.punch_in_type = 'button'
                attendance_record.status = 'approved'
            else:  # punch_type == 'out'
                if attendance_record.punch_out_time:
                    return jsonify({'success': False, 'error': 'Already punched out'}), 400
                attendance_record.punch_out_time = timestamp
                attendance_record.status = 'completed'

        db.session.commit()

        return jsonify({
            'success': True,
            'staff_name': staff.name,
            'punch_type': punch_type,
            'timestamp': timestamp.isoformat() + 'Z',
            'message': f'Manual punch {punch_type} recorded for {staff.name}',
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('/report', methods=['GET'])
@jwt_required()
def get_report():
    """
    Get attendance report.

    Query params:
    - start_date: Start date (YYYY-MM-DD, required)
    - end_date: End date (YYYY-MM-DD, required)
    - staff_id: Optional specific staff ID
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        staff_id = request.args.get('staff_id')

        if not start_date_str or not end_date_str:
            return jsonify({'success': False, 'error': 'start_date and end_date are required'}), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Query attendance records
        query = AttendanceRecord.query.filter(
            AttendanceRecord.date >= start_date,
            AttendanceRecord.date <= end_date,
        )

        if staff_id:
            query = query.filter_by(staff_id=staff_id)

        records = query.all()

        # Group by staff
        staff_records = {}
        for record in records:
            if record.staff_id not in staff_records:
                staff_records[record.staff_id] = {
                    'staff_id': record.staff_id,
                    'staff_name': record.staff.name if record.staff else None,
                    'staff_role': record.staff.role if record.staff else None,
                    'total_days': 0,
                    'present_days': 0,
                    'absent_days': 0,
                    'total_hours': 0,
                    'records': [],
                }

            staff_records[record.staff_id]['total_days'] += 1

            if record.status == 'completed':
                staff_records[record.staff_id]['present_days'] += 1
                if record.punch_in_time and record.punch_out_time:
                    hours = (record.punch_out_time - record.punch_in_time).total_seconds() / 3600
                    staff_records[record.staff_id]['total_hours'] += hours
            else:
                staff_records[record.staff_id]['absent_days'] += 1

            staff_records[record.staff_id]['records'].append({
                'date': record.date.isoformat(),
                'punch_in': record.punch_in_time.strftime('%H:%M') if record.punch_in_time else None,
                'punch_out': record.punch_out_time.strftime('%H:%M') if record.punch_out_time else None,
                'hours': (record.punch_out_time - record.punch_in_time).total_seconds() / 3600 if (record.punch_in_time and record.punch_out_time) else 0,
                'status': record.status,
            })

        return jsonify({
            'success': True,
            'period': f'{start_date_str} to {end_date_str}',
            'staff_count': len(staff_records),
            'data': list(staff_records.values()),
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@attendance_bp.route('', methods=['GET'])
@jwt_required()
def get_attendance_records():
    """
    Get attendance records with filtering and pagination.

    Query params:
    - start_date: Start date (YYYY-MM-DD, required)
    - end_date: End date (YYYY-MM-DD, required)
    - staff_id: Optional staff ID
    - department: Optional department/role
    - page: Page number (default 1)
    - per_page: Records per page (default 20)
    - company_id: Optional company ID
    """
    current_user_id = get_jwt_identity()

    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        staff_id = request.args.get('staff_id', type=int)
        department = request.args.get('department')
        company_id = request.args.get('company_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # REFACTORING FIX: Use defaults if dates not provided (last 30 days)
        if not start_date_str:
            start_date = datetime.now().date() - timedelta(days=30)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        if not end_date_str:
            end_date = datetime.now().date()
        else:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Build query
        query = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date,
        )

        # Apply filters
        if company_id:
            query = query.join(Staff).filter(Staff.company_id == company_id)

        if staff_id:
            query = query.filter(Attendance.staff_id == staff_id)

        if department:
            query = query.join(Staff).filter(Staff.role == department)

        # Get total count before pagination
        total_records = query.count()

        # Apply pagination
        records = query.order_by(Attendance.date.desc(), Attendance.staff_id).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Format response
        data = []
        for record in records.items:
            staff = Staff.query.get(record.staff_id)
            data.append({
                'id': record.id,
                'staff_id': record.staff_id,
                'staff_name': staff.name if staff else 'Unknown',
                'date': record.date.isoformat(),
                'present': record.present,
                'half_day': record.half_day,
                'night_shift': record.night_shift,
                'overtime_hours': record.overtime_hours,
                'leave_reason': record.leave_reason,
                'punch_in_time': record.punch_in_time.isoformat() if record.punch_in_time else None,
                'punch_out_time': record.punch_out_time.isoformat() if record.punch_out_time else None,
            })

        return jsonify({
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_records,
                'pages': records.pages,
            }
        }), 200

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return jsonify({'success': False, 'error': str(e), 'traceback': tb}), 500


@attendance_bp.route('/export', methods=['GET'])
@jwt_required()
def export_attendance():
    """
    Export attendance records to CSV or PDF format.

    Query Parameters:
    - format: 'csv' or 'pdf' (default: 'csv')
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    - staff_id: Optional staff ID to filter
    - department: Optional department to filter

    Returns:
    - File download
    """
    try:
        # Get parameters
        export_format = request.args.get('format', 'csv').lower()
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        staff_id = request.args.get('staff_id', type=int)
        department = request.args.get('department')
        company_id = request.args.get('company_id', type=int)

        # Validate format
        if export_format not in ['csv', 'pdf']:
            return jsonify({'success': False, 'error': 'Invalid format. Use csv or pdf'}), 400

        # Parse dates
        if not start_date_str or not end_date_str:
            return jsonify({'success': False, 'error': 'start_date and end_date are required'}), 400

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Build query
        query = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date,
        )

        if company_id:
            query = query.join(Staff).filter(Staff.company_id == company_id)

        if staff_id:
            query = query.filter(Attendance.staff_id == staff_id)

        if department:
            query = query.join(Staff).filter(Staff.role == department)

        records = query.order_by(Attendance.date.desc(), Attendance.staff_id).all()

        if not records:
            return jsonify({'success': False, 'error': 'No records found for the given criteria'}), 404

        # Generate export
        if export_format == 'csv':
            from attendance_management.services.export_service import ExportService
            csv_content = ExportService.generate_csv(records)
            filename = f'attendance_report_{start_date_str}_to_{end_date_str}.csv'

            from io import BytesIO
            return send_file(
                BytesIO(csv_content.encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )

        elif export_format == 'pdf':
            from attendance_management.services.export_service import ExportService
            pdf_content = ExportService.generate_pdf(records, start_date_str, end_date_str)
            filename = f'attendance_report_{start_date_str}_to_{end_date_str}.pdf'

            from io import BytesIO
            return send_file(
                BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Export failed: {str(e)}'
        }), 500
