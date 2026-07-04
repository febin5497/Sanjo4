import sqlite3
from datetime import datetime, timedelta
import random

db_path = "data.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Enable foreign keys
cursor.execute('PRAGMA foreign_keys = ON')

# 1. Create/Insert Company
company_data = ('Test Construction Co', 'support@testconstruction.com', '+1-234-567-8900', '123 Main St, New York, NY')
cursor.execute('''INSERT INTO company (name, email, phone, address) VALUES (?, ?, ?, ?)''', company_data)
conn.commit()

# Get company ID
cursor.execute('SELECT id FROM company LIMIT 1')
company_id = cursor.fetchone()[0]
print("[OK] Company created: ID={}".format(company_id))

# 2. Create Admin User
user_data = ('admin', 'Test@1234', 'admin', company_id, True)
cursor.execute('''INSERT INTO user (username, password, role, company_id, is_active) VALUES (?, ?, ?, ?, ?)''', user_data)
conn.commit()

cursor.execute('SELECT id FROM user LIMIT 1')
admin_user_id = cursor.fetchone()[0]
print("[OK] Admin user created: ID={}".format(admin_user_id))

# 3. Create Clients
clients = [
    ('ABC Construction Ltd', 'John Smith', 'john@abc-const.com', '+1-111-111-1111'),
    ('XYZ Developers Inc', 'Jane Doe', 'jane@xyz-dev.com', '+1-222-222-2222'),
    ('BuildRight Corp', 'Mike Johnson', 'mike@buildright.com', '+1-333-333-3333'),
]

client_ids = []
for client in clients:
    cursor.execute('''INSERT INTO client (name, contact_person, email, phone) VALUES (?, ?, ?, ?)''', client)
    conn.commit()
    cursor.execute('SELECT last_insert_rowid()')
    client_id = cursor.fetchone()[0]
    client_ids.append(client_id)
    print("[OK] Client created: {}".format(client[0]))

# 4. Create Materials
materials = [
    ('Cement (50kg bag)', 'kg', 150.00, 100),
    ('Steel Bar (12mm)', 'kg', 45.00, 200),
    ('Bricks (red)', 'thousand', 5000.00, 50),
    ('Sand', 'ton', 2000.00, 100),
    ('Gravel', 'ton', 2500.00, 80),
    ('Plywood (4x8)', 'piece', 1200.00, 30),
    ('Electrical Wire', 'meter', 15.00, 500),
    ('Paint', 'liter', 350.00, 100),
]

material_ids = []
for material in materials:
    cursor.execute('''INSERT INTO material (name, unit, unit_price, quantity, company_id)
                      VALUES (?, ?, ?, ?, ?)''', (material[0], material[1], material[2], material[3], company_id))
    conn.commit()
    cursor.execute('SELECT last_insert_rowid()')
    mat_id = cursor.fetchone()[0]
    material_ids.append(mat_id)
    print("[OK] Material created: {}".format(material[0]))

# 5. Create Staff
staff_list = [
    ('Rajesh Kumar', 'Foreman', '9876543210', 'rajesh@test.com', 50000, 5000, 2000),
    ('Priya Sharma', 'Site Engineer', '9876543211', 'priya@test.com', 65000, 6500, 2500),
    ('Arun Singh', 'Supervisor', '9876543212', 'arun@test.com', 45000, 4500, 1800),
    ('Neha Patel', 'Safety Officer', '9876543213', 'neha@test.com', 40000, 4000, 1500),
    ('Vikram Verma', 'Electrician', '9876543214', 'vikram@test.com', 35000, 3500, 1200),
]

