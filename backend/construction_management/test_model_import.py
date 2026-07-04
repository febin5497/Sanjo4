import sys
import os
os.chdir(r'C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\backend\construction_management')
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("Testing attendance_management.models import")
print("=" * 60)

try:
    print("\n1. Importing extensions.db...")
    from extensions import db
    print("   OK - db imported successfully")
    
    print("\n2. Importing attendance_record...")
    from attendance_management.models.attendance_record import AttendanceRecord
    print("   OK - AttendanceRecord imported")
    
    print("\n3. Importing attendance_photo...")
    from attendance_management.models.attendance_photo import AttendancePhoto
    print("   OK - AttendancePhoto imported")
    
    print("\n4. Importing full attendance_management.models package...")
    from attendance_management.models import AttendanceRecord, AttendancePhoto, Attendance
    print("   OK - All imported successfully")
    print(f"   - AttendanceRecord: {AttendanceRecord}")
    print(f"   - AttendancePhoto: {AttendancePhoto}")
    print(f"   - Attendance: {Attendance}")
    
except Exception as e:
    import traceback
    print(f"\n   ERROR: {str(e)}")
    traceback.print_exc()

print("\n" + "=" * 60)
