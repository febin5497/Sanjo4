#!/usr/bin/env python
"""
Script to create test attendance records for testing the Attendance Report feature
"""

import sys
import os
from datetime import datetime, timedelta
import importlib.util

# Add construction_management directory to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
cm_dir = os.path.join(backend_dir, 'construction_management')
sys.path.insert(0, cm_dir)

from construction_management.app import create_app
from extensions import db
from staff_management.models import Staff

# Load Attendance model directly from the models.py file to avoid circular imports
attendance_models_path = os.path.join(cm_dir, 'attendance_management', 'models.py')
spec = importlib.util.spec_from_file_location('attendance_models_module', attendance_models_path)
attendance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attendance_module)
Attendance = attendance_module.Attendance

def create_test_attendance():
    """Create test attendance records"""
    app = create_app()

    with app.app_context():
        # Get all staff
        staff_list = Staff.query.all()
        if not staff_list:
            print("No staff found. Please create staff first.")
            return

        print(f"Found {len(staff_list)} staff members")

        # Create attendance records for the last 10 days
        base_date = datetime.now().date()
        attendance_records = []

        for day_offset in range(10):
            current_date = base_date - timedelta(days=day_offset)

            for staff in staff_list[:5]:  # Create records for first 5 staff
                # Skip weekends randomly
                if current_date.weekday() < 5:  # Only weekdays
                    present = day_offset % 2 == 0  # Alternate present/absent

                    attendance = Attendance(
                        staff_id=staff.id,
                        date=current_date,
                        present=present,
                        half_day=False,
                        night_shift=day_offset % 5 == 0,  # Every 5th day is night shift
                        overtime_hours=2.0 if day_offset % 3 == 0 else 0.0,  # Some days with overtime
                        leave_reason=None if present else "Sick Leave" if day_offset % 2 == 0 else "Personal Leave"
                    )
                    attendance_records.append(attendance)

        # Add all records to session and commit
        for record in attendance_records:
            db.session.add(record)

        try:
            db.session.commit()
            print(f"✓ Created {len(attendance_records)} test attendance records")

            # Display summary
            for staff in staff_list[:5]:
                count = Attendance.query.filter_by(staff_id=staff.id).count()
                print(f"  - {staff.name}: {count} records")

        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating records: {str(e)}")
            return False

    return True

if __name__ == '__main__':
    success = create_test_attendance()
    sys.exit(0 if success else 1)
