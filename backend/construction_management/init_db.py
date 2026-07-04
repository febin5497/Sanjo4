#!/usr/bin/env python
"""Initialize database with schema and seed data"""
import os
import sys
from app import app, db
from user_management.models import User
from company_settings.models import Company
from client_management.models import Client
from material_management.models import Material
from staff_management.models import Staff
from project_management.models import Project, ProjectAssignment
from project_management.models.models import ProjectStaffHistory
from vehicle_management.models import Vehicle
from attendance_management.models import Attendance
from salary_management.models import SalaryRecord
from invoice_management.models import Invoice, InvoiceItem
from datetime import datetime, timedelta
import random

print("[*] Initializing database...")

with app.app_context():
    # Create all tables
    db.create_all()
    print("[OK] Database schema created")

    # 1. Create Company
    company = Company(
        name='Test Construction Co',
        email='support@testconstruction.com',
        phone='+1-234-567-8900',
        address='123 Main St, New York, NY'
    )
    db.session.add(company)
    db.session.commit()
    print("[OK] Company created: Test Construction Co")

    # 2. Create Admin User
    admin = User(
        username='admin',
        role='admin',
        company_id=company.id,
        is_active=True
    )
    admin.set_password('Test@1234')
    db.session.add(admin)
    db.session.commit()
    print("[OK] Admin user created: admin (password: Test@1234)")

    # 3. Create Clients
    clients_data = [
        ('ABC Construction Ltd', 'John Smith', 'john@abc-const.com', '+1-111-111-1111'),
        ('XYZ Developers Inc', 'Jane Doe', 'jane@xyz-dev.com', '+1-222-222-2222'),
        ('BuildRight Corp', 'Mike Johnson', 'mike@buildright.com', '+1-333-333-3333'),
    ]

    clients = []
    for name, contact, email, phone in clients_data:
        client = Client(
            name=name,
            contact_person=contact,
            email=email,
            phone=phone,
            company_id=company.id
        )
        db.session.add(client)
        clients.append(client)
    db.session.commit()
    print("[OK] 3 Clients created")

    # 4. Create Materials
    materials_data = [
        ('Cement (50kg bag)', 'kg', 150.00, 100),
        ('Steel Bar (12mm)', 'kg', 45.00, 200),
        ('Bricks (red)', 'thousand', 5000.00, 50),
        ('Sand', 'ton', 2000.00, 100),
        ('Gravel', 'ton', 2500.00, 80),
        ('Plywood (4x8)', 'piece', 1200.00, 30),
        ('Electrical Wire', 'meter', 15.00, 500),
        ('Paint', 'liter', 350.00, 100),
    ]

    materials = []
    for name, unit, price, qty in materials_data:
        material = Material(
            name=name,
            unit=unit,
            unit_price=price,
            quantity=qty,
            company_id=company.id
        )
        db.session.add(material)
        materials.append(material)
    db.session.commit()
    print("[OK] 8 Materials created")

    # 5. Create Staff
    staff_data = [
        ('Rajesh Kumar', 'Foreman', '9876543210', 'rajesh@test.com', 50000, 5000, 2000),
        ('Priya Sharma', 'Site Engineer', '9876543211', 'priya@test.com', 65000, 6500, 2500),
        ('Arun Singh', 'Supervisor', '9876543212', 'arun@test.com', 45000, 4500, 1800),
        ('Neha Patel', 'Safety Officer', '9876543213', 'neha@test.com', 40000, 4000, 1500),
        ('Vikram Verma', 'Electrician', '9876543214', 'vikram@test.com', 35000, 3500, 1200),
    ]

    staff_list = []
    joining_date = datetime.now() - timedelta(days=365)
    for name, role, phone, email, salary, pf, esi in staff_data:
        staff = Staff(
            name=name,
            role=role,
            phone=phone,
            email=email,
            salary=salary,
            pf=pf,
            esi=esi,
            joining_date=joining_date.date(),
            company_id=company.id
        )
        db.session.add(staff)
        staff_list.append(staff)
    db.session.commit()
    print("[OK] 5 Staff members created")

    # 6. Create Projects
    projects_data = [
        ('Residential Complex A', 'Mumbai, India', 'In Progress', 50000, 5000),
        ('Commercial Building B', 'Delhi, India', 'Not Started', 75000, 8000),
        ('Office Tower C', 'Bangalore, India', 'Planning', 100000, 10000),
        ('Hospital D', 'Hyderabad, India', 'In Progress', 60000, 6500),
    ]

    projects = []
    for name, location, status, rate, sqft in projects_data:
        project = Project(
            name=name,
            location=location,
            status=status,
            rate_per_sqft=rate,
            square_feet=sqft,
            user_id=admin.id,
            company_id=company.id,
            client_id=random.choice(clients).id,
            start_date=datetime.now().date()
        )
        db.session.add(project)
        projects.append(project)
    db.session.commit()
    print("[OK] 4 Projects created")

    # 7. Assign Staff to Projects
    for proj in projects:
        staff_to_assign = random.sample(staff_list, min(3, len(staff_list)))
        for stf in staff_to_assign:
            assignment = ProjectAssignment(
                project_id=proj.id,
                staff_id=stf.id,
                assigned_on=datetime.utcnow()
            )
            history = ProjectStaffHistory(
                project_id=proj.id,
                staff_id=stf.id,
                assigned_date=datetime.utcnow()
            )
            db.session.add(assignment)
            db.session.add(history)
    db.session.commit()
    print("[OK] Staff assigned to projects")

    # 8. Create Vehicles
    vehicles_data = [
        ('Excavator', 'CAT-320', 'Operational'),
        ('Concrete Mixer', 'KIRLOSKAR-350', 'Operational'),
        ('Dumper Truck', 'TATA-PRIMA', 'Maintenance'),
        ('JCB', 'JCB-3DX', 'Operational'),
        ('Crane', 'LIEBHERR-LR1130', 'Operational'),
    ]

    for name, model, status in vehicles_data:
        vehicle = Vehicle(
            name=name,
            model=model,
            status=status,
            company_id=company.id
        )
        db.session.add(vehicle)
    db.session.commit()
    print("[OK] 5 Vehicles created")

    # 9. Create Attendance Records
    for stf in staff_list:
        for days_ago in range(10, 0, -1):
            if random.random() > 0.34:  # 66% attendance rate
                attendance_date = (datetime.now() - timedelta(days=days_ago)).date()
                attendance = Attendance(
                    staff_id=stf.id,
                    attendance_date=attendance_date,
                    is_present=True,
                    company_id=company.id
                )
                db.session.add(attendance)
    db.session.commit()
    print("[OK] Attendance records created")

    # 10. Create Salary Records
    for stf in staff_list:
        salary_record = SalaryRecord(
            staff_id=stf.id,
            month=3,
            year=2026,
            basic_salary=stf.salary,
            pf=stf.pf,
            esi=stf.esi,
            total=stf.salary - stf.pf - stf.esi,
            status='Paid',
            company_id=company.id
        )
        db.session.add(salary_record)
    db.session.commit()
    print("[OK] Salary records created")

    # 11. Create Invoices
    for proj in projects:
        invoice = Invoice(
            invoice_no='INV-{}-{}'.format(datetime.now().year, random.randint(1001, 9999)),
            project_id=proj.id,
            company_id=company.id,
            amount=500000 + random.randint(0, 500000),
            status='Pending'
        )
        db.session.add(invoice)
    db.session.commit()
    print("[OK] Invoices created")

    print("\n[DONE] Database initialization completed successfully!")
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Password: Test@1234")
