import subprocess
import sqlite3
import bcrypt

print("Installing dependencies...")
subprocess.run("pip install -r requirements.txt", shell=True)

print("Setting up admin user...")

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'worker',
    company_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
""")

cursor.execute("DELETE FROM user")
cursor.execute("INSERT INTO user (username, password, role) VALUES ('admin', 'admin123', 'admin')")

conn.commit()
conn.close()

print("Admin user created")
print("username: admin")
print("password: admin123")

print("Starting backend server...")
subprocess.run("python app.py", shell=True)