#!/usr/bin/env python3
"""
Setup script to create Staff record for testuser and other test data
Run this AFTER starting the backend (so database tables exist)
Execute from backend directory: python construction_management/setup_testuser.py
"""

import sys
import os

# Change to construction_management directory
os.chdir('construction_management')
sys.path.insert(0, os.getcwd())

from app import app
from extensions import db
from user_management.models import User
from company_settings.models import Company
from staff_management.models import Staff
from datetime import datetime

with app.app_context():
    print("=" * 60)
    print("Setting up test data for attendance system")
    print("=" * 60)

    try:
        # 1. Create company if not exists
        print("\n[1] Checking Test Construction Company...")
        company = Company.query.filter_by(name='Test Construction Company').first()
        if not company:
            company = Company(name='Test Construction Company')
            db.session.add(company)
            db.session.commit()
            print(f"    Created company: {company.name} (ID: {company.id})")
        else:
            print(f"    Found existing company: {company.name} (ID: {company.id})")

        # 2. Create testuser if not exists
        print("\n[2] Checking testuser account...")
        testuser = User.query.filter_by(username='testuser').first()
        if not testuser:
            testuser = User(username='testuser', role='worker', company_id=company.id)
            testuser.set_password('Test@123')
            db.session.add(testuser)
            db.session.commit()
            print(f"    Created user: testuser (ID: {testuser.id})")
        else:
            print(f"    Found existing user: testuser (ID: {testuser.id})")
            # Update company_id if not set
            if not testuser.company_id:
                testuser.company_id = company.id
                db.session.commit()
                print(f"    Updated testuser to company: {company.name}")

        # 3. Create Staff record for testuser
        print("\n[3] Checking Staff record for testuser...")
        staff = Staff.query.filter_by(user_id=testuser.id).first()
        if not staff:
            staff = Staff(
                name='Test Worker',
                role='Site Worker',
                phone='+1234567890',
                email='testuser@construction.com',
                joining_date=datetime.utcnow().date(),
                salary=30000,
                pf=12,
                esi=4.75,
                user_id=testuser.id,
                company_id=company.id
            )
            db.session.add(staff)
            db.session.commit()
            print(f"    Created Staff record: Test Worker (ID: {staff.id})")
        else:
            print(f"    Found existing Staff record: {staff.name} (ID: {staff.id})")

        print("\n" + "=" * 60)
        print("Test data setup complete!")
        print("=" * 60)
        print("\nYou can now login with:")
        print("  Company: Test Construction Company")
        print("  Username: testuser")
        print("  Password: Test@123")
        print("\nThe app will route to the worker dashboard after login.")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
    finally:
        db.session.close()
