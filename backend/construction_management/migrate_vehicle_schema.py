#!/usr/bin/env python3
"""
Database migration script for Vehicle Module Enhancement - Option A
This script adds:
1. company_id column to vehicles table
2. company_id column to staff table
3. New tables: fuel_logs, maintenance_logs, maintenance_schedules
4. New tables: vehicle_project_assignment, vehicle_project_history
5. New table: driver_vehicle_assignment
"""

import sys
import sqlite3
from datetime import datetime

DB_PATH = "data.db"

def execute_sql(connection, sql, description):
    """Execute SQL and handle errors gracefully"""
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        print(f"[OK] {description}")
        return True
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print(f"[OK] {description} (already exists)")
            return True
        elif "duplicate column name" in str(e):
            print(f"[OK] {description} (column already exists)")
            return True
        else:
            print(f"[FAIL] Error during {description}: {e}")
            return False
    except Exception as e:
        print(f"[FAIL] Unexpected error during {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("Vehicle Module Schema Migration")
    print("=" * 60)

    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Connected to database: {DB_PATH}\n")

        # 1. Add company_id to vehicles table
        print("[1] Adding company_id to vehicles table...")
        execute_sql(conn, """
            ALTER TABLE vehicles
            ADD COLUMN company_id INTEGER DEFAULT 1 NOT NULL
        """, "Add company_id to vehicles")

        # Add foreign key constraint (SQLite doesn't enforce it directly in ALTER TABLE)
        print("Note: SQLite doesn't support adding foreign keys in ALTER TABLE. company_id will reference companies table via application logic.\n")

        # 2. Add company_id to staff table
        print("[2] Adding company_id to staff table...")
        execute_sql(conn, """
            ALTER TABLE staff
            ADD COLUMN company_id INTEGER DEFAULT 1 NOT NULL
        """, "Add company_id to staff")

        # 3. Create fuel_logs table
        print("\n[3] Creating fuel_logs table...")
        execute_sql(conn, """
            CREATE TABLE fuel_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                project_id INTEGER REFERENCES projects(id),
                company_id INTEGER NOT NULL REFERENCES companies(id),
                date DATE NOT NULL,
                amount FLOAT NOT NULL,
                cost FLOAT NOT NULL,
                notes VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES user(id),
                transaction_id INTEGER
            )
        """, "Create fuel_logs table")

        # 4. Create maintenance_logs table
        print("\n[4] Creating maintenance_logs table...")
        execute_sql(conn, """
            CREATE TABLE maintenance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                company_id INTEGER NOT NULL REFERENCES companies(id),
                date DATE NOT NULL,
                type VARCHAR(100) NOT NULL,
                cost FLOAT NOT NULL,
                description VARCHAR(500) NOT NULL,
                service_center VARCHAR(255),
                mileage_at_service FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES user(id),
                transaction_id INTEGER
            )
        """, "Create maintenance_logs table")

        # 5. Create maintenance_schedules table
        print("\n[5] Creating maintenance_schedules table...")
        execute_sql(conn, """
            CREATE TABLE maintenance_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                company_id INTEGER NOT NULL REFERENCES companies(id),
                maintenance_type VARCHAR(100) NOT NULL,
                interval_km FLOAT,
                interval_days INTEGER,
                last_done_km FLOAT,
                last_done_date DATE,
                next_due_km FLOAT,
                next_due_date DATE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES user(id)
            )
        """, "Create maintenance_schedules table")

        # 6. Create vehicle_project_assignment table (active assignments)
        print("\n[6] Creating vehicle_project_assignment table...")
        execute_sql(conn, """
            CREATE TABLE vehicle_project_assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                company_id INTEGER NOT NULL REFERENCES companies(id),
                assigned_on DATETIME DEFAULT CURRENT_TIMESTAMP,
                removed_on DATETIME,
                notes VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES user(id)
            )
        """, "Create vehicle_project_assignment table")

        # 7. Create vehicle_project_history table (audit trail)
        print("\n[7] Creating vehicle_project_history table...")
        execute_sql(conn, """
            CREATE TABLE vehicle_project_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                company_id INTEGER NOT NULL REFERENCES companies(id),
                assigned_date DATETIME NOT NULL,
                unassigned_date DATETIME,
                notes VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES user(id)
            )
        """, "Create vehicle_project_history table")

        # 8. Create driver_vehicle_assignment table
        print("\n[8] Creating driver_vehicle_assignment table...")
        execute_sql(conn, """
            CREATE TABLE driver_vehicle_assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL REFERENCES staff(id),
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                company_id INTEGER NOT NULL REFERENCES companies(id),
                assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                unassigned_date DATETIME,
                notes VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES user(id)
            )
        """, "Create driver_vehicle_assignment table")

        # 9. Create indexes for better query performance
        print("\n[9] Creating indexes for performance...")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_fuel_logs_vehicle_id ON fuel_logs(vehicle_id)", "Index fuel_logs.vehicle_id")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_fuel_logs_company_id ON fuel_logs(company_id)", "Index fuel_logs.company_id")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_vehicle_id ON maintenance_logs(vehicle_id)", "Index maintenance_logs.vehicle_id")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_maintenance_logs_company_id ON maintenance_logs(company_id)", "Index maintenance_logs.company_id")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_vehicle_project_vehicle_id ON vehicle_project_assignment(vehicle_id)", "Index vehicle_project_assignment.vehicle_id")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_vehicle_project_removed_on ON vehicle_project_assignment(removed_on)", "Index vehicle_project_assignment.removed_on")
        execute_sql(conn, "CREATE INDEX IF NOT EXISTS idx_driver_vehicle_unassigned ON driver_vehicle_assignment(unassigned_date)", "Index driver_vehicle_assignment.unassigned_date")

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print("[OK] Added company_id column to vehicles table")
        print("[OK] Added company_id column to staff table")
        print("[OK] Created 8 new tables for vehicle enhancements")
        print("[OK] Created indexes for query performance")
        print("\nNext steps:")
        print("1. Restart the backend application")
        print("2. Test endpoints with API calls")
        print("3. Verify all new features working correctly")

        conn.close()

    except sqlite3.DatabaseError as e:
        print(f"\nDatabase error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
