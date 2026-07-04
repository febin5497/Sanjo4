from datetime import datetime
from extensions import db
from attendance_management.models import AttendancePhoto, Attendance, AttendanceRecord


def _create_notification(user_id, company_id, title, message, notification_type, related_model=None, related_id=None):
    """Helper to create in-app notification"""
    try:
        from notifications.models import Notification
        notification = Notification(
            user_id=user_id,
            company_id=company_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_model=related_model,
            related_id=related_id
        )
        db.session.add(notification)
    except Exception as e:
        print(f"Warning: Could not create notification: {str(e)}")


class ApprovalService:
    """Service for managing attendance photo approval workflow"""

    @staticmethod
    def approve_photo(photo_id, approved_by_staff_id, notes=None):
        """
        Approve a photo and create/update attendance record.

        Args:
            photo_id: ID of photo to approve
            approved_by_staff_id: ID of staff member approving
            notes: Optional approval notes

        Returns:
            dict: Success status and attendance record
        """
        try:
            photo = AttendancePhoto.query.get(photo_id)
            if not photo:
                return {'success': False, 'error': 'Photo not found'}

            if photo.approval_status != 'pending':
                return {'success': False, 'error': f'Photo already {photo.approval_status}'}

            # Update photo record
            photo.approval_status = 'approved'
            photo.approved_by = approved_by_staff_id
            photo.approved_at = datetime.utcnow()

            # Check if attendance record exists for this date
            attendance_record = Attendance.query.filter_by(
                staff_id=photo.staff_id,
                date=photo.timestamp_captured.date(),
            ).first()

            if not attendance_record:
                # Create new attendance record with location data
                attendance_record = AttendanceRecord(
                    staff_id=photo.staff_id,
                    punch_in_time=photo.timestamp_captured,
                    punch_in_type='photo',
                    punch_in_photo_id=photo_id,
                    latitude=photo.latitude,
                    longitude=photo.longitude,
                    location_accuracy=photo.location_accuracy,
                    status='approved',
                    date=photo.timestamp_captured.date(),
                )
                db.session.add(attendance_record)
            else:
                # Update existing record with location data
                attendance_record.punch_in_time = photo.timestamp_captured
                attendance_record.punch_in_type = 'photo'
                attendance_record.punch_in_photo_id = photo_id
                attendance_record.latitude = photo.latitude
                attendance_record.longitude = photo.longitude
                attendance_record.location_accuracy = photo.location_accuracy
                attendance_record.status = 'approved'

            db.session.commit()

            # Create notification for the staff member
            try:
                from notifications.models import Notification
                from user_management.models import User
                staff_user = User.query.filter_by(id=photo.staff.user_id).first() if photo.staff else None
                if staff_user:
                    notif = Notification(
                        user_id=staff_user.id,
                        company_id=staff_user.company_id,
                        title='Attendance Approved',
                        message=f'Your attendance for {photo.timestamp_captured.date().isoformat()} has been approved.',
                        notification_type='attendance',
                        related_model='attendance',
                        related_id=attendance_record.id
                    )
                    db.session.add(notif)
                    db.session.commit()
                    print(f"[NOTIFICATION] Attendance approval notification sent to user #{staff_user.id}")
            except Exception as e:
                print(f"[NOTIFICATION ERROR] Could not send attendance approval notification: {str(e)}")
                db.session.rollback()

            return {
                'success': True,
                'message': 'Photo approved',
                'attendance_record_id': attendance_record.id,
                'staff_name': photo.staff.name if photo.staff else None,
                'punch_in_time': attendance_record.punch_in_time.isoformat(),
            }

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to approve photo: {str(e)}'}

    @staticmethod
    def reject_photo(photo_id, approved_by_staff_id, rejection_reason):
        """
        Reject a photo and notify staff member.

        Args:
            photo_id: ID of photo to reject
            approved_by_staff_id: ID of staff member rejecting
            rejection_reason: Reason for rejection

        Returns:
            dict: Success status
        """
        try:
            photo = AttendancePhoto.query.get(photo_id)
            if not photo:
                return {'success': False, 'error': 'Photo not found'}

            if photo.approval_status != 'pending':
                return {'success': False, 'error': f'Photo already {photo.approval_status}'}

            # Update photo record
            photo.approval_status = 'rejected'
            photo.rejected_by = approved_by_staff_id
            photo.rejected_at = datetime.utcnow()
            photo.rejection_reason = rejection_reason

            # If attendance record exists, mark as rejected
            attendance_record = Attendance.query.filter_by(
                punch_in_photo_id=photo_id
            ).first()

            if attendance_record:
                attendance_record.status = 'rejected'

            db.session.commit()

            # Create notification for the staff member
            try:
                from notifications.models import Notification
                from user_management.models import User
                staff_user = User.query.filter_by(id=photo.staff.user_id).first() if photo.staff else None
                if staff_user:
                    notif = Notification(
                        user_id=staff_user.id,
                        company_id=staff_user.company_id,
                        title='Attendance Rejected',
                        message=f'Your attendance for {photo.timestamp_captured.date().isoformat()} was rejected. Reason: {rejection_reason}',
                        notification_type='attendance',
                        related_model='attendance',
                        related_id=photo_id
                    )
                    db.session.add(notif)
                    db.session.commit()
                    print(f"[NOTIFICATION] Attendance rejection notification sent to user #{staff_user.id}")
            except Exception as e:
                print(f"[NOTIFICATION ERROR] Could not send attendance rejection notification: {str(e)}")
                db.session.rollback()

            return {
                'success': True,
                'message': 'Photo rejected - staff member notified',
                'staff_name': photo.staff.name if photo.staff else None,
                'rejection_reason': rejection_reason,
            }

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to reject photo: {str(e)}'}

    @staticmethod
    def get_pending_approvals(date=None, limit=20, offset=0):
        """
        Get list of pending photo approvals.

        Args:
            date: Optional specific date to filter
            limit: Number of results
            offset: Pagination offset

        Returns:
            dict: Pending photos and metadata
        """
        try:
            query = AttendancePhoto.query.filter_by(
                approval_status='pending'
            )

            if date:
                query = query.filter(AttendancePhoto.timestamp_captured >= date).filter(
                    AttendancePhoto.timestamp_captured < date + timedelta(days=1)
                )

            total = query.count()
            pending_photos = query.order_by(
                AttendancePhoto.timestamp_submitted.asc()
            ).limit(limit).offset(offset).all()

            # Add time pending calculation
            now = datetime.utcnow()
            photos_data = []
            for photo in pending_photos:
                photo_dict = photo.to_dict()
                time_pending = (now - photo.timestamp_submitted).total_seconds()
                photo_dict['time_pending_seconds'] = int(time_pending)
                photos_data.append(photo_dict)

            return {
                'success': True,
                'total': total,
                'limit': limit,
                'offset': offset,
                'pending': photos_data,
            }

        except Exception as e:
            return {'success': False, 'error': f'Failed to fetch pending approvals: {str(e)}'}

    @staticmethod
    def get_approval_stats(date=None):
        """
        Get approval statistics for dashboard.

        Args:
            date: Optional specific date

        Returns:
            dict: Statistics
        """
        try:
            from datetime import timedelta

            if not date:
                date = datetime.utcnow().date()

            # Count by approval status for the date
            query_base = AttendancePhoto.query.filter(
                AttendancePhoto.timestamp_submitted >= date
            ).filter(
                AttendancePhoto.timestamp_submitted < date + timedelta(days=1)
            )

            pending_count = query_base.filter_by(approval_status='pending').count()
            approved_count = query_base.filter_by(approval_status='approved').count()
            rejected_count = query_base.filter_by(approval_status='rejected').count()

            return {
                'success': True,
                'date': date.isoformat(),
                'pending': pending_count,
                'approved': approved_count,
                'rejected': rejected_count,
                'total': pending_count + approved_count + rejected_count,
            }

        except Exception as e:
            return {'success': False, 'error': f'Failed to fetch stats: {str(e)}'}


from datetime import timedelta
