import sqlite3
import os

db_path = "data.db"

# List of tables to clear (in order to respect foreign keys)
tables_to_clear = [
    'project_staff_history',
    'project_assignment',
    'site_photo',
    'project_cost',
    'attendance',
    'salary_record',
    'vehicle',
    'material',
    'invoice_item',
    'invoice',
    'cash_transaction',
    'project',
    'staff',
    'client',
    'user',
    'company',
]

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Disable foreign key constraints temporarily
    cursor.execute('PRAGMA foreign_keys = OFF')
    
    for table in tables_to_clear:
        try:
            cursor.execute(f'DELETE FROM {table}')
            print(f"[OK] Cleared {table}")
        except Exception as e:
            print(f"[ERR] Error clearing {table}: {e}")
    
    # Re-enable foreign key constraints
    cursor.execute('PRAGMA foreign_keys = ON')
    
    conn.commit()
    conn.close()
    
    print("\n[DONE] Database cleared successfully!")
    
except Exception as e:
    print(f"[ERR] Error: {e}")
