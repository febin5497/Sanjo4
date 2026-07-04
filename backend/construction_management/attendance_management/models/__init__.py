# Unified Attendance Models
# The Attendance model now handles both simple daily tracking and photo-based approval workflows

from .attendance import Attendance
from .attendance_photo import AttendancePhoto

# Legacy compatibility: AttendanceRecord is now just Attendance
AttendanceRecord = Attendance

__all__ = ['Attendance', 'AttendancePhoto', 'AttendanceRecord']
