"""
Integration Tests for Task Management System
Tests complete workflows and data persistence
"""

import pytest
import json
from datetime import date, timedelta
from flask_jwt_extended import create_access_token
from extensions import db
from project_management.models import Project
from project_management.models.task_model import ProjectTask
from staff_management.models import Staff
from client_management.models import Client


@pytest.fixture
def setup_test_data(client, test_company, admin_user):
    """Create test project, staff, and user for testing"""
    # Create a test client
    test_client = Client(
        name='Test Client',
        email='client@test.com',
        phone='1234567890',
        address='Test Address'
    )
    db.session.add(test_client)
    db.session.flush()

    # Create a test project
    project = Project(
        name='Test Task Project',
        location='Test Location',
        company_id=test_company.id,
        start_date=date.today(),
        user_id=admin_user.id,
        client_id=test_client.id
    )
    db.session.add(project)
    db.session.flush()

    # Create test staff members
    staff_list = []
    for i in range(3):
        staff = Staff(
            first_name=f'Staff{i}',
            last_name=f'Member{i}',
            staff_id=f'STF-2026-{i:03d}',
            company_id=test_company.id,
            email=f'staff{i}@test.com',
            personal_phone='1234567890',
            role='Worker',
            joining_date=date.today()
        )
        db.session.add(staff)
        staff_list.append(staff)

    db.session.commit()

    return {
        'project': project,
        'staff': staff_list,
        'user': admin_user,
        'company': test_company
    }