staff_ids = []
joining_date = datetime.now() - timedelta(days=365)
for staff in staff_list:
    cursor.execute('''INSERT INTO staff (name, role, phone, email, salary, pf, esi, joining_date, company_id, created_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (staff[0], staff[1], staff[2], staff[3], staff[4], staff[5], staff[6], joining_date.strftime('%Y-%m-%d'), company_id, datetime.utcnow()))
    conn.commit()
    cursor.execute('SELECT last_insert_rowid()')
    staff_id = cursor.fetchone()[0]
    staff_ids.append(staff_id)
    print("[OK] Staff created: {}".format(staff[0]))

# 6. Create Projects
projects = [
    ('Residential Complex A', 'Mumbai, India', 'In Progress', 50000, 5000, admin_user_id, company_id, client_ids[0]),
    ('Commercial Building B', 'Delhi, India', 'Not Started', 75000, 8000, admin_user_id, company_id, client_ids[1]),
    ('Office Tower C', 'Bangalore, India', 'Planning', 100000, 10000, admin_user_id, company_id, client_ids[2]),
    ('Hospital D', 'Hyderabad, India', 'In Progress', 60000, 6500, admin_user_id, company_id, client_ids[0]),
]

project_ids = []
for project in projects:
    start_date = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''INSERT INTO project (name, location, status, rate_per_sqft, square_feet, user_id, company_id, client_id, start_date)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (project[0], project[1], project[2], project[3], project[4], project[5], project[6], project[7], start_date))
    conn.commit()
    cursor.execute('SELECT last_insert_rowid()')
    proj_id = cursor.fetchone()[0]
    project_ids.append(proj_id)
    print("[OK] Project created: {}".format(project[0]))

# 7. Assign staff to projects
for i, proj_id in enumerate(project_ids):
    staff_to_assign = random.sample(staff_ids, min(3, len(staff_ids)))
    for staff_id in staff_to_assign:
        cursor.execute('''INSERT INTO project_assignment (project_id, staff_id, assigned_on)
                          VALUES (?, ?, ?)''', (proj_id, staff_id, datetime.utcnow()))
        cursor.execute('''INSERT INTO project_staff_history (project_id, staff_id, assigned_date)
                          VALUES (?, ?, ?)''', (proj_id, staff_id, datetime.utcnow()))
        conn.commit()
print("[OK] Staff assigned to projects")

# 8. Create Invoices
invoice_ids = []
for i, proj_id in enumerate(project_ids):
    invoice_no = 'INV-{}-{}'.format(datetime.now().year, 1001 + i)
    cursor.execute('''INSERT INTO invoice (invoice_no, project_id, company_id, amount, status, created_at)
                      VALUES (?, ?, ?, ?, ?, ?)''', (invoice_no, proj_id, company_id, 500000 + i*100000, 'Pending', datetime.utcnow()))
    conn.commit()
    cursor.execute('SELECT last_insert_rowid()')
    inv_id = cursor.fetchone()[0]
    invoice_ids.append(inv_id)
print("[OK] Invoices created")

# 9. Create Vehicles
vehicles = [
    ('Excavator', 'CAT-320', 'Operational'),
    ('Concrete Mixer', 'KIRLOSKAR-350', 'Operational'),
    ('Dumper Truck', 'TATA-PRIMA', 'Maintenance'),
    ('JCB', 'JCB-3DX', 'Operational'),
    ('Crane', 'LIEBHERR-LR1130', 'Operational'),
]

for vehicle in vehicles:
    cursor.execute('''INSERT INTO vehicle (name, model, status, company_id) VALUES (?, ?, ?, ?)''', (vehicle[0], vehicle[1], vehicle[2], company_id))
    conn.commit()
print("[OK] Vehicles created")

# 10. Create Attendance Records (last 10 days)
for staff_id in staff_ids:
    for days_ago in range(10, 0, -1):
        attendance_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        is_present = random.choice([True, True, False])
        if is_present:
            cursor.execute('''INSERT INTO attendance (staff_id, attendance_date, is_present, company_id)
                              VALUES (?, ?, ?, ?)''', (staff_id, attendance_date, is_present, company_id))
            conn.commit()
print("[OK] Attendance records created")

# 11. Create Salary Records
for staff_id in staff_ids:
    cursor.execute('''INSERT INTO salary_record (staff_id, month, year, basic_salary, pf, esi, total, status, company_id)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (staff_id, 3, 2026, 50000, 5000, 2000, 47000, 'Paid', company_id))
    conn.commit()
print("[OK] Salary records created")

conn.close()
print("\n[DONE] Test data population completed successfully!")
