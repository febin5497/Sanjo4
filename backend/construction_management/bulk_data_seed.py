"""
Comprehensive Bulk Data Seeding Script
Populates ALL major models with realistic sample data
"""

import random
from datetime import datetime, timedelta
from extensions import db
from app import create_app

# ============================================
# DATA DEFINITIONS
# ============================================

CLIENTS = [
    {"name": "Greenfield Builders", "email": "info@greenfield.in", "phone": "9988776655", "address": "42 MG Road, Mumbai"},
    {"name": "Urban Spaces Ltd", "email": "contact@urbanspaces.com", "phone": "8877665544", "address": "15 Brigade Road, Bangalore"},
    {"name": "Skyline Developers", "email": "info@skylinedev.in", "phone": "7766554433", "address": "88 Park Street, Kolkata"},
    {"name": "Nirman Constructions", "email": "nirman@constructions.com", "phone": "6655443322", "address": "7 Shivaji Nagar, Pune"},
    {"name": "Sahyadri Estates", "email": "info@sahyadri.in", "phone": "5544332211", "address": "23 FC Road, Nagpur"},
]

STAFF_DATA = [
    {"first_name": "Rajesh", "last_name": "Kumar", "role": "Project Manager", "designation": "Senior PM", "department": "Management", "personal_phone": "9876543210", "personal_email": "rajesh.k@buildcorp.in", "joining_date": "2021-06-01", "salary": 85000, "monthly_salary": 75000, "gender": "Male"},
    {"first_name": "Priya", "last_name": "Sharma", "role": "Site Engineer", "designation": "Structural Engineer", "department": "Engineering", "personal_phone": "9876543211", "personal_email": "priya.sharma@buildcorp.in", "joining_date": "2022-01-15", "salary": 65000, "monthly_salary": 58000, "gender": "Female"},
    {"first_name": "Amit", "last_name": "Patel", "role": "Supervisor", "designation": "Site Supervisor", "department": "Operations", "personal_phone": "9876543212", "personal_email": "amit.patel@buildcorp.in", "joining_date": "2020-03-10", "salary": 45000, "monthly_salary": 40000, "gender": "Male"},
    {"first_name": "Neha", "last_name": "Singh", "role": "Safety Officer", "designation": "Safety Manager", "department": "HSE", "personal_phone": "9876543213", "personal_email": "neha.singh@buildcorp.in", "joining_date": "2021-09-20", "salary": 55000, "monthly_salary": 50000, "gender": "Female"},
    {"first_name": "Vikram", "last_name": "Desai", "role": "Worker", "designation": "Mason", "department": "Construction", "personal_phone": "9876543214", "personal_email": "vikram.d@buildcorp.in", "joining_date": "2023-02-05", "salary": 25000, "monthly_salary": 22000, "gender": "Male"},
    {"first_name": "Anjali", "last_name": "Verma", "role": "Worker", "designation": "Helper", "department": "Construction", "personal_phone": "9876543215", "personal_email": "anjali.v@buildcorp.in", "joining_date": "2023-03-15", "salary": 24000, "monthly_salary": 21000, "gender": "Female"},
    {"first_name": "Suresh", "last_name": "Gupta", "role": "Worker", "designation": "Senior Mason", "department": "Construction", "personal_phone": "9876543216", "personal_email": "suresh.g@buildcorp.in", "joining_date": "2019-08-22", "salary": 32000, "monthly_salary": 28000, "gender": "Male"},
    {"first_name": "Meera", "last_name": "Nair", "role": "Assistant Engineer", "designation": "Junior Engineer", "department": "Engineering", "personal_phone": "9876543217", "personal_email": "meera.nair@buildcorp.in", "joining_date": "2022-07-11", "salary": 45000, "monthly_salary": 40000, "gender": "Female"},
    {"first_name": "Akshay", "last_name": "Rao", "role": "Driver", "designation": "Equipment Operator", "department": "Logistics", "personal_phone": "9876543218", "personal_email": "akshay.rao@buildcorp.in", "joining_date": "2021-11-30", "salary": 40000, "monthly_salary": 36000, "gender": "Male", "license_number": "MH01-2021-12345", "license_expiry": "2027-11-30"},
    {"first_name": "Pooja", "last_name": "Chawla", "role": "Quality Inspector", "designation": "QA Engineer", "department": "Quality", "personal_phone": "9876543219", "personal_email": "pooja.chawla@buildcorp.in", "joining_date": "2022-05-18", "salary": 50000, "monthly_salary": 45000, "gender": "Female"},
    {"first_name": "Ravi", "last_name": "Shankar", "role": "Worker", "designation": "Carpenter", "department": "Construction", "personal_phone": "9876543220", "personal_email": "ravi.s@buildcorp.in", "joining_date": "2023-01-10", "salary": 23000, "monthly_salary": 20000, "gender": "Male"},
    {"first_name": "Divya", "last_name": "Joshi", "role": "Accountant", "designation": "Finance Officer", "department": "Finance", "personal_phone": "9876543221", "personal_email": "divya.joshi@buildcorp.in", "joining_date": "2020-12-05", "salary": 52000, "monthly_salary": 47000, "gender": "Female"},
    {"first_name": "Karan", "last_name": "Mehta", "role": "Store Keeper", "designation": "Inventory Manager", "department": "Stores", "personal_phone": "9876543222", "personal_email": "karan.mehta@buildcorp.in", "joining_date": "2021-04-10", "salary": 38000, "monthly_salary": 34000, "gender": "Male"},
    {"first_name": "Sneha", "last_name": "Reddy", "role": "HR Executive", "designation": "HR Manager", "department": "HR", "personal_phone": "9876543223", "personal_email": "sneha.reddy@buildcorp.in", "joining_date": "2022-10-01", "salary": 48000, "monthly_salary": 43000, "gender": "Female"},
    {"first_name": "Manoj", "last_name": "Tiwari", "role": "Driver", "designation": "Heavy Vehicle Driver", "department": "Logistics", "personal_phone": "9876543224", "personal_email": "manoj.tiwari@buildcorp.in", "joining_date": "2020-08-15", "salary": 35000, "monthly_salary": 32000, "gender": "Male", "license_number": "UP14-2020-67890", "license_expiry": "2026-08-15"},
]