class TestTaskWorkflows:
    """Integration tests for complete task workflows"""

    def test_complete_task_workflow(self, client, setup_test_data):
        """Test complete workflow: create, read, update, delete"""
        test_data = setup_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Create a task
        task_data = {
            'task_name': 'Integration Test Task',
            'description': 'Testing complete workflow',
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
        task = json.loads(response.data)['data']
        task_id = task['id']

        # 2. Read the task
        response = client.get(
            f'/api/projects/{project_id}/tasks/{task_id}',
            headers=headers
        )

        assert response.status_code == 200
        retrieved_task = json.loads(response.data)['data']
        assert retrieved_task['task_name'] == 'Integration Test Task'

        # 3. Update the task
        update_data = {
            'task_name': 'Updated Integration Task',
            'status': 'in-progress',
            'progress': 50
        }

        response = client.put(
            f'/api/projects/{project_id}/tasks/{task_id}',
            json=update_data,
            headers=headers
        )

        assert response.status_code == 200
        updated_task = json.loads(response.data)['data']
        assert updated_task['task_name'] == 'Updated Integration Task'
        assert updated_task['progress'] == 50

        # 4. Delete the task
        response = client.delete(
            f'/api/projects/{project_id}/tasks/{task_id}',
            headers=headers
        )

        assert response.status_code == 200

        # 5. Verify deletion
        response = client.get(
            f'/api/projects/{project_id}/tasks/{task_id}',
            headers=headers
        )

        assert response.status_code == 404

    def test_staff_assignment_workflow(self, client, setup_test_data):
        """Test assigning and managing staff on tasks"""
        test_data = setup_test_data
        project = test_data['project']
        staff_list = test_data['staff']
        user = test_data['user']

        if len(staff_list) < 2:
            pytest.skip("Not enough staff members for testing")

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create a task
        task = ProjectTask(
            project_id=project.id,
            company_id=project.company_id,
            task_name="Staff Assignment Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            created_by_user_id=user.id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # Assign first staff member
        response = client.post(
            f'/api/projects/{project.id}/tasks/{task_id}/assign-staff',
            json={
                'staff_id': staff_list[0].id,
                'role_on_task': 'Lead',
                'hours_allocated': 40
            },
            headers=headers
        )

        assert response.status_code == 201
        assignment1 = json.loads(response.data)['data']
        assert assignment1['staff_id'] == staff_list[0].id

        # Assign second staff member
        response = client.post(
            f'/api/projects/{project.id}/tasks/{task_id}/assign-staff',
            json={
                'staff_id': staff_list[1].id,
                'role_on_task': 'Support',
                'hours_allocated': 20
            },
            headers=headers
        )

        assert response.status_code == 201

        # Get all assigned staff
        response = client.get(
            f'/api/projects/{project.id}/tasks/{task_id}/staff',
            headers=headers
        )

        assert response.status_code == 200
        assigned = json.loads(response.data)['data']
        assert len(assigned) == 2

        # Unassign first staff member
        response = client.post(
            f'/api/projects/{project.id}/tasks/{task_id}/unassign-staff',
            json={'staff_id': staff_list[0].id},
            headers=headers
        )

        assert response.status_code == 200

        # Verify unassignment
        response = client.get(
            f'/api/projects/{project.id}/tasks/{task_id}/staff',
            headers=headers
        )

        assigned = json.loads(response.data)['data']
        assert len(assigned) == 1
        assert assigned[0]['staff_id'] == staff_list[1].id

        # Clean up
        db.session.delete(task)
        db.session.commit()

    def test_bulk_assignment_workflow(self, client, setup_test_data):
        """Test bulk assigning multiple staff to a task"""
        test_data = setup_test_data
        project = test_data['project']
        staff_list = test_data['staff']
        user = test_data['user']

        if len(staff_list) < 3:
            pytest.skip("Not enough staff members for bulk test")

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create a task
        task = ProjectTask(
            project_id=project.id,
            company_id=project.company_id,
            task_name="Bulk Assignment Test",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            created_by_user_id=user.id
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # Bulk assign staff
        staff_ids = [staff_list[0].id, staff_list[1].id, staff_list[2].id]
        response = client.post(
            f'/api/projects/{project.id}/tasks/{task_id}/bulk-assign',
            json={'staff_ids': staff_ids},
            headers=headers
        )

        assert response.status_code == 201
        result = json.loads(response.data)['data']
        assert len(result['assigned']) == 3

        # Clean up
        db.session.delete(task)
        db.session.commit()


class TestDataPersistence:
    """Tests for data persistence and consistency"""

    def test_task_data_persists(self, client, setup_test_data):
        """Test that task data persists across requests"""
        test_data = setup_test_data
        project = test_data['project']
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create a task with specific data
        task_data = {
            'task_name': 'Persistence Test',
            'description': 'Testing data persistence',
            'priority': 'critical',
            'progress': 75,
            'status': 'in-progress',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=10)).isoformat(),
            'company_id': project.company_id
        }

        create_response = client.post(
            f'/api/projects/{project.id}/tasks',
            json=task_data,
            headers=headers
        )

        assert create_response.status_code == 201
        created_task = json.loads(create_response.data)['data']
        task_id = created_task['id']

        # Retrieve the task multiple times
        for _ in range(3):
            response = client.get(
                f'/api/projects/{project.id}/tasks/{task_id}',
                headers=headers
            )

            assert response.status_code == 200
            retrieved = json.loads(response.data)['data']

            # Verify all data persists
            assert retrieved['task_name'] == task_data['task_name']
            assert retrieved['description'] == task_data['description']
            assert retrieved['priority'] == task_data['priority']
            assert retrieved['progress'] == task_data['progress']
            assert retrieved['status'] == task_data['status']

        # Clean up
        delete_response = client.delete(
            f'/api/projects/{project.id}/tasks/{task_id}',
            headers=headers
        )
        assert delete_response.status_code == 200


class TestErrorHandling:
    """Tests for error handling and validation"""

    def test_invalid_task_dates(self, client, setup_test_data):
        """Test that invalid date ranges are rejected"""
        test_data = setup_test_data
        project = test_data['project']
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Try to create task with end_date before start_date
        task_data = {
            'task_name': 'Invalid Dates',
            'start_date': (date.today() + timedelta(days=10)).isoformat(),
            'end_date': date.today().isoformat(),  # Before start
            'company_id': project.company_id
        }

        response = client.post(
            f'/api/projects/{project.id}/tasks',
            json=task_data,
            headers=headers
        )

        assert response.status_code == 400

    def test_missing_authentication(self, client, setup_test_data):
        """Test that missing authentication is rejected"""
        test_data = setup_test_data
        project = test_data['project']

        # Request without auth header
        response = client.get(f'/api/projects/{project.id}/tasks')

        assert response.status_code == 401

    def test_nonexistent_project(self, client, setup_test_data):
        """Test accessing tasks from non-existent project"""
        test_data = setup_test_data
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Try to access non-existent project
        response = client.get(
            '/api/projects/999999/tasks',
            headers=headers
        )

        # Should return empty or 404
        assert response.status_code in [200, 404]


class TestAPIResponseFormat:
    """Tests for API response format and structure"""

    def test_response_structure(self, client, setup_test_data):
        """Test that API responses follow expected structure"""
        test_data = setup_test_data
        project = test_data['project']
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        response = client.get(
            f'/api/projects/{project.id}/tasks',
            headers=headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        # Check required fields
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_task_serialization_format(self, client, setup_test_data):
        """Test that tasks are properly serialized"""
        test_data = setup_test_data
        project = test_data['project']
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create a task
        task_data = {
            'task_name': 'Serialization Test',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=1)).isoformat(),
            'company_id': project.company_id
        }

        response = client.post(
            f'/api/projects/{project.id}/tasks',
            json=task_data,
            headers=headers
        )

        task = json.loads(response.data)['data']

        # Verify all expected fields are present
        required_fields = [
            'id', 'task_name', 'start_date', 'end_date',
            'status', 'progress', 'priority'
        ]

        for field in required_fields:
            assert field in task, f"Missing field: {field}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
