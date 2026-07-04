"""
Pytest Configuration & Fixtures
Central fixture configuration for all backend tests
"""

import os
import sys
import pytest
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load test environment
load_dotenv('.env.test')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from user_management.models import User
from company_settings.models import Company


# ============================================================================
# APP & DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope='session')
def app():
    """Create Flask app for testing"""
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'sqlite:///tests.db'

    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-only'
    app.config['WTF_CSRF_ENABLED'] = False

    return app


@pytest.fixture(scope='function')
def client(app):
    """Create test client for each test"""
    with app.app_context():
        # Create all tables
        db.create_all()
        yield app.test_client()
        # Cleanup after test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI runner for each test"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Get database session"""
    with app.app_context():
        yield db.session


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_company(db_session):
    """Create a test company"""
    company = Company(
        name='Test Construction Co',
        address='Main Street, Test City',
        phone='1234567890',
        email='company@test.com',
        gst_number='TEST123'
    )
    db_session.add(company)
    db_session.commit()
    return company


@pytest.fixture
def admin_user(db_session, test_company):
    """Create admin test user"""
    user = User(
        username='admin',
        email='admin@test.com',
        company_id=test_company.id,
        role='admin'
    )
    user.set_password('Admin@123')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def regular_user(db_session, test_company):
    """Create regular test user"""
    user = User(
        username='testuser',
        email='user@test.com',
        company_id=test_company.id,
        role='worker'
    )
    user.set_password('Test@1234')
    db_session.add(user)
    db_session.commit()
    return user


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'Admin@123'
    })

    if response.status_code == 200:
        return response.get_json().get('access_token')
    else:
        pytest.skip('Could not get admin token')


@pytest.fixture
def user_token(client, regular_user):
    """Get JWT token for regular user"""
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'Test@1234'
    })

    if response.status_code == 200:
        return response.get_json().get('access_token')
    else:
        pytest.skip('Could not get user token')


@pytest.fixture
def admin_headers(admin_token):
    """Get headers with admin token"""
    return {'Authorization': f'Bearer {admin_token}'}


@pytest.fixture
def user_headers(user_token):
    """Get headers with regular user token"""
    return {'Authorization': f'Bearer {user_token}'}


# ============================================================================
# TEST DATA FACTORIES - STAFF
# ============================================================================

@pytest.fixture
def create_staff(client, admin_headers, test_company):
    """Factory to create staff members"""
    staff_counter = 0

    def _create_staff(name='Test Staff', role='Laborer', salary=30000, **kwargs):
        nonlocal staff_counter
        staff_counter += 1

        payload = {
            'name': name + str(staff_counter),
            'email': f'staff{staff_counter}@test.com',
            'phone': f'999{staff_counter:06d}',
            'role': role,
            'joining_date': '2026-01-01',
            'salary': salary,
            'pf': 12,
            'esi': 0.75,
            **kwargs
        }

        response = client.post('/api/staff',
                              json=payload,
                              headers=admin_headers)

        if response.status_code == 201:
            return response.get_json().get('data')
        return None

    return _create_staff


@pytest.fixture
def sample_staff_list(create_staff):
    """Create 5 sample staff members"""
    staff = []
    roles = ['Engineer', 'Manager', 'Foreman', 'Laborer', 'Safety Officer']

    for i, role in enumerate(roles):
        staff_data = create_staff(
            name=f'Staff {i+1}',
            role=role,
            salary=25000 + (i * 5000)
        )
        if staff_data:
            staff.append(staff_data)

    return staff


# ============================================================================
# TEST DATA FACTORIES - ATTENDANCE
# ============================================================================

@pytest.fixture
def create_attendance(client, admin_headers):
    """Factory to create attendance records"""
    attendance_counter = 0

    def _create_attendance(staff_id, date=None, present=True, **kwargs):
        nonlocal attendance_counter
        attendance_counter += 1

        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        payload = {
            'staff_id': staff_id,
            'date': date,
            'present': present,
            'half_day': False,
            'night_shift': False,
            'overtime_hours': 0,
            **kwargs
        }

        response = client.post('/api/attendance',
                              json=payload,
                              headers=admin_headers)

        if response.status_code == 201:
            return response.get_json().get('data')
        return None

    return _create_attendance


@pytest.fixture
def sample_attendance(create_attendance, sample_staff_list):
    """Create sample attendance records"""
    attendance = []

    for staff_id_obj in sample_staff_list[:2]:  # Use first 2 staff
        staff_id = staff_id_obj.get('id') if isinstance(staff_id_obj, dict) else staff_id_obj

        for i in range(5):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            present = i % 2 == 0  # Alternate present/absent

            record = create_attendance(staff_id, date, present)
            if record:
                attendance.append(record)

    return attendance


