import sqlite3, bcrypt
conn = sqlite3.connect('D:\\Projects\\backend\\construction_management\\data.db')
c = conn.cursor()

# Check admin_test password
r = c.execute('SELECT username, password FROM user WHERE username="admin_test"').fetchone()
if r:
    print(f'Testing passwords for {r[0]}:')
    for pw in ['admin_test', 'Admin@123', 'password', 'admin123', 'test123']:
        try:
            ok = bcrypt.checkpw(pw.encode(), r[1].encode())
            if ok: print(f'  ✓ PASSWORD IS: {pw}')
        except: pass
    
# Also try common passwords for other test users
for user in ['manager_test', 'engineer_test', 'hr_test', 'driver_test', 'staffone', 'admin']:
    r2 = c.execute('SELECT password FROM user WHERE username=?', (user,)).fetchone()
    if r2:
        for pw in [user, 'password', 'admin123', 'password123', 'test123']:
            try:
                if bcrypt.checkpw(pw.encode(), r2[1].encode()):
                    print(f'{user} / {pw} ✓ WORKS')
            except: pass

# Create a fresh test user if needed
from werkzeug.security import generate_password_hash
pw_hash = generate_password_hash('test123')
try:
    c.execute('INSERT OR IGNORE INTO user (username, password, role, company_id, is_active) VALUES (?,?,?,?,?)',
              ('testuser123', pw_hash, 'admin', 1, 1))
    conn.commit()
    print('\nCreated testuser123 / test123')
except: pass

conn.close()
