import os
import shutil
from datetime import datetime
from pathlib import Path
from extensions import db
from attendance_management.models import AttendancePhoto
from attendance_management.utils import PhotoValidator


class PhotoService:
    """Service for handling attendance photo storage and retrieval"""

    # Base upload directory
    UPLOAD_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'attendance')

    @staticmethod
    def get_photo_path(staff_id, capture_date, filename_prefix=''):
        """
        Generate organized photo path: /uploads/attendance/YYYY/MM/DD/

        Args:
            staff_id: ID of staff member
            capture_date: datetime object of capture
            filename_prefix: Optional prefix for filename

        Returns:
            tuple: (relative_path, full_path)
        """
        # Create directory structure: YYYY/MM/DD
        year = capture_date.strftime('%Y')
        month = capture_date.strftime('%m')
        day = capture_date.strftime('%d')

        relative_dir = f'{year}/{month}/{day}'
        full_dir = os.path.join(PhotoService.UPLOAD_BASE_PATH, relative_dir)

        # Create directories if they don't exist
        os.makedirs(full_dir, exist_ok=True)

        # Generate filename: {staff_id}_{timestamp}_{prefix}.jpg
        timestamp = capture_date.strftime('%Y%m%d_%H%M%S')
        filename = f'{staff_id}_{timestamp}.jpg'

        relative_path = f'{relative_dir}/{filename}'
        full_path = os.path.join(full_dir, filename)

        return relative_path, full_path

    @staticmethod
    def save_photo(file_obj, staff_id, timestamp_captured, latitude=None, longitude=None, location_accuracy=None,
                   created_by_id=None, updated_by_id=None, company_id=None):
        """
        Save photo file to disk and create database record.

        Args:
            file_obj: Flask FileStorage object
            staff_id: ID of staff member
            timestamp_captured: ISO 8601 datetime of capture
            latitude: Optional GPS latitude
            longitude: Optional GPS longitude
            location_accuracy: Optional location accuracy in meters
            created_by_id: Optional user ID who created the record
            updated_by_id: Optional user ID who last updated the record
            company_id: Optional company ID for multi-tenancy

        Returns:
            dict: Photo record data or error dict
        """
        # Validate photo
        is_valid, error_msg, photo_data = PhotoValidator.validate_photo_file(file_obj, file_obj.filename)
        if not is_valid:
            return {'success': False, 'error': error_msg}

        # Validate timestamp
        ts_valid, ts_error = PhotoValidator.validate_timestamp(timestamp_captured)
        if not ts_valid:
            return {'success': False, 'error': ts_error}

        try:
            # Parse timestamp
            timestamp_captured_dt = datetime.fromisoformat(timestamp_captured.replace('Z', '+00:00'))
            if timestamp_captured_dt.tzinfo:
                timestamp_captured_dt = timestamp_captured_dt.replace(tzinfo=None)

            # Get photo path
            relative_path, full_path = PhotoService.get_photo_path(staff_id, timestamp_captured_dt)

            # Save file to disk
            file_obj.seek(0)
            file_obj.save(full_path)

            # Create database record
            photo = AttendancePhoto(
                staff_id=staff_id,
                photo_path=relative_path,
                photo_size=photo_data['size'],
                photo_width=photo_data['width'],
                photo_height=photo_data['height'],
                latitude=latitude,
                longitude=longitude,
                location_accuracy=location_accuracy,
                timestamp_captured=timestamp_captured_dt,
                timestamp_submitted=datetime.utcnow(),
                approval_status='pending',
                created_by_id=created_by_id,
                updated_by_id=updated_by_id,
                company_id=company_id,
            )

            db.session.add(photo)
            db.session.commit()

            return {
                'success': True,
                'photo_id': photo.id,
                'photo_data': photo.to_dict(),
            }

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to save photo: {str(e)}'}

    @staticmethod
    def get_photo_file(photo_id):
        """
        Retrieve photo file from disk.

        Args:
            photo_id: ID of attendance photo record

        Returns:
            tuple: (file_path, photo_record) or (None, None) if not found
        """
        photo = AttendancePhoto.query.get(photo_id)
        if not photo:
            return None, None

        full_path = os.path.join(PhotoService.UPLOAD_BASE_PATH, photo.photo_path)

        if not os.path.exists(full_path):
            return None, photo

        return full_path, photo

    @staticmethod
    def delete_photo(photo_id):
        """
        Delete photo file and database record.

        Args:
            photo_id: ID of attendance photo record

        Returns:
            dict: Success/error message
        """
        try:
            photo = AttendancePhoto.query.get(photo_id)
            if not photo:
                return {'success': False, 'error': 'Photo not found'}

            # Delete file from disk
            full_path = os.path.join(PhotoService.UPLOAD_BASE_PATH, photo.photo_path)
            if os.path.exists(full_path):
                os.remove(full_path)

            # Delete database record
            db.session.delete(photo)
            db.session.commit()

            return {'success': True, 'message': 'Photo deleted'}

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Failed to delete photo: {str(e)}'}

    @staticmethod
    def cleanup_old_photos(days_old=90, dry_run=False):
        """
        Delete photos older than specified days (data retention policy).

        Args:
            days_old: Number of days to keep (default 90)
            dry_run: If True, don't actually delete, just report

        Returns:
            dict: Statistics of cleanup operation
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        old_photos = AttendancePhoto.query.filter(
            AttendancePhoto.created_at < cutoff_date
        ).all()

        stats = {
            'total_found': len(old_photos),
            'deleted': 0,
            'failed': 0,
            'errors': [],
        }

        for photo in old_photos:
            try:
                full_path = os.path.join(PhotoService.UPLOAD_BASE_PATH, photo.photo_path)
                if not dry_run:
                    if os.path.exists(full_path):
                        os.remove(full_path)
                    db.session.delete(photo)
                stats['deleted'] += 1
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f"Failed to delete photo {photo.id}: {str(e)}")

        if not dry_run:
            db.session.commit()

        return stats
