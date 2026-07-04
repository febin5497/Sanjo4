import sys
import os
os.chdir(r'C:\Users\roms0\OneDrive\Documents\construction_management_app\construction_management_app\backend\construction_management')
sys.path.insert(0, os.getcwd())

from app import create_app
from extensions import db
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    try:
        from attendance_management.models import Attendance
        from staff_management.models import Staff
        
        # Try to query attendance
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
        
        query = Attendance.query.filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date,
        )
        
        total = query.count()
        print(f"Successfully queried {total} attendance records")
        
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        traceback.print_exc()
