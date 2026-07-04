"""
API Endpoint Tests for Task Management
Tests all CRUD operations and staff assignment endpoints
"""

import pytest
import json
from datetime import date, timedelta
from app import create_app
from extensions import db, bcrypt
from project_management.models.task_model import ProjectTask
from project_management.models.task_assignment import TaskStaffAssignment
from project_management.models.models import Project
from staff_management.models import Staff
from user_management.models import User
from company_settings.models import Company


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_token(app, client):
    """Create authenticated user and return JWT token"""
    with app.app_context():
        company = Company(company_name="Test Company", registration_number="TC001")
        db.session.add(company)
        db.session.commit()

        user = User(
            username="testuser",
            email="test@example.com",
            company_id=company.id,
            role="admin",
            password_hash=bcrypt.generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()

        # Create a simple token for testing (in real scenario, would use login endpoint)
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=user.id)

        return {
            'token': token,
            'user_id': user.id,
            'company_id': company.id
        }


@pytest.fixture
def setup_test_data(app, auth_token):
    """Create test data for endpoints"""
    with app.app_context():
        company_id = auth_token['company_id']

        # Create project
        project = Project(
            project_name="Test Project",
            company_id=company_id,
            status="Active",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        db.session.add(project)
        db.session.commit()

        # Create staff
        staff1 = Staff(
            first_name="John",
            last_name="Doe",
            role="Developer",
            company_id=company_id,
            personal_email="john@example.com"
        )
        staff2 = Staff(
            first_name="Jane",
            last_name="Smith",
            role="Manager",
            company_id=company_id,
            personal_email="jane@example.com"
        )
        db.session.add_all([staff1, staff2])
        db.session.commit()

        return {
            'project_id': project.id,
            'company_id': company_id,
            'staff1_id': staff1.id,
            'staff2_id': staff2.id,
            'user_id': auth_token['user_id']
        }


class TestTaskCRUDEndpoints:
    """Tests for task CRUD operations"""

    def test_get_tasks_list(self, client, auth_token, setup_test_data):
        """Test GET /api/projects/<id>/tasks"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']

        response = client.get(
            f'/api/projects/{project_id}/tasks',
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_create_task(self, client, auth_token, setup_test_data):
        """Test POST /api/projects/<id>/tasks"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        task_data = {
            'task_name': 'Build API',
            'description': 'Create REST API endpoints',
            'task_type': 'Activity',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=5)).isoformat(),
            'status': 'todo',
            'progress': 0,
            'priority': 'high',
            'company_id': company_id
        }

        response = client.post(
            f'/api/projects/{project_id}/tasks',
            json=task_data,
            headers=headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['task_name'] == 'Build API'
        assert data['data']['status'] == 'todo'

    def test_create_task_missing_required_field(self, client, auth_token, setup_test_data):
        """Test POST with missing required fields"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']

        # Missing task_name
        task_data = {
            'description': 'No name',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=1)).isoformat()
        }

        response = client.post(
            f'/api/projects/{project_id}/tasks',
            json=task_data,
            headers=headers
        )

        assert response.status_code == 400

    def test_create_task_invalid_dates(self, client, auth_token, setup_test_data):
        """Test POST with end_date before start_date"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        task_data = {
            'task_name': 'Invalid Task',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() - timedelta(days=1)).isoformat(),
            'company_id': company_id
        }

        response = client.post(
            f'/api/projects/{project_id}/tasks',
            json=task_data,
            headers=headers
        )

        assert response.status_code == 400

    def test_get_task_detail(self, app, client, auth_token, setup_test_data):
        """Test GET /api/projects/<id>/tasks/<task_id>"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        # Create a task first
        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test Task",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1),
                status="todo"
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.get(
            f'/api/projects/{project_id}/tasks/{task_id}',
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['task_name'] == "Test Task"

    def test_get_nonexistent_task(self, client, auth_token, setup_test_data):
        """Test GET for non-existent task"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']

        response = client.get(
            f'/api/projects/{project_id}/tasks/99999',
            headers=headers
        )

        assert response.status_code == 404

    def test_update_task(self, app, client, auth_token, setup_test_data):
        """Test PUT /api/projects/<id>/tasks/<task_id>"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        # Create a task first
        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Original Name",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1),
                status="todo"
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Update the task
        update_data = {
            'task_name': 'Updated Name',
            'status': 'in-progress',
            'progress': 50
        }

        response = client.put(
            f'/api/projects/{project_id}/tasks/{task_id}',
            json=update_data,
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['task_name'] == 'Updated Name'
        assert data['data']['status'] == 'in-progress'
        assert data['data']['progress'] == 50

    def test_delete_task(self, app, client, auth_token, setup_test_data):
        """Test DELETE /api/projects/<id>/tasks/<task_id>"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        # Create a task first
        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="To Delete",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Delete the task
        response = client.delete(
            f'/api/projects/{project_id}/tasks/{task_id}',
            headers=headers
        )

        assert response.status_code == 200

        # Verify deletion
        with app.app_context():
            deleted_task = ProjectTask.query.get(task_id)
            assert deleted_task is None