PROJECTS = [
    {"name": "Green Valley Residency", "location": "Hinjewadi, Pune", "status": "In Progress", "rate_per_sqft": 4500, "square_feet": 25000, "latitude": 18.5793, "longitude": 73.7409},
    {"name": "Skyline Corporate Tower", "location": "Andheri East, Mumbai", "status": "In Progress", "rate_per_sqft": 8500, "square_feet": 75000, "latitude": 19.1136, "longitude": 72.8697},
    {"name": "Lakeview Villas", "location": "Whitefield, Bangalore", "status": "Not Started", "rate_per_sqft": 6200, "square_feet": 18000, "latitude": 12.9716, "longitude": 77.5946},
    {"name": "Riverside Township", "location": "Bandra West, Mumbai", "status": "Planning", "rate_per_sqft": 7800, "square_feet": 120000, "latitude": 19.0596, "longitude": 72.8295},
    {"name": "Industrial Shed Complex", "location": "MIDC, Nagpur", "status": "Completed", "rate_per_sqft": 2200, "square_feet": 60000, "latitude": 21.1458, "longitude": 79.0882},
    {"name": "EduPark School Campus", "location": "Hinjewadi Phase 2, Pune", "status": "In Progress", "rate_per_sqft": 3800, "square_feet": 35000, "latitude": 18.5913, "longitude": 73.7628},
]

SUPPLIERS = [
    {"name": "Tata Steel Ltd", "email": "orders@tatasteel.com", "phone": "1800-345-6789", "contact_person": "Rahul Joshi", "contact_phone": "9988770011", "gstin": "27AABCT1234H1Z5", "payment_terms": "Net 45", "credit_limit": 5000000, "performance_score": 92},
    {"name": "Birla Cement Co", "email": "sales@birlacement.in", "phone": "1800-234-5678", "contact_person": "Sanjay Gupta", "contact_phone": "8877660022", "gstin": "29AABCB5678K1Z3", "payment_terms": "Net 30", "credit_limit": 3500000, "performance_score": 88},
    {"name": "Jindal Building Products", "email": "info@jindalbuild.in", "phone": "9876540099", "contact_person": "Vikram Jindal", "contact_phone": "7766550033", "gstin": "30AABCJ9012L1Z7", "payment_terms": "Net 60", "credit_limit": 2000000, "performance_score": 75},
    {"name": "Shree Cement Ltd", "email": "orders@shreecement.in", "phone": "1800-456-7890", "contact_person": "Amit Agarwal", "contact_phone": "6655440044", "gstin": "24AABCS3456M1Z9", "payment_terms": "Net 30", "credit_limit": 2800000, "performance_score": 85},
    {"name": "Pioneer Hardware", "email": "info@pioneerhw.in", "phone": "9876540088", "contact_person": "Deepak Shah", "contact_phone": "5544330055", "gstin": "27AABCP7890N1Z1", "payment_terms": "Net 15", "credit_limit": 500000, "performance_score": 95},
]

MATERIALS = [
    {"name": "OPC Cement (43 Grade)", "unit_of_measurement": "Bags", "price": 380, "quantity": 5000},
    {"name": "TMT Steel Bars (12mm)", "unit_of_measurement": "Tonnes", "price": 68000, "quantity": 200},
    {"name": "River Sand", "unit_of_measurement": "Cubic Feet", "price": 55, "quantity": 30000},
    {"name": "20mm Crushed Stone", "unit_of_measurement": "Cubic Feet", "price": 45, "quantity": 25000},
    {"name": "Red Clay Bricks", "unit_of_measurement": "1000 pcs", "price": 8500, "quantity": 500},
    {"name": "Ceramic Floor Tiles (2x2 ft)", "unit_of_measurement": "Boxes", "price": 1200, "quantity": 800},
    {"name": "White Paint (20L)", "unit_of_measurement": "Buckets", "price": 3200, "quantity": 150},
    {"name": "PVC Pipes (4 inch)", "unit_of_measurement": "Pieces", "price": 650, "quantity": 1000},
]

