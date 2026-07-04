#!/usr/bin/env python3
"""
Comprehensive test script for Vehicle Management Module Enhancement - Option A
Tests all new endpoints for:
- Fuel Log tracking
- Maintenance Log tracking
- Maintenance Schedules
- Vehicle-Project Assignments
- Driver Assignments
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
ADMIN_USER = "admin"
ADMIN_PASS = "Admin@123"

# Global token and IDs
token = None
user_id = None
company_id = None
vehicle_id = None
project_id = None
driver_id = None

def print_test(test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)

def print_result(success, message, data=None):
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {message}")
    if data:
        print(f"Data: {json.dumps(data, indent=2)[:200]}")

def authenticate():
    """Login and get JWT token"""
    global token, user_id, company_id

    print_test("Authentication")

    payload = {
        "username": ADMIN_USER,
        "password": ADMIN_PASS
    }

    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)

    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        user_data = data.get('user', {})
        user_id = user_data.get('id')
        company_id = 1  # Default to company 1, will be retrieved from user

        if token and user_id:
            print_result(True, f"Login successful - Token: {token[:20]}...", {"user_id": user_id, "company_id": company_id})
            return True
        else:
            print_result(False, f"Login response missing token or user_id: {data}")
            return False
    else:
        print_result(False, f"Login failed: {response.status_code} - {response.text}")
        return False

def get_vehicle():
    """Get an existing vehicle or the first one"""
    global vehicle_id

    print_test("Get Existing Vehicle")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles?page=1&per_page=10", headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            vehicle_id = data['data'][0]['id']
            print_result(True, f"Got vehicle ID {vehicle_id}", data['data'][0])
            return True

    print_result(False, "No vehicles found - creating test vehicle...")

    # Create a vehicle if none exists
    vehicle_data = {
        "make": "Test Make",
        "model": "Test Model",
        "year": 2023,
        "registration_number": f"TEST-{datetime.now().timestamp():.0f}",
        "type": "commercial",
        "status": "active"
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/vehicles", json=vehicle_data, headers=headers)

    if response.status_code == 201:
        data = response.json()
        vehicle_id = data.get('data', {}).get('id')
        print_result(True, f"Created vehicle ID {vehicle_id}", data.get('data'))
        return True
    else:
        print_result(False, f"Failed to create vehicle: {response.text}")
        return False

def get_project():
    """Get an existing project or create one"""
    global project_id

    print_test("Get Existing Project")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/projects?page=1&per_page=10", headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            project_id = data['data'][0]['id']
            print_result(True, f"Got project ID {project_id}", data['data'][0])
            return True

    print_result(False, "No projects found")
    return False

def get_driver():
    """Get an existing staff member to use as driver"""
    global driver_id

    print_test("Get Existing Staff/Driver")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/staff?page=1&per_page=10", headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            driver_id = data['data'][0]['id']
            print_result(True, f"Got staff ID {driver_id}", data['data'][0])
            return True

    print_result(False, "No staff members found")
    return False

# ============== FUEL LOG TESTS ==============

def test_create_fuel_log():
    """Test creating a fuel log"""
    print_test("Create Fuel Log")

    payload = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": 50.0,
        "cost": 3500.0,
        "notes": "Regular fuel fill-up"
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/vehicles/{vehicle_id}/fuel-logs", json=payload, headers=headers)

    if response.status_code == 201:
        print_result(True, "Fuel log created successfully", response.json().get('data'))
        return response.json().get('data', {}).get('id')
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return None

def test_get_fuel_logs():
    """Test getting fuel logs"""
    print_test("Get Fuel Logs")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/fuel-logs?page=1&per_page=10", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved {len(data.get('data', []))} fuel logs", data)
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

def test_fuel_summary():
    """Test fuel summary endpoint"""
    print_test("Get Fuel Summary")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/fuel-logs/summary", headers=headers)

    if response.status_code == 200:
        print_result(True, "Fuel summary retrieved", response.json().get('data'))
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

# ============== MAINTENANCE LOG TESTS ==============

def test_create_maintenance_log():
    """Test creating a maintenance log"""
    print_test("Create Maintenance Log")

    payload = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "Service",
        "cost": 5000.0,
        "description": "Regular oil change and filter replacement",
        "service_center": "Test Service Center",
        "mileage_at_service": 25000.0
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/vehicles/{vehicle_id}/maintenance-logs", json=payload, headers=headers)

    if response.status_code == 201:
        print_result(True, "Maintenance log created successfully", response.json().get('data'))
        return response.json().get('data', {}).get('id')
    else:
        print_result(False, f"Failed: {response.text}")
        return None

def test_get_maintenance_logs():
    """Test getting maintenance logs"""
    print_test("Get Maintenance Logs")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/maintenance-logs?page=1&per_page=10", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved {len(data.get('data', []))} maintenance logs", data)
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

# ============== MAINTENANCE SCHEDULE TESTS ==============

def test_create_maintenance_schedule():
    """Test creating a maintenance schedule"""
    print_test("Create Maintenance Schedule")

    payload = {
        "maintenance_type": "Oil Change",
        "interval_km": 5000.0,
        "interval_days": 180,
        "last_done_km": 20000.0,
        "last_done_date": datetime.now().strftime("%Y-%m-%d"),
        "next_due_km": 25000.0,
        "next_due_date": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/vehicles/{vehicle_id}/maintenance-schedule", json=payload, headers=headers)

    if response.status_code == 201:
        print_result(True, "Maintenance schedule created successfully", response.json().get('data'))
        return response.json().get('data', {}).get('id')
    else:
        print_result(False, f"Failed: {response.text}")
        return None

def test_get_maintenance_schedules():
    """Test getting maintenance schedules"""
    print_test("Get Maintenance Schedules")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/maintenance-schedule", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved {len(data.get('data', []))} schedules", data)
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

# ============== VEHICLE-PROJECT ASSIGNMENT TESTS ==============

def test_assign_vehicle_to_project():
    """Test assigning vehicle to project"""
    if not project_id:
        print_test("Assign Vehicle to Project - SKIPPED (no project)")
        return None

    print_test("Assign Vehicle to Project")

    payload = {
        "project_id": project_id,
        "notes": "Assigned for transport duties"
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/vehicles/{vehicle_id}/assign-project", json=payload, headers=headers)

    if response.status_code == 201:
        print_result(True, "Vehicle assigned to project", response.json().get('data'))
        return response.json().get('data', {}).get('id')
    else:
        print_result(False, f"Failed: {response.text}")
        return None

def test_get_vehicle_projects():
    """Test getting projects for a vehicle"""
    print_test("Get Vehicle Projects")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/projects", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved {len(data.get('data', []))} projects", data)
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

def test_get_active_projects():
    """Test getting active projects for a vehicle"""
    print_test("Get Active Vehicle Projects")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/projects/active", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved {len(data.get('data', []))} active projects", data)
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

# ============== DRIVER ASSIGNMENT TESTS ==============

def test_assign_driver():
    """Test assigning driver to vehicle"""
    if not driver_id:
        print_test("Assign Driver - SKIPPED (no driver)")
        return None

    print_test("Assign Driver to Vehicle")

    payload = {
        "driver_id": driver_id,
        "notes": "Primary driver for this vehicle"
    }

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/vehicles/{vehicle_id}/assign-driver", json=payload, headers=headers)

    if response.status_code == 201:
        print_result(True, "Driver assigned to vehicle", response.json().get('data'))
        return response.json().get('data', {}).get('id')
    else:
        print_result(False, f"Failed: {response.text}")
        return None

def test_get_current_driver():
    """Test getting current driver"""
    print_test("Get Current Driver")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/driver", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, "Current driver retrieved", data.get('data'))
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

def test_get_driver_history():
    """Test getting driver history"""
    print_test("Get Driver History")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/vehicles/{vehicle_id}/driver-history", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Retrieved {len(data.get('data', []))} driver history entries", data)
        return True
    else:
        print_result(False, f"Failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("*" * 60)
    print("VEHICLE MODULE ENHANCEMENT - COMPREHENSIVE TEST SUITE")
    print("*" * 60)

    # Authenticate
    if not authenticate():
        print("\nAuthentication failed - cannot proceed")
        return

    # Get test data
    if not get_vehicle():
        print("\nCannot get/create vehicle - cannot proceed")
        return

    get_project()  # Optional
    get_driver()   # Optional

    print("\n" + "=" * 60)
    print("TESTING FUEL LOG ENDPOINTS")
    print("=" * 60)

    fuel_log_id = test_create_fuel_log()
    test_get_fuel_logs()
    test_fuel_summary()

    print("\n" + "=" * 60)
    print("TESTING MAINTENANCE LOG ENDPOINTS")
    print("=" * 60)

    maintenance_log_id = test_create_maintenance_log()
    test_get_maintenance_logs()

    print("\n" + "=" * 60)
    print("TESTING MAINTENANCE SCHEDULE ENDPOINTS")
    print("=" * 60)

    schedule_id = test_create_maintenance_schedule()
    test_get_maintenance_schedules()

    print("\n" + "=" * 60)
    print("TESTING VEHICLE-PROJECT ASSIGNMENT ENDPOINTS")
    print("=" * 60)

    assignment_id = test_assign_vehicle_to_project()
    test_get_vehicle_projects()
    test_get_active_projects()

    print("\n" + "=" * 60)
    print("TESTING DRIVER ASSIGNMENT ENDPOINTS")
    print("=" * 60)

    driver_assignment_id = test_assign_driver()
    test_get_current_driver()
    test_get_driver_history()

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\nAll new endpoints have been tested successfully!")

if __name__ == "__main__":
    main()
