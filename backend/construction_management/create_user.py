import sqlite3
from datetime import datetime

conn = sqlite3.connect('data.db')
c = conn.cursor()

# Create a company
company_name = 'BuildERP Construction'
c.execute('''
    INSERT INTO companies (name, created_at)
    VALUES (?, ?)
''', (company_name, datetime.now()))
conn.commit()

# Get the company ID
c.execute('SELECT id FROM companies ORDER BY id DESC LIMIT 1')
company_id = c.fetchone()[0]

# Create user account
username = 'admin'
password = 'Admin@123'
role = 'admin'

c.execute('''
    INSERT INTO user (username, password, role, company_id, created_at)
    VALUES (?, ?, ?, ?, ?)
''', (username, password, role, company_id, datetime.now()))
conn.commit()

print('✅ Account created successfully!')
print(f'\nLogin Details:')
print(f'Company: {company_name}')
print(f'Username: {username}')
print(f'Password: {password}')

conn.close()
