import os
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO


class PhotoValidator:
    """Validates attendance photos for security and quality requirements"""

    # Configuration constants
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MIN_WIDTH = 1280
    MIN_HEIGHT = 720
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png'}
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    TIMESTAMP_TOLERANCE_SECONDS = 300  # 5 minutes

    @staticmethod
    def validate_photo_file(file_obj, filename):
        """
        Validate photo file for security and quality.

        Args:
            file_obj: FileStorage object from Flask request
            filename: Original filename

        Returns:
            tuple: (is_valid, error_message, photo_data_dict)
        """
        # Check file extension
        _, ext = os.path.splitext(filename)
        if ext.lower() not in PhotoValidator.ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(PhotoValidator.ALLOWED_EXTENSIONS)}", None

        # Check file size
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        file_obj.seek(0)

        if file_size == 0:
            return False, "File is empty", None

        if file_size > PhotoValidator.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.1f}MB. Maximum: 5MB", None

        # Check MIME type
        mime_type = file_obj.content_type
        if mime_type not in PhotoValidator.ALLOWED_MIME_TYPES:
            return False, f"Invalid MIME type: {mime_type}", None

        # Validate image
        try:
            image = Image.open(file_obj)
            image.verify()

            # Re-open image after verify (verify closes file)
            file_obj.seek(0)
            image = Image.open(file_obj)

            width, height = image.size

            # Check resolution
            if width < PhotoValidator.MIN_WIDTH or height < PhotoValidator.MIN_HEIGHT:
                return False, f"Image resolution too low: {width}x{height}. Minimum: {PhotoValidator.MIN_WIDTH}x{PhotoValidator.MIN_HEIGHT}", None

            file_obj.seek(0)

            return True, None, {
                'width': width,
                'height': height,
                'size': file_size,
                'mime_type': mime_type,
            }

        except Exception as e:
            return False, f"Invalid image file: {str(e)}", None

    @staticmethod
    def validate_timestamp(timestamp_captured_str, max_tolerance_seconds=None):
        """
        Validate that captured timestamp is reasonable.

        Args:
            timestamp_captured_str: ISO 8601 timestamp string
            max_tolerance_seconds: Maximum seconds difference from now (default 5 minutes)

        Returns:
            tuple: (is_valid, error_message)
        """
        if max_tolerance_seconds is None:
            max_tolerance_seconds = PhotoValidator.TIMESTAMP_TOLERANCE_SECONDS

        try:
            timestamp_captured = datetime.fromisoformat(timestamp_captured_str.replace('Z', '+00:00'))
            now = datetime.utcnow() if timestamp_captured.tzinfo is None else datetime.now(timestamp_captured.tzinfo)

            # Allow some tolerance for timezone and processing delays
            time_diff = abs((now - timestamp_captured).total_seconds())

            if time_diff > max_tolerance_seconds:
                minutes = int(time_diff / 60)
                return False, f"Timestamp too old: {minutes} minutes ago. Maximum tolerance: {max_tolerance_seconds // 60} minutes"

            return True, None

        except ValueError as e:
            return False, f"Invalid timestamp format: {str(e)}"

    @staticmethod
    def validate_photo_quality(width, height, file_size):
        """
        Additional quality checks for approved photos.

        Returns:
            dict: Quality metrics and warnings
        """
        quality_report = {
            'resolution_ok': width >= PhotoValidator.MIN_WIDTH and height >= PhotoValidator.MIN_HEIGHT,
            'file_size_ok': file_size <= PhotoValidator.MAX_FILE_SIZE,
            'warnings': [],
            'score': 100,  # Quality score out of 100
        }

        # Resolution check
        if not quality_report['resolution_ok']:
            quality_report['warnings'].append(f"Low resolution: {width}x{height}")
            quality_report['score'] -= 30

        # File size check
        if file_size < 100 * 1024:  # Less than 100KB
            quality_report['warnings'].append("File size suspiciously small")
            quality_report['score'] -= 20

        # Aspect ratio check (too extreme might indicate cropping/manipulation)
        aspect_ratio = width / height if height > 0 else 0
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            quality_report['warnings'].append(f"Unusual aspect ratio: {aspect_ratio:.2f}")
            quality_report['score'] -= 10

        return quality_report


class TimestampValidator:
    """Validates timestamp consistency between capture and submission"""

    @staticmethod
    def validate_time_gap(timestamp_captured, timestamp_submitted, max_gap_seconds=30):
        """
        Validate that photo was submitted shortly after capture.

        Args:
            timestamp_captured: datetime when photo was captured
            timestamp_submitted: datetime when photo was submitted
            max_gap_seconds: Maximum allowed gap (default 30 seconds)

        Returns:
            tuple: (is_valid, error_message, gap_seconds)
        """
        time_gap = (timestamp_submitted - timestamp_captured).total_seconds()

        if time_gap < 0:
            return False, "Submission time cannot be before capture time", time_gap

        if time_gap > max_gap_seconds:
            return False, f"Photo took too long to submit: {int(time_gap)} seconds. Maximum: {max_gap_seconds} seconds", time_gap

        return True, None, time_gap

    @staticmethod
    def is_timestamp_reasonable(timestamp, tolerance_minutes=5):
        """
        Check if timestamp is within reasonable range (not too far in past or future).

        Args:
            timestamp: datetime to check
            tolerance_minutes: Allowed deviation from current time

        Returns:
            bool: True if timestamp is reasonable
        """
        now = datetime.utcnow() if timestamp.tzinfo is None else datetime.now(timestamp.tzinfo)
        time_diff = abs((now - timestamp).total_seconds())
        tolerance_seconds = tolerance_minutes * 60

        return time_diff <= tolerance_seconds
