#!/usr/bin/env python
"""
Create test attendance records directly in the database
"""

import sqlite3
from datetime import datetime, timedelta
import os

# Use the database that has staff
db_path = r'C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\backend\data.db'

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

print(f"Using database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing staff
    cursor.execute("SELECT id, name FROM staff ORDER BY id LIMIT 10")
    staff_list = cursor.fetchall()

    if not staff_list:
        print("No staff found in database")
        conn.close()
        exit(1)

    print(f"Found {len(staff_list)} staff members")

    # Create attendance records
    base_date = datetime.now().date()
    records_created = 0
    records_skipped = 0

    for day_offset in range(10):
        current_date = base_date - timedelta(days=day_offset)

        for staff_id, staff_name in staff_list[:5]:
            if current_date.weekday() < 5:  # Only weekdays
                present = day_offset % 2 == 0
                night_shift = 1 if day_offset % 5 == 0 else 0
                overtime_hours = 2.0 if day_offset % 3 == 0 else 0.0
                leave_reason = None if present else ("Sick Leave" if day_offset % 2 == 0 else "Personal Leave")

                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO attendance (staff_id, date, present, half_day, night_shift, overtime_hours, leave_reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (staff_id, current_date.isoformat(), 1 if present else 0, 0, night_shift, overtime_hours, leave_reason))
                    records_created += 1
                except sqlite3.IntegrityError:
                    records_skipped += 1

    conn.commit()
    print(f"Created {records_created} test attendance records ({records_skipped} skipped as duplicates)")

    # Display summary
    cursor.execute("SELECT staff_id, COUNT(*) as count FROM attendance GROUP BY staff_id ORDER BY staff_id LIMIT 10")
    print("Attendance records per staff:")
    for staff_id, count in cursor.fetchall():
        cursor.execute("SELECT name FROM staff WHERE id = ?", (staff_id,))
        name_result = cursor.fetchone()
        name = name_result[0] if name_result else "Unknown"
        print(f"  {name}: {count} records")

    conn.close()
    print("Database populated successfully!")

except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
