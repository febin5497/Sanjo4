#!/usr/bin/env python
"""Simple database initialization"""
import sys
from app import app, db
from user_management.models import User
from datetime import datetime

print("[*] Initializing database...")

with app.app_context():
    # Create all tables
    db.create_all()
    print("[OK] Database schema created")

    # Create admin user
    admin = User(
        username='admin',
        role='admin',
        is_active=True
    )
    admin.set_password('Test@1234')
    db.session.add(admin)
    db.session.commit()
    print("[OK] Admin user created")
    print("\n[DONE] Database initialization completed!")
    print("\nLogin Credentials:")
    print("  Username: admin")
    print("  Password: Test@1234")
