import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

print('Companies table columns:')
c.execute('PRAGMA table_info(companies)')
columns = c.fetchall()
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

conn.close()