VEHICLES = [
    {"make": "Tata", "model": "LPK 2518", "year": 2021, "registration_number": "MH-12-AB-1234", "type": "tipper", "status": "Active", "mileage": 45000},
    {"make": "Ashok Leyland", "model": "Boss 1920", "year": 2022, "registration_number": "MH-14-CD-5678", "type": "tipper", "status": "Active", "mileage": 28000},
    {"make": "Mahindra", "model": "Bolero Pickup", "year": 2020, "registration_number": "MH-12-EF-9012", "type": "commercial", "status": "Active", "mileage": 62000},
    {"make": "Tata", "model": "Prima 4028", "year": 2023, "registration_number": "MH-12-GH-3456", "type": "commercial", "status": "Active", "mileage": 12000},
]

EQUIPMENT = [
    {"name": "JCB 3DX Backhoe Loader", "category": "Heavy Machinery", "equipment_code": "EQ-001", "purchase_cost": 2800000, "current_value": 2200000, "condition": "Good", "location": "Green Valley Site"},
    {"name": "Tower Crane (50m)", "category": "Heavy Machinery", "equipment_code": "EQ-002", "purchase_cost": 8500000, "current_value": 7200000, "condition": "Excellent", "location": "Skyline Tower Site"},
    {"name": "Concrete Mixer (0.5 bag)", "category": "Light Machinery", "equipment_code": "EQ-003", "purchase_cost": 185000, "current_value": 120000, "condition": "Good", "location": "Warehouse A"},
    {"name": "Plate Compactor", "category": "Light Machinery", "equipment_code": "EQ-004", "purchase_cost": 95000, "current_value": 65000, "condition": "Fair", "location": "Warehouse A"},
    {"name": "Welding Machine (400A)", "category": "Tools", "equipment_code": "EQ-005", "purchase_cost": 45000, "current_value": 32000, "condition": "Good", "location": "Green Valley Site"},
    {"name": "Water Pump (5 HP)", "category": "Tools", "equipment_code": "EQ-006", "purchase_cost": 28000, "current_value": 18000, "condition": "Under Repair", "location": "Workshop"},
]

PROJECT_STAGES_TEMPLATES = [
    {"name": "Foundation", "billing_percentage": 15, "order": 1},
    {"name": "Ground Floor Structure", "billing_percentage": 25, "order": 2},
    {"name": "First Floor & Roof", "billing_percentage": 30, "order": 3},
    {"name": "Finishing & Handover", "billing_percentage": 30, "order": 4},
]

