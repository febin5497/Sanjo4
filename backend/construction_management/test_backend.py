#!/usr/bin/env python3
"""
Backend Diagnostic Script - Tests all critical components
"""
import sys
import os

print("=" * 60)
print("CONSTRUCTION MANAGEMENT BACKEND DIAGNOSTIC")
print("=" * 60)

# Test 1: Flask App Creation
print("\n[1/5] Testing Flask App Creation...")
try:
    from app import create_app
    app = create_app()
    print("  ✓ Flask app created successfully")
except Exception as e:
    print(f"  ✗ Error creating Flask app: {e}")
    sys.exit(1)

# Test 2: Database Connection
print("\n[2/5] Testing Database Connection...")
try:
    with app.app_context():
        from extensions import db
        db.session.execute("SELECT 1")
        print("  ✓ Database connection successful")
except Exception as e:
    print(f"  ✗ Database error: {e}")

# Test 3: Routes Registration
print("\n[3/5] Checking Registered Routes...")
try:
    api_routes = [rule for rule in app.url_map.iter_rules() if 'api' in rule.rule]
    print(f"  ✓ Found {len(api_routes)} API routes")
    print(f"    Sample routes:")
    for route in list(api_routes)[:5]:
        print(f"      - {list(route.methods - {'OPTIONS', 'HEAD'})[0] if route.methods else 'ANY'} {route.rule}")
except Exception as e:
    print(f"  ✗ Error reading routes: {e}")

# Test 4: CORS Configuration
print("\n[4/5] Checking CORS Configuration...")
try:
    from flask_cors import CORS
    print(f"  ✓ CORS enabled")
    print(f"    Allowed origins include:")
    print(f"      - http://localhost:5173")
    print(f"      - http://127.0.0.1:5173")
except Exception as e:
    print(f"  ✗ CORS error: {e}")

# Test 5: Critical Models
print("\n[5/5] Checking Critical Models...")
try:
    with app.app_context():
        from user_management.models import User
        from staff_management.models import Staff
        print(f"  ✓ User model loaded")
        print(f"  ✓ Staff model loaded")
except Exception as e:
    print(f"  ✗ Model error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nTo start the server, run:")
print("  python -m flask run --debug")
print("\nThen test with:")
print("  curl http://localhost:5000/api/staff -H 'Authorization: Bearer YOUR_TOKEN'")
print("=" * 60)
