"""
Database Seeding Script
Populates Staff and Attendance tables with realistic sample data
"""

from datetime import datetime, timedelta
from extensions import db
from staff_management.models import Staff
from attendance_management.models import Attendance
from app import create_app

def seed_database():
    """Populate database with sample data"""

    app = create_app()

    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🗑️  Clearing existing data...")
        Attendance.query.delete()
        Staff.query.delete()
        db.session.commit()

        # ============================================
        # SEED STAFF DATA
        # ============================================
        print("\n📝 Creating Staff records...")

        staff_data = [
            {
                "name": "Rajesh Kumar",
                "role": "Site Engineer",
                "phone": "9876543210",
                "email": "rajesh.kumar@construction.com",
                "joining_date": datetime(2022, 1, 15).date(),
                "salary": 65000,
                "pf": 12,
                "esi": 0.75
            },
            {
                "name": "Priya Sharma",
                "role": "Project Manager",
                "phone": "9876543211",
                "email": "priya.sharma@construction.com",
                "joining_date": datetime(2021, 6, 1).date(),
                "salary": 75000,
                "pf": 12,
                "esi": 0.75
            },
            {
                "name": "Amit Patel",
                "role": "Foreman",
                "phone": "9876543212",
                "email": "amit.patel@construction.com",
                "joining_date": datetime(2020, 3, 10).date(),
                "salary": 45000,
                "pf": 12,
                "esi": 1.0
            },
            {
                "name": "Neha Singh",
                "role": "Safety Officer",
                "phone": "9876543213",
                "email": "neha.singh@construction.com",
                "joining_date": datetime(2021, 9, 20).date(),
                "salary": 55000,
                "pf": 12,
                "esi": 0.75
            },
            {
                "name": "Vikram Desai",
                "role": "Laborer",
                "phone": "9876543214",
                "email": "vikram.desai@construction.com",
                "joining_date": datetime(2023, 2, 5).date(),
                "salary": 25000,
                "pf": 12,
                "esi": 1.0
            },
            {
                "name": "Anjali Verma",
                "role": "Laborer",
                "phone": "9876543215",
                "email": "anjali.verma@construction.com",
                "joining_date": datetime(2023, 3, 15).date(),
                "salary": 24000,
                "pf": 12,
                "esi": 1.0
            },
            {
                "name": "Suresh Gupta",
                "role": "Senior Laborer",
                "phone": "9876543216",
                "email": "suresh.gupta@construction.com",
                "joining_date": datetime(2019, 8, 22).date(),
                "salary": 32000,
                "pf": 12,
                "esi": 1.0
            },
            {
                "name": "Meera Nair",
                "role": "Assistant Engineer",
                "phone": "9876543217",
                "email": "meera.nair@construction.com",
                "joining_date": datetime(2022, 7, 11).date(),
                "salary": 45000,
                "pf": 12,
                "esi": 0.75
            },
            {
                "name": "Akshay Rao",
                "role": "Equipment Operator",
                "phone": "9876543218",
                "email": "akshay.rao@construction.com",
                "joining_date": datetime(2021, 11, 30).date(),
                "salary": 40000,
                "pf": 12,
                "esi": 1.0
            },
            {
                "name": "Pooja Chawla",
                "role": "Quality Inspector",
                "phone": "9876543219",
                "email": "pooja.chawla@construction.com",
                "joining_date": datetime(2022, 5, 18).date(),
                "salary": 50000,
                "pf": 12,
                "esi": 0.75
            },
            {
                "name": "Ravi Shankar",
                "role": "Laborer",
                "phone": "9876543220",
                "email": "ravi.shankar@construction.com",
                "joining_date": datetime(2023, 1, 10).date(),
                "salary": 23000,
                "pf": 12,
                "esi": 1.0
            },
            {
                "name": "Divya Joshi",
                "role": "Supervisor",
                "phone": "9876543221",
                "email": "divya.joshi@construction.com",
                "joining_date": datetime(2020, 12, 5).date(),
                "salary": 52000,
                "pf": 12,
                "esi": 0.75
            }
        ]

        staff_records = []
        for data in staff_data:
            staff = Staff(**data)
            db.session.add(staff)
            staff_records.append(staff)
            print(f"  ✅ Added: {data['name']} ({data['role']})")

        db.session.commit()
        print(f"\n✅ Created {len(staff_records)} staff records")

        # ============================================
        # SEED ATTENDANCE DATA
        # ============================================
        print("\n📅 Creating Attendance records...")

        # Generate attendance for last 45 days
        today = datetime.now().date()
        start_date = today - timedelta(days=45)

        attendance_records = []

        for staff in staff_records:
            current_date = start_date

            while current_date <= today:
                # Skip weekends (Saturday=5, Sunday=6)
                if current_date.weekday() < 5:  # Monday to Friday
                    # Realistic attendance patterns
                    import random
                    rand = random.random()

                    # 85% present, 10% half day, 5% absent
                    if rand < 0.85:
                        present = True
                        half_day = False
                        night_shift = False
                        overtime = random.choice([0, 0, 0, 2, 3, 4]) if staff.role in ["Site Engineer", "Project Manager", "Supervisor"] else 0
                    elif rand < 0.95:
                        present = True
                        half_day = True
                        night_shift = False
                        overtime = 0
                    else:
                        present = False
                        half_day = False
                        night_shift = False
                        overtime = 0

                    # Occasionally add night shifts for laborers and operators
                    if staff.role in ["Laborer", "Senior Laborer", "Equipment Operator"] and random.random() < 0.05:
                        night_shift = True

                    # Check for duplicate before adding
                    existing = Attendance.query.filter_by(
                        staff_id=staff.id,
                        date=current_date
                    ).first()

                    if not existing:
                        attendance = Attendance(
                            staff_id=staff.id,
                            date=current_date,
                            present=present,
                            half_day=half_day,
                            night_shift=night_shift,
                            overtime_hours=overtime
                        )
                        db.session.add(attendance)
                        attendance_records.append(attendance)

                current_date += timedelta(days=1)

        db.session.commit()
        print(f"✅ Created {len(attendance_records)} attendance records")

        # ============================================
        # PRINT SUMMARY
        # ============================================
        print("\n" + "="*60)
        print("🎉 DATABASE SEEDING COMPLETED!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Staff Members: {Staff.query.count()}")
        print(f"  • Attendance Records: {Attendance.query.count()}")
        print(f"  • Date Range: {start_date} to {today}")
        print(f"\n✨ Sample Data Details:")
        print(f"  • Roles: Site Engineer, Project Manager, Foreman, Safety Officer,")
        print(f"           Assistant Engineer, Supervisor, Quality Inspector, etc.")
        print(f"  • Salaries: ₹23,000 - ₹75,000")
        print(f"  • Attendance Pattern: 85% present, 10% half-day, 5% absent")
        print(f"\n🚀 Your modules are ready! Data is now visible in the UI.")
        print("="*60 + "\n")


if __name__ == "__main__":
    seed_database()