# Geo coordinates for project locations (India)
PROJECT_COORDS = [
    {"lat": 18.5793, "lng": 73.7409, "address": "Hinjewadi Phase 1, Pune, Maharashtra 411057"},
    {"lat": 19.1136, "lng": 72.8697, "address": "Andheri East, Mumbai, Maharashtra 400093"},
    {"lat": 12.9716, "lng": 77.5946, "address": "Whitefield, Bangalore, Karnataka 560066"},
    {"lat": 19.0596, "lng": 72.8295, "address": "Bandra West, Mumbai, Maharashtra 400050"},
    {"lat": 21.1458, "lng": 79.0882, "address": "MIDC Hingna, Nagpur, Maharashtra 440028"},
    {"lat": 18.5913, "lng": 73.7628, "address": "Hinjewadi Phase 2, Pune, Maharashtra 411057"},
]


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        print("=" * 60)
        print("COMPREHENSIVE BULK DATA SEEDING")
        print("=" * 60)

        # ============================================
        # 1. COMPANY
        # ============================================
        print("\n1. Company...")
        from company_settings.models import Company
        company = Company.query.filter_by(name="BuildCorp Construction").first()
        if not company:
            company = Company(
                name="BuildCorp Construction",
                email="info@buildcorp.in",
                phone="022-45678900",
                address="202 Tech Park, Andheri East, Mumbai - 400093",
                status="active",
                subscription_plan="enterprise",
                tax_percentage=18.0,
                gst_number="27AABCU1234D1Z1",
                created_by_id=1,
            )
            db.session.add(company)
            db.session.flush()
            print("  Created: BuildCorp Construction (ID: %d)" % company.id)
        else:
            print("  Already exists: BuildCorp Construction (ID: %d)" % company.id)

        # ============================================
        # 2. ADMIN USER
        # ============================================
        print("\n2. Admin User...")
        from user_management.models import User
        from extensions import bcrypt
        admin = User.query.filter_by(username="admin_test").first()
        if not admin:
            admin = User(
                username="admin_test",
                name="Admin User",
                email="admin@buildcorp.in",
                password=bcrypt.generate_password_hash("admin123").decode("utf-8"),
                role="admin",
                company_id=company.id,
                is_active=True,
            )
            db.session.add(admin)
            db.session.flush()
            print("  Created: admin_test (ID: %d)" % admin.id)
        else:
            print("  Already exists: admin_test (ID: %d)" % admin.id)
            admin.company_id = company.id

        db.session.commit()

        # ============================================
        # 3. CLIENTS
        # ============================================
        print("\n3. Clients...")
        from client_management.models import Client
        clients_created = 0
        for c in CLIENTS:
            existing = Client.query.filter_by(name=c["name"]).first()
            if not existing:
                client = Client(**c)
                db.session.add(client)
                clients_created += 1
        db.session.commit()
        all_clients = Client.query.all()
        print("  Total clients: %d (new: %d)" % (len(all_clients), clients_created))

        # ============================================
        # 4. STAFF
        # ============================================
        print("\n4. Staff...")
        from staff_management.models import Staff
        staff_records = []
        i = 1
        for s in STAFF_DATA:
            existing = Staff.query.filter_by(personal_phone=s["personal_phone"]).first()
            if existing:
                staff_records.append(existing)
                continue
            staff = Staff(
                company_id=company.id,
                staff_id="STF-2026-%03d" % i,
                first_name=s["first_name"],
                last_name=s["last_name"],
                name=s["first_name"] + " " + s["last_name"],
                role=s["role"],
                designation=s.get("designation"),
                department=s.get("department"),
                phone=s["personal_phone"],
                email=s["personal_email"],
                personal_phone=s["personal_phone"],
                personal_email=s["personal_email"],
                gender=s.get("gender"),
                joining_date=parse_date(s["joining_date"]),
                salary=s["salary"],
                monthly_salary=s.get("monthly_salary"),
                status="Active",
                license_number=s.get("license_number"),
                license_expiry=parse_date(s["license_expiry"]) if s.get("license_expiry") else None,
                pf_applicable=True,
                esi_applicable=True,
            )
            db.session.add(staff)
            staff_records.append(staff)
            i += 1
        db.session.commit()
        all_staff = Staff.query.all()
        print("  Total staff: %d (new: %d)" % (len(all_staff), len(STAFF_DATA)))

        # Ensure we have enough staff records
        if len(staff_records) < len(STAFF_DATA):
            all_staff = Staff.query.order_by(Staff.id.asc()).all()
            staff_records = all_staff

        # ============================================
        # 5. SUPPLIERS
        # ============================================
        print("\n5. Suppliers...")
        from supplier_management.models import Supplier
        suppliers_created = 0
        for s in SUPPLIERS:
            existing = Supplier.query.filter_by(name=s["name"]).first()
            if not existing:
                supplier = Supplier(**s)
                db.session.add(supplier)
                suppliers_created += 1
        db.session.commit()
        all_suppliers = Supplier.query.all()
        print("  Total suppliers: %d (new: %d)" % (len(all_suppliers), suppliers_created))

        # ============================================
        # 6. MATERIALS
        # ============================================
        print("\n6. Materials...")
        from material_management.models import Material
        materials_created = 0
        for m in MATERIALS:
            existing = Material.query.filter_by(name=m["name"]).first()
            if not existing:
                material = Material(
                    name=m["name"],
                    unit_of_measurement=m["unit_of_measurement"],
                    price=m["price"],
                    quantity=m["quantity"],
                )
                db.session.add(material)
                materials_created += 1
        db.session.commit()
        print("  Total materials: %d (new: %d)" % (len(Material.query.all()), materials_created))

        # ============================================
        # 7. PROJECTS
        # ============================================
        print("\n7. Projects...")
        from project_management.models.models import Project
        project_records = []
        start_date_base = datetime.now() - timedelta(days=365)

        for idx, p in enumerate(PROJECTS):
            existing = Project.query.filter_by(name=p["name"]).first()
            if existing:
                project_records.append(existing)
                continue
            client = all_clients[idx % len(all_clients)]
            proj = Project(
                name=p["name"],
                location=p["location"],
                start_date=start_date_base.date() + timedelta(days=idx * 60),
                user_id=admin.id,
                company_id=company.id,
                client_id=client.id,
                rate_per_sqft=p["rate_per_sqft"],
                square_feet=p["square_feet"],
                status=p["status"],
                latitude=p.get("latitude"),
                longitude=p.get("longitude"),
            )
            db.session.add(proj)
            project_records.append(proj)

        db.session.commit()
        all_projects = Project.query.order_by(Project.id.asc()).all()
        project_records = all_projects
        print("  Total projects: %d" % len(project_records))

        # ============================================
        # 8. PROJECT STAGES
        # ============================================
        print("\n8. Project Stages...")
        from project_management.models.stage import ProjectStage
        stages_created = 0
        for proj in project_records:
            existing_stages = ProjectStage.query.filter_by(project_id=proj.id).count()
            if existing_stages > 0:
                stages_created += existing_stages
                continue
            for st in PROJECT_STAGES_TEMPLATES:
                stage = ProjectStage(
                    project_id=proj.id,
                    name=st["name"],
                    description="%s phase for %s" % (st["name"], proj.name),
                    billing_percentage=st["billing_percentage"],
                    percentage_complete=0,
                    status="not_started",
                    company_id=company.id,
                    planned_start_date=proj.start_date,
                    planned_end_date=proj.start_date + timedelta(days=st["order"] * 90),
                )
                db.session.add(stage)
                stages_created += 1
        db.session.commit()
        print("  Project stages: %d" % stages_created)

        # ============================================
        # 9. PLANNER TASKS (Gantt Chart)
        # ============================================
        print("\n9. Planner Tasks (Gantt)...")
        from planner_management.models import PlannerTask
        task_names = [
            "Site Survey & Soil Testing", "Excavation Work", "Foundation Pouring",
            "Column & Beam Reinforcement", "Slab Casting", "Brickwork & Masonry",
            "Plumbing & Electrical", "Plastering & Flooring", "Painting & Finishing",
            "Landscaping & Handover",
        ]
        planner_tasks_created = 0
        for proj in project_records:
            existing_tasks = PlannerTask.query.filter_by(project_id=proj.id).count()
            if existing_tasks > 0:
                planner_tasks_created += existing_tasks
                continue
            num_tasks = random.randint(4, 7)
            selected = random.sample(task_names, num_tasks)
            task_start = datetime.combine(proj.start_date, datetime.min.time()) if proj.start_date else datetime.now()
            for j, tn in enumerate(selected):
                t_start = task_start + timedelta(days=j * 45)
                t_end = t_start + timedelta(days=30 + random.randint(0, 20))
                status_choice = random.choices(
                    ["todo", "in-progress", "done"],
                    weights=[0.2, 0.5, 0.3],
                )[0] if proj.status == "In Progress" else "todo"
                progress_val = random.randint(0, 100) if status_choice == "done" else (random.randint(10, 80) if status_choice == "in-progress" else 0)
                task = PlannerTask(
                    project_id=proj.id,
                    task_name=tn,
                    start_date=t_start,
                    end_date=t_end,
                    status=status_choice,
                    progress=progress_val,
                    description="%s for %s" % (tn, proj.name),
                )
                db.session.add(task)
                planner_tasks_created += 1
        db.session.commit()
        print("  Planner tasks: %d" % planner_tasks_created)

        # ============================================
        # 10. SITE PHOTOS
        # ============================================
        print("\n10. Site Photos...")
        from site_photos.models import SitePhoto
        photo_categories = ["excavation", "foundation", "structure", "finishing", "aerial", "progress"]
        photo_captions = [
            "Site clearing completed", "Foundation excavation in progress",
            "Concrete pouring for footing", "Steel reinforcement work",
            "Column shuttering completed", "Slab casting in progress",
            "Brickwork on ground floor", "Plumbing rough-in work",
            "Electrical conduit laying", "Plastering completed",
            "Floor tiling in progress", "Painting - first coat",
            "Site progress overview", "Material delivery at site",
            "Safety inspection conducted",
        ]
        site_photos_created = 0
        for proj in project_records:
            existing_photos = SitePhoto.query.filter_by(project_id=proj.id).count()
            if existing_photos > 0:
                site_photos_created += existing_photos
                continue
            num_photos = random.randint(3, 6)
            selected_captions = random.sample(photo_captions, min(num_photos, len(photo_captions)))
            for cap in selected_captions:
                photo = SitePhoto(
                    project_id=proj.id,
                    photo_path="/uploads/projects/%d/%s.jpg" % (proj.id, cap.lower().replace(" ", "_")),
                    caption=cap,
                    category=random.choice(photo_categories),
                    file_type="image/jpeg",
                    file_size=random.randint(200000, 2500000),
                    taken_at=datetime.now() - timedelta(days=random.randint(0, 180)),
                    uploaded_by=admin.id,
                )
                db.session.add(photo)
                site_photos_created += 1
        db.session.commit()
        print("  Site photos: %d" % site_photos_created)

        # ============================================
        # 11. PROJECT LOCATIONS (Map Markers)
        # ============================================
        print("\n11. Project Locations (Maps)...")
        from location_mapping.models import ProjectLocation
        locations_created = 0
        for idx, proj in enumerate(project_records):
            existing_locs = ProjectLocation.query.filter_by(project_id=proj.id).count()
            if existing_locs > 0:
                locations_created += existing_locs
                continue
            coords = PROJECT_COORDS[idx % len(PROJECT_COORDS)]
            loc = ProjectLocation(
                project_id=proj.id,
                name=proj.name,
                latitude=coords["lat"],
                longitude=coords["lng"],
                address=coords["address"],
                marker_type="project",
                marker_color="#0052CC",
                description="Main site location for %s" % proj.name,
                is_gate=False,
                is_entry_point=True,
                radius_meters=100.0,
            )
            db.session.add(loc)
            locations_created += 1

            # Add a gate marker
            gate = ProjectLocation(
                project_id=proj.id,
                name="%s - Main Gate" % proj.name,
                latitude=coords["lat"] + random.uniform(-0.002, 0.002),
                longitude=coords["lng"] + random.uniform(-0.002, 0.002),
                address=coords["address"],
                marker_type="gate",
                marker_color="#E53E3E",
                description="Main entry gate for %s" % proj.name,
                is_gate=True,
                is_entry_point=True,
                radius_meters=10.0,
            )
            db.session.add(gate)
            locations_created += 1
        db.session.commit()
        print("  Map locations: %d" % locations_created)

        # ============================================
        # 12. VEHICLES
        # ============================================
        print("\n12. Vehicles...")
        from vehicle_management.models import Vehicle
        vehicles_created = 0
        for v in VEHICLES:
            existing = Vehicle.query.filter_by(registration_number=v["registration_number"]).first()
            if not existing:
                vehicle = Vehicle(
                    company_id=company.id,
                    make=v["make"],
                    model=v["model"],
                    year=v["year"],
                    registration_number=v["registration_number"],
                    type=v["type"],
                    status=v["status"],
                    mileage=v["mileage"],
                    registration_date=datetime(v["year"], 1, 15).date(),
                    insurance_date=datetime(v["year"], 6, 1).date(),
                    pollution_date=datetime(v["year"], 3, 1).date(),
                )
                db.session.add(vehicle)
                vehicles_created += 1
        db.session.commit()
        all_vehicles = Vehicle.query.all()
        print("  Total vehicles: %d (new: %d)" % (len(all_vehicles), vehicles_created))

        # ============================================
        # 13. EQUIPMENT
        # ============================================
        print("\n13. Equipment...")
        from equipment_management.models import Equipment
        equipment_created = 0
        for eq in EQUIPMENT:
            existing = Equipment.query.filter_by(equipment_code=eq["equipment_code"]).first()
            if not existing:
                equipment = Equipment(
                    company_id=company.id,
                    name=eq["name"],
                    category=eq["category"],
                    equipment_code=eq["equipment_code"],
                    purchase_cost=eq["purchase_cost"],
                    current_value=eq["current_value"],
                    condition=eq["condition"],
                    location=eq["location"],
                    supplier_id=all_suppliers[0].id if all_suppliers else None,
                    purchase_date=datetime.now() - timedelta(days=random.randint(180, 730)),
                    is_active=True,
                )
                db.session.add(equipment)
                equipment_created += 1
        db.session.commit()
        print("  Total equipment: %d (new: %d)" % (len(Equipment.query.all()), equipment_created))

        # ============================================
        # 14. ATTENDANCE RECORDS (Last 60 days)
        # ============================================
        print("\n14. Attendance Records...")
        from attendance_management.models import Attendance
        today = datetime.now().date()
        start_date = today - timedelta(days=60)
        attendance_created = 0

        for staff in staff_records:
            current_date = start_date
            while current_date <= today:
                if current_date.weekday() < 6:
                    rand = random.random()
                    if rand < 0.82:
                        present, half_day, night_shift = True, False, False
                        overtime = random.choice([0, 0, 0, 1, 2, 3]) if staff.role in ["Project Manager", "Site Engineer", "Supervisor"] else 0
                    elif rand < 0.92:
                        present, half_day, night_shift, overtime = True, True, False, 0
                    else:
                        present, half_day, night_shift, overtime = False, False, False, 0

                    if staff.role in ["Worker", "Driver"] and random.random() < 0.05:
                        night_shift = True

                    existing = Attendance.query.filter_by(staff_id=staff.id, date=current_date).first()
                    if not existing:
                        att = Attendance(
                            staff_id=staff.id,
                            date=current_date,
                            present=present,
                            half_day=half_day,
                            night_shift=night_shift,
                            overtime_hours=overtime,
                            status="approved" if present else "pending",
                        )
                        db.session.add(att)
                        attendance_created += 1
                current_date += timedelta(days=1)
        db.session.commit()
        print("  Attendance records created: %d" % attendance_created)

        # ============================================
        # 15. INVOICES
        # ============================================
        print("\n15. Invoices (via raw SQL - model out of sync with schema)...")
        from sqlalchemy import text
        invoices_created = 0
        try:
            for idx, proj in enumerate(project_records[:4]):
                client = Client.query.get(proj.client_id)
                subtotal = (proj.rate_per_sqft or 5000) * (proj.square_feet or 10000) * 0.15
                gst = subtotal * 0.18
                total = subtotal + gst
                due = today - timedelta(days=30 * (len(project_records) - idx)) + timedelta(days=30)
                status = "paid" if idx == 4 else ("sent" if idx < 2 else "draft")
                inv_id = "INV-2026-%04d" % (idx + 1)
                existing = db.session.execute(text("SELECT id FROM invoices WHERE invoice_id = :id"), {"id": inv_id}).fetchone()
                if not existing:
                    db.session.execute(text("""
                        INSERT INTO invoices (invoice_id, client, subtotal, total, gst_rate, gst_amount, due_date, status, description, company_id, created_at, updated_at)
                        VALUES (:inv_id, :client, :subtotal, :total, :gst_rate, :gst, :due, :status, :desc, :company_id, :now, :now)
                    """), {
                        "inv_id": inv_id, "client": client.name if client else "Unknown",
                        "subtotal": subtotal, "total": total, "gst_rate": 18.0, "gst": gst,
                        "due": due.isoformat(), "status": status,
                        "desc": "Progress billing for %s" % proj.name,
                        "company_id": company.id, "now": datetime.utcnow().isoformat(),
                    })
                    invoices_created += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("  Warning: Could not seed invoices (%s)" % e)
        print("  Invoices created: %d" % invoices_created)

        # ============================================
        # 16. QUOTES
        # ============================================
        print("\n16. Quotes...")
        from quote_management.models import Quote
        quotes_created = 0
        for idx, client in enumerate(all_clients[:3]):
            existing = Quote.query.filter_by(client_id=client.id).first()
            if existing:
                quotes_created += Quote.query.filter_by(client_id=client.id).count()
                continue
            subtotal = random.uniform(500000, 5000000)
            tax = subtotal * 0.18
            quote = Quote(
                company_id=company.id,
                quote_number="QTE-2026-%04d" % (idx + 1),
                client_id=client.id,
                user_id=admin.id,
                subtotal=subtotal,
                tax_rate=18.0,
                tax_amount=tax,
                total=subtotal + tax,
                valid_until=datetime.now() + timedelta(days=30),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.session.add(quote)
            quotes_created += 1
        db.session.commit()
        print("  Quotes: %d" % quotes_created)

        # ============================================
        # 17. FINANCE: Chart of Accounts
        # ============================================
        print("\n17. Chart of Accounts...")
        from finance_management.models.chart_of_accounts import ChartOfAccounts
        coa_entries = [
            {"account_code": "1001", "name": "Cash", "account_type": "asset", "category": "Current Assets", "description": "Cash on hand"},
            {"account_code": "1002", "name": "Bank Account", "account_type": "asset", "category": "Current Assets", "description": "Main operating account"},
            {"account_code": "1101", "name": "Accounts Receivable", "account_type": "asset", "category": "Current Assets", "description": "Client invoices due"},
            {"account_code": "1201", "name": "Equipment", "account_type": "asset", "category": "Fixed Assets", "description": "Construction equipment"},
            {"account_code": "2001", "name": "Accounts Payable", "account_type": "liability", "category": "Current Liabilities", "description": "Supplier bills due"},
            {"account_code": "2101", "name": "Salaries Payable", "account_type": "liability", "category": "Current Liabilities", "description": "Staff salaries pending"},
            {"account_code": "3001", "name": "Owner's Equity", "account_type": "equity", "category": "Equity", "description": "Capital invested"},
            {"account_code": "4001", "name": "Project Revenue", "account_type": "revenue", "category": "Income", "description": "Income from projects"},
            {"account_code": "4002", "name": "Consulting Income", "account_type": "revenue", "category": "Income", "description": "Consulting fees"},
            {"account_code": "5001", "name": "Material Cost", "account_type": "expense", "category": "material", "description": "Raw material purchases"},
            {"account_code": "5002", "name": "Labor Cost", "account_type": "expense", "category": "labor", "description": "Staff and worker wages"},
            {"account_code": "5003", "name": "Transport Cost", "account_type": "expense", "category": "transport", "description": "Logistics and transport"},
            {"account_code": "5004", "name": "Equipment Rental", "account_type": "expense", "category": "equipment", "description": "Equipment hire costs"},
        ]
        coa_created = 0
        for entry in coa_entries:
            existing = ChartOfAccounts.query.filter_by(account_code=entry["account_code"], company_id=company.id).first()
            if not existing:
                account = ChartOfAccounts(company_id=company.id, **entry)
                db.session.add(account)
                coa_created += 1
        db.session.commit()
        print("  Chart of Accounts: %d created" % coa_created)

        # ============================================
        # 18. FINANCE: Budgets & Budget Categories
        # ============================================
        print("\n18. Budgets & Categories...")
        from finance_management.models.budget import Budget, BudgetCategory
        budgets_created = 0
        categories_created = 0
        budget_categories_pool = [
            {"category": "material", "allocated": 5000000, "pct_range": (0.4, 0.6)},
            {"category": "labor", "allocated": 3000000, "pct_range": (0.2, 0.35)},
            {"category": "transport", "allocated": 500000, "pct_range": (0.05, 0.1)},
            {"category": "equipment", "allocated": 800000, "pct_range": (0.05, 0.12)},
        ]
        for proj in project_records:
            existing = Budget.query.filter_by(project_id=proj.id, company_id=company.id).first()
            if existing:
                budgets_created += 1
                categories_created += len(existing.categories)
                continue
            total_budget = (proj.rate_per_sqft or 5000) * (proj.square_feet or 10000)
            budget = Budget(
                company_id=company.id,
                project_id=proj.id,
                total_budget=total_budget,
                status="active",
                start_date=today - timedelta(days=60),
                end_date=today + timedelta(days=365),
                description="Budget for %s" % proj.name,
                created_by_id=admin.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.session.add(budget)
            db.session.flush()
            budgets_created += 1
            for bc in budget_categories_pool:
                allocated = int(bc["allocated"] * random.uniform(*bc["pct_range"]))
                cat = BudgetCategory(
                    budget_id=budget.id,
                    category=bc["category"],
                    allocated_amount=allocated,
                    used_amount=int(allocated * random.uniform(0.1, 0.4)),
                    warning_threshold=80,
                )
                db.session.add(cat)
                categories_created += 1
        db.session.commit()
        print("  Budgets: %d, Categories: %d" % (budgets_created, categories_created))

        # ============================================
        # 19. FINANCE: Cash Transactions
        # ============================================
        print("\n19. Cash Transactions (with Chart of Accounts)...")
        from finance_management.models.cash_transaction import CashTransaction
        from finance_management.models.chart_of_accounts import ChartOfAccounts
        from project_management.models.models import Project
        tx_created = 0
        income_accounts = ChartOfAccounts.query.filter_by(account_type='revenue', company_id=company.id).all()
        expense_accounts = ChartOfAccounts.query.filter_by(account_type='expense', company_id=company.id).all()
        for proj in project_records:
            project = Project.query.get(proj.id)
            if not project:
                continue
            # 2 income transactions per project
            for i in range(2):
                date = today - timedelta(days=random.randint(10, 90))
                amount = random.randint(50000, 500000)
                acct = random.choice(income_accounts) if income_accounts else None
                tx = CashTransaction(
                    project_id=proj.id,
                    staff_id=None,
                    date=date,
                    type="income",
                    category=acct.category if acct else 'project_revenue',
                    account_code=acct.account_code if acct else None,
                    amount=amount,
                    description="Payment received for %s - milestone %d" % (project.name, i + 1),
                    created_by=admin.id,
                )
                db.session.add(tx)
                tx_created += 1
            # 3-5 expense transactions per project
            for i in range(random.randint(3, 5)):
                date = today - timedelta(days=random.randint(5, 95))
                amount = random.randint(5000, 150000)
                acct = random.choice(expense_accounts) if expense_accounts else None
                tx = CashTransaction(
                    project_id=proj.id,
                    staff_id=random.choice(all_staff).id if all_staff else None,
                    date=date,
                    type="expense",
                    category=acct.category if acct else random.choice(['material', 'labor', 'transport', 'equipment']),
                    account_code=acct.account_code if acct else None,
                    amount=amount,
                    description="%s expense for %s" % ((acct.name if acct else 'General'), project.name),
                    created_by=admin.id,
                )
                db.session.add(tx)
                tx_created += 1
        db.session.commit()
        print("  Cash Transactions (with CoA codes): %d" % tx_created)

        # ============================================
        # SUMMARY
        # ============================================
        print("\n" + "=" * 60)
        print("BULK DATA SEEDING COMPLETED!")
        print("=" * 60)
        print("\nSummary:")
        print("  Company: 1")
        print("  Admin User: 1")
        print("  Clients: %d" % Client.query.count())
        print("  Staff: %d" % Staff.query.count())
        print("  Suppliers: %d" % Supplier.query.count())
        print("  Materials: %d" % len(MATERIALS))
        print("  Projects: %d" % len(project_records))
        print("  Project Stages: %d" % ProjectStage.query.count())
        print("  Planner Tasks: %d" % PlannerTask.query.count())
        print("  Site Photos: %d" % SitePhoto.query.count())
        print("  Map Locations: %d" % ProjectLocation.query.count())
        print("  Vehicles: %d" % len(all_vehicles))
        print("  Equipment: %d" % len(EQUIPMENT))
        print("  Attendance Records: %d" % attendance_created)
        print("  Invoices: %d" % invoices_created)
        print("  Quotes: %d" % quotes_created)
        print("  Chart of Accounts: %d" % coa_created)
        print("  Budgets: %d" % budgets_created)
        print("  Cash Transactions: %d" % tx_created)
        print("\nData populated! Refresh the UI to see it.")


if __name__ == "__main__":
    seed_database()