class TestTaskStaffAssignmentEndpoints:
    """Tests for staff assignment endpoints"""

    def test_assign_staff_to_task(self, app, client, auth_token, setup_test_data):
        """Test POST /api/projects/<id>/tasks/<task_id>/assign-staff"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']
        staff_id = setup_test_data['staff1_id']

        # Create a task first
        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test Task",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        # Assign staff
        assignment_data = {
            'staff_id': staff_id,
            'role_on_task': 'Lead',
            'hours_allocated': 40
        }

        response = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/assign-staff',
            json=assignment_data,
            headers=headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['data']['staff_id'] == staff_id

    def test_assign_staff_missing_staff_id(self, app, client, auth_token, setup_test_data):
        """Test POST without staff_id"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/assign-staff',
            json={},
            headers=headers
        )

        assert response.status_code == 400

    def test_assign_staff_duplicate(self, app, client, auth_token, setup_test_data):
        """Test assigning same staff twice"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']
        staff_id = setup_test_data['staff1_id']

        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        assignment_data = {'staff_id': staff_id}

        # First assignment should succeed
        response1 = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/assign-staff',
            json=assignment_data,
            headers=headers
        )
        assert response1.status_code == 201

        # Second assignment should fail
        response2 = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/assign-staff',
            json=assignment_data,
            headers=headers
        )
        assert response2.status_code == 400

    def test_unassign_staff_from_task(self, app, client, auth_token, setup_test_data):
        """Test POST /api/projects/<id>/tasks/<task_id>/unassign-staff"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']
        staff_id = setup_test_data['staff1_id']
        user_id = setup_test_data['user_id']

        # Create task and assignment
        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=staff_id,
                company_id=company_id,
                assigned_by_user_id=user_id
            )
            db.session.add(assignment)
            db.session.commit()
            task_id = task.id

        # Unassign
        response = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/unassign-staff',
            json={'staff_id': staff_id},
            headers=headers
        )

        assert response.status_code == 200

    def test_get_task_staff(self, app, client, auth_token, setup_test_data):
        """Test GET /api/projects/<id>/tasks/<task_id>/staff"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']
        staff_id = setup_test_data['staff1_id']
        user_id = setup_test_data['user_id']

        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()

            assignment = TaskStaffAssignment(
                task_id=task.id,
                staff_id=staff_id,
                company_id=company_id,
                assigned_by_user_id=user_id
            )
            db.session.add(assignment)
            db.session.commit()
            task_id = task.id

        response = client.get(
            f'/api/projects/{project_id}/tasks/{task_id}/staff',
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data['data'], list)
        assert len(data['data']) == 1

    def test_bulk_assign_staff(self, app, client, auth_token, setup_test_data):
        """Test POST /api/projects/<id>/tasks/<task_id>/bulk-assign"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']
        staff_ids = [setup_test_data['staff1_id'], setup_test_data['staff2_id']]

        with app.app_context():
            task = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Test",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        response = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/bulk-assign',
            json={'staff_ids': staff_ids},
            headers=headers
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert len(data['data']['assigned']) == 2


class TestTaskFiltering:
    """Tests for task filtering and sorting"""

    def test_filter_by_status(self, app, client, auth_token, setup_test_data):
        """Test filtering tasks by status"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        with app.app_context():
            for status in ['todo', 'in-progress', 'done']:
                task = ProjectTask(
                    project_id=project_id,
                    company_id=company_id,
                    task_name=f"Task {status}",
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=1),
                    status=status
                )
                db.session.add(task)
            db.session.commit()

        response = client.get(
            f'/api/projects/{project_id}/tasks?status=todo',
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(t['status'] == 'todo' for t in data['data'])

    def test_sort_by_start_date(self, app, client, auth_token, setup_test_data):
        """Test sorting tasks by start date"""
        headers = {'Authorization': f'Bearer {auth_token["token"]}'}
        project_id = setup_test_data['project_id']
        company_id = setup_test_data['company_id']

        with app.app_context():
            task1 = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="First",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=1)
            )
            task2 = ProjectTask(
                project_id=project_id,
                company_id=company_id,
                task_name="Second",
                start_date=date.today() + timedelta(days=5),
                end_date=date.today() + timedelta(days=6)
            )
            db.session.add_all([task1, task2])
            db.session.commit()

        response = client.get(
            f'/api/projects/{project_id}/tasks?sort_by=start_date',
            headers=headers
        )

        assert response.status_code == 200


class TestAuthenticationAndAuthorization:
    """Tests for authentication and authorization"""

    def test_endpoint_requires_auth(self, client, setup_test_data):
        """Test that endpoints require authentication"""
        project_id = setup_test_data['project_id']

        response = client.get(f'/api/projects/{project_id}/tasks')

        assert response.status_code == 401

    def test_invalid_token(self, client, setup_test_data):
        """Test with invalid JWT token"""
        headers = {'Authorization': 'Bearer invalid_token'}
        project_id = setup_test_data['project_id']

        response = client.get(
            f'/api/projects/{project_id}/tasks',
            headers=headers
        )

        assert response.status_code == 422


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
