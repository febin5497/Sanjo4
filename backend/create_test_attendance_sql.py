#!/usr/bin/env python
"""
Create test attendance records using direct SQL
"""

import sqlite3
from datetime import datetime, timedelta
import os

# Find the database file
db_path = None
for root, dirs, files in os.walk(r'C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\backend'):
    if 'construction.db' in files or 'app.db' in files or 'test.db' in files:
        db_path = os.path.join(root, next((f for f in files if f.endswith('.db')), None))
        break

# Try common locations
possible_paths = [
    'construction_management/instance/construction.db',
    'construction_management/construction.db',
    'instance/construction.db',
    '../instance/construction.db',
]

for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("Database not found. Searching...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db'):
                db_path = os.path.join(root, file)
                print(f"Found database: {db_path}")
                break

if not db_path:
    print("ERROR: Could not find database file")
    exit(1)

print(f"Using database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing staff
    cursor.execute("SELECT id, name FROM staff LIMIT 10")
    staff_list = cursor.fetchall()

    if not staff_list:
        print("No staff found in database")
        conn.close()
        exit(1)

    print(f"Found {len(staff_list)} staff members")

    # Create attendance records
    base_date = datetime.now().date()
    records_created = 0

    for day_offset in range(10):
        current_date = base_date - timedelta(days=day_offset)

        for staff_id, staff_name in staff_list[:5]:
            if current_date.weekday() < 5:  # Only weekdays
                present = day_offset % 2 == 0
                night_shift = day_offset % 5 == 0
                overtime_hours = 2.0 if day_offset % 3 == 0 else 0.0
                leave_reason = None if present else ("Sick Leave" if day_offset % 2 == 0 else "Personal Leave")

                try:
                    cursor.execute("""
                        INSERT INTO attendance (staff_id, date, present, half_day, night_shift, overtime_hours, leave_reason)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (staff_id, current_date.isoformat(), present, False, night_shift, overtime_hours, leave_reason))
                    records_created += 1
                except sqlite3.IntegrityError as e:
                    # Record might already exist
                    pass

    conn.commit()
    print(f"✓ Created {records_created} test attendance records")

    # Display summary
    cursor.execute("SELECT staff_id, COUNT(*) as count FROM attendance GROUP BY staff_id LIMIT 5")
    for staff_id, count in cursor.fetchall():
        cursor.execute("SELECT name FROM staff WHERE id = ?", (staff_id,))
        name_result = cursor.fetchone()
        name = name_result[0] if name_result else "Unknown"
        print(f"  - {name}: {count} records")

    conn.close()
    print("✓ Database populated successfully")

except Exception as e:
    print(f"✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