# ============================================================================
# TEST DATA FACTORIES - VEHICLES
# ============================================================================

@pytest.fixture
def create_vehicle(client, admin_headers, test_company):
    """Factory to create vehicles"""
    vehicle_counter = 0

    def _create_vehicle(registration=None, model='Test Vehicle', **kwargs):
        nonlocal vehicle_counter
        vehicle_counter += 1

        if registration is None:
            registration = f'TEST{vehicle_counter:04d}'

        payload = {
            'registration_number': registration,
            'model': model,
            'type': 'Truck',
            'year': 2023,
            'capacity': 10000,
            'company_id': test_company.id,
            **kwargs
        }

        response = client.post('/api/vehicles',
                              json=payload,
                              headers=admin_headers)

        if response.status_code == 201:
            return response.get_json().get('data')
        return None

    return _create_vehicle


@pytest.fixture
def sample_vehicle(create_vehicle):
    """Create a sample vehicle"""
    return create_vehicle()


# ============================================================================
# TEST DATA FACTORIES - PROJECTS
# ============================================================================

@pytest.fixture
def create_project(client, admin_headers, test_company):
    """Factory to create projects"""
    project_counter = 0

    def _create_project(name=None, location='Test Site', **kwargs):
        nonlocal project_counter
        project_counter += 1

        if name is None:
            name = f'Test Project {project_counter}'

        start_date = datetime.now()
        end_date = start_date + timedelta(days=90)

        payload = {
            'name': name,
            'location': location,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'area': 5000,
            'rate_per_sqft': 2500,
            'status': 'Planned',
            'company_id': test_company.id,
            **kwargs
        }

        response = client.post('/api/projects',
                              json=payload,
                              headers=admin_headers)

        if response.status_code == 201:
            return response.get_json().get('data')
        return None

    return _create_project


@pytest.fixture
def sample_project(create_project):
    """Create a sample project"""
    return create_project()


@pytest.fixture
def sample_projects(create_project):
    """Create multiple sample projects"""
    projects = []
    for i in range(3):
        project = create_project(name=f'Project {i+1}')
        if project:
            projects.append(project)
    return projects


# ============================================================================
# TEST DATA FACTORIES - EXPENSES
# ============================================================================

@pytest.fixture
def create_expense(client, admin_headers, sample_project):
    """Factory to create expenses"""
    expense_counter = 0

    def _create_expense(category='Materials', amount=5000, **kwargs):
        nonlocal expense_counter
        expense_counter += 1

        if not sample_project:
            return None

        project_id = sample_project.get('id') if isinstance(sample_project, dict) else sample_project

        payload = {
            'project_id': project_id,
            'category': category,
            'description': f'Expense {expense_counter}',
            'amount': amount,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'vendor_name': 'Test Vendor',
            'payment_method': 'Cheque',
            **kwargs
        }

        response = client.post('/api/expense',
                              json=payload,
                              headers=admin_headers)

        if response.status_code in [200, 201]:
            return response.get_json().get('data') or response.get_json()
        return None

    return _create_expense


@pytest.fixture
def sample_expense(create_expense):
    """Create a sample expense"""
    expense = create_expense()
    if expense and isinstance(expense, dict):
        return expense
    return {'id': 1, 'category': 'Materials', 'amount': 5000}


# ============================================================================
# TEST DATA FACTORIES - STAFF (Additional)
# ============================================================================

@pytest.fixture
def sample_staff(sample_staff_list):
    """Get sample staff (already created by sample_staff_list)"""
    if sample_staff_list:
        return sample_staff_list
    return [{'id': 1, 'name': 'Test Staff', 'role': 'Engineer'}]


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def json_headers():
    """Headers for JSON API requests"""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture
def fake_email():
    """Generate fake email"""
    import random
    return f'test{random.randint(1000, 9999)}@test.com'


@pytest.fixture
def fake_phone():
    """Generate fake phone number"""
    import random
    return f'999{random.randint(100000, 999999)}'


# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line('markers', 'smoke: Mark test as smoke test')
    config.addinivalue_line('markers', 'integration: Mark test as integration test')


@pytest.fixture(autouse=True)
def reset_db(app):
    """Reset database before each test"""
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


# ============================================================================
# PYTEST OUTPUT
# ============================================================================

@pytest.fixture(scope='session', autouse=True)
def print_test_info():
    """Print test configuration info"""
    print('\n' + '='*70)
    print('TEST ENVIRONMENT CONFIGURATION')
    print('='*70)
    print(f'Environment: {os.environ.get("FLASK_ENV", "development")}')
    print(f'Testing: {os.environ.get("TESTING", False)}')
    print(f'Database: {os.environ.get("DATABASE_URL", "sqlite:///tests.db")}')
    print('='*70 + '\n')

    yield
