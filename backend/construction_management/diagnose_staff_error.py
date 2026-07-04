#!/usr/bin/env python3
"""
Diagnostic script to test staff creation and find the exact error
"""
import sys
import os
import json
from datetime import datetime

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 70)
print("STAFF CREATION DIAGNOSTIC")
print("=" * 70)

# Test 1: Import all required modules
print("\n[1/5] Testing imports...")
try:
    from app import create_app
    from extensions import db
    from user_management.models import User
    from staff_management.models import Staff
    from staff_management.user_id_service import UserIDGenerator
    print("  [OK] All imports successful")
except Exception as e:
    print(f"  [ERROR] Import failed: {e}")
    sys.exit(1)

# Test 2: Create Flask app
print("\n[2/5] Creating Flask app...")
try:
    app = create_app()
    print("  [OK] Flask app created")
except Exception as e:
    print(f"  [ERROR] App creation failed: {e}")
    sys.exit(1)

# Test 3: Check database and create test user
print("\n[3/5] Setting up test data...")
try:
    with app.app_context():
        # Check if companies table exists
        from company_management.models import Company
        company = Company.query.first()
        if not company:
            print("  [WARN] No companies found, creating test company...")
            company = Company(company_name="Test Company")
            db.session.add(company)
            db.session.commit()
            company_id = company.id
        else:
            company_id = company.id
            print(f"  [OK] Found company: {company.company_name} (ID: {company_id})")

        # Check or create test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            print("  [WARN] Test user not found, creating...")
            from extensions import bcrypt
            test_user = User(
                username='testuser',
                email='test@example.com',
                company_id=company_id
            )
            test_user.password = bcrypt.generate_password_hash('testpass123')
            db.session.add(test_user)
            db.session.commit()
            print(f"  [OK] Created test user (ID: {test_user.id}, Company: {test_user.company_id})")
        else:
            print(f"  [OK] Found test user (ID: {test_user.id}, Company: {test_user.company_id})")
except Exception as e:
    print(f"  [ERROR] Setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test staff creation directly
print("\n[4/5] Testing staff creation...")
try:
    with app.app_context():
        # Prepare test data
        test_data = {
            "name": "Paul John",
            "first_name": "Paul",
            "last_name": "John",
            "role": "Site Supervisor",
            "phone": "9544221144",
            "personal_phone": "9544221144",
            "email": "paul@gmail.com",
            "personal_email": "paul@gmail.com",
            "joining_date": "03/04/2026",
            "salary": 15000,
            "pf": 0,
            "esi": 0,
            "needs_user_access": True
        }

        print(f"  Test data: {json.dumps(test_data, indent=2)}")

        # Get test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            print("  [ERROR] Test user not found!")
            sys.exit(1)

        print(f"\n  Creating staff for user: {test_user.username} (Company: {test_user.company_id})")

        # Generate staff ID
        staff_id = UserIDGenerator.generate_user_id(test_user.company_id)
        print(f"  Generated staff ID: {staff_id}")

        # Parse dates
        from datetime import datetime as dt
        joining_date = None
        try:
            joining_date = dt.strptime(test_data['joining_date'], '%d/%m/%Y').date()
        except:
            joining_date = dt.now().date()

        print(f"  Parsed joining_date: {joining_date}")

        # Create staff object
        staff = Staff(
            company_id=test_user.company_id or 1,
            staff_id=staff_id,
            name=test_data.get('name', ''),
            first_name=test_data.get('first_name', 'Paul'),
            last_name=test_data.get('last_name', 'John'),
            role=test_data.get('role', 'worker'),
            phone=test_data.get('phone', ''),
            personal_phone=test_data.get('personal_phone', ''),
            email=test_data.get('email'),
            personal_email=test_data.get('personal_email'),
            joining_date=joining_date,
            salary=float(test_data.get('salary', 0)),
            pf=float(test_data.get('pf', 0)),
            esi=float(test_data.get('esi', 0)),
            monthly_salary=float(test_data.get('salary', 0)),
            status='Active'
        )

        print(f"  Staff object created")
        print(f"    - ID: {staff.id}")
        print(f"    - Name: {staff.first_name} {staff.last_name}")
        print(f"    - Company: {staff.company_id}")
        print(f"    - Role: {staff.role}")

        # Add to database
        db.session.add(staff)
        db.session.commit()

        print(f"  [OK] Staff created successfully (ID: {staff.id})")

except Exception as e:
    print(f"  [ERROR] Staff creation failed!")
    print(f"  Error: {e}")
    print(f"\n  Full traceback:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Verify creation
print("\n[5/5] Verifying staff creation...")
try:
    with app.app_context():
        staff = Staff.query.filter_by(name="Paul John").first()
        if staff:
            print(f"  [OK] Staff verified in database!")
            print(f"    - ID: {staff.id}")
            print(f"    - Name: {staff.first_name} {staff.last_name}")
            print(f"    - Salary: {staff.salary}")
        else:
            print(f"  [WARN] Staff not found in database after creation")
except Exception as e:
    print(f"  [ERROR] Verification failed: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nIf all tests passed, the issue is with the API request format.")
print("If a test failed, the error message above shows the exact problem.")
print("=" * 70)
