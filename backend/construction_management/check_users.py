import sqlite3
conn = sqlite3.connect('D:\\Projects\\backend\\construction_management\\data.db')
c = conn.cursor()
tables = [t[0] for t in c.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()]
print('Tables:', tables)
for t in tables:
    if 'user' in t.lower():
        print(f'\n=== {t} ===')
        cols = [col[1] for col in c.execute(f'PRAGMA table_info({t})').fetchall()]
        print('Columns:', cols)
        rows = c.execute(f'SELECT * FROM {t}').fetchall()
        for r in rows[:20]:
            print(r)
conn.close()
