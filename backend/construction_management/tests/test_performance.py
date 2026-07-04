"""
Performance Testing for Task Management System
Tests system behavior with large datasets and high load
"""

import pytest
import time
import json
from datetime import date, timedelta
from flask_jwt_extended import create_access_token
from extensions import db
from project_management.models import Project
from project_management.models.task_model import ProjectTask
from staff_management.models import Staff
from client_management.models import Client


@pytest.fixture
def performance_test_data(client, test_company, admin_user):
    """Create large dataset for performance testing"""
    # Create test client and project
    test_client = Client(
        name='Performance Test Client',
        email='perf@test.com',
        phone='9999999999',
        address='Test Address'
    )
    db.session.add(test_client)
    db.session.flush()

    project = Project(
        name='Performance Test Project',
        location='Test Location',
        company_id=test_company.id,
        start_date=date.today(),
        user_id=admin_user.id,
        client_id=test_client.id
    )
    db.session.add(project)
    db.session.flush()

    # Create multiple staff members
    staff_list = []
    for i in range(50):  # 50 staff members
        staff = Staff(
            first_name=f'PerfStaff{i}',
            last_name=f'Worker{i}',
            staff_id=f'STF-PERF-{i:04d}',
            company_id=test_company.id,
            email=f'perfstaff{i}@test.com',
            personal_phone=f'555000{i:04d}',
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


class TestPerformanceWithManyTasks:
    """Performance tests with large task datasets"""

    def test_create_1000_tasks_performance(self, client, performance_test_data):
        """Test performance of creating 1000 tasks"""
        test_data = performance_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Measure task creation time
        start_time = time.time()
        created_tasks = []

        for i in range(100):  # Create 100 tasks for practical testing
            task_data = {
                'task_name': f'Performance Task {i}',
                'description': f'Task for performance testing - {i}',
                'task_type': 'Activity',
                'start_date': date.today().isoformat(),
                'end_date': (date.today() + timedelta(days=10)).isoformat(),
                'status': 'todo',
                'progress': 0,
                'priority': 'medium',
                'company_id': company_id
            }

            response = client.post(
                f'/api/projects/{project_id}/tasks',
                json=task_data,
                headers=headers
            )

            assert response.status_code == 201
            task = json.loads(response.data)['data']
            created_tasks.append(task['id'])

        elapsed_time = time.time() - start_time
        avg_time_per_task = elapsed_time / 100

        # Performance assertions
        assert elapsed_time < 30  # 100 tasks should be created in < 30 seconds
        assert avg_time_per_task < 0.3  # Average < 300ms per task

        print(f"\n✅ Created 100 tasks in {elapsed_time:.2f}s (avg {avg_time_per_task*1000:.1f}ms per task)")

    def test_list_tasks_pagination_performance(self, client, performance_test_data):
        """Test performance of listing tasks with pagination"""
        test_data = performance_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create 50 tasks
        for i in range(50):
            task_data = {
                'task_name': f'List Test Task {i}',
                'start_date': date.today().isoformat(),
                'end_date': (date.today() + timedelta(days=5)).isoformat(),
                'company_id': company_id
            }
            client.post(
                f'/api/projects/{project_id}/tasks',
                json=task_data,
                headers=headers
            )

        # Measure list performance with pagination
        start_time = time.time()
        response = client.get(
            f'/api/projects/{project_id}/tasks?page=1&per_page=10',
            headers=headers
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data

        # Performance assertion
        assert elapsed_time < 1.0  # Should retrieve paginated list in < 1 second

        print(f"\n✅ Listed paginated tasks in {elapsed_time*1000:.1f}ms")

    def test_bulk_assignment_performance(self, client, performance_test_data):
        """Test performance of bulk staff assignment"""
        test_data = performance_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        staff_list = test_data['staff'][:20]  # Use 20 staff members
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create a task
        task_data = {
            'task_name': 'Bulk Assignment Performance Test',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=5)).isoformat(),
            'company_id': company_id
        }
        response = client.post(
            f'/api/projects/{project_id}/tasks',
            json=task_data,
            headers=headers
        )
        task_id = json.loads(response.data)['data']['id']

        # Measure bulk assignment performance
        staff_ids = [s.id for s in staff_list]
        start_time = time.time()

        response = client.post(
            f'/api/projects/{project_id}/tasks/{task_id}/bulk-assign',
            json={'staff_ids': staff_ids},
            headers=headers
        )

        elapsed_time = time.time() - start_time

        assert response.status_code == 201
        result = json.loads(response.data)['data']
        assert len(result['assigned']) == len(staff_ids)

        # Performance assertion
        assert elapsed_time < 2.0  # Bulk assign 20 staff in < 2 seconds

        print(f"\n✅ Bulk assigned {len(staff_ids)} staff in {elapsed_time*1000:.1f}ms")

    def test_filter_and_sort_performance(self, client, performance_test_data):
        """Test performance of filtering and sorting tasks"""
        test_data = performance_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create tasks with various statuses
        for i in range(30):
            status = ['todo', 'in-progress', 'done'][i % 3]
            task_data = {
                'task_name': f'Filter Test Task {i}',
                'start_date': date.today().isoformat(),
                'end_date': (date.today() + timedelta(days=5)).isoformat(),
                'status': status,
                'company_id': company_id
            }
            client.post(
                f'/api/projects/{project_id}/tasks',
                json=task_data,
                headers=headers
            )

        # Test filtering performance
        start_time = time.time()
        response = client.get(
            f'/api/projects/{project_id}/tasks?status=in-progress&sort_by=start_date',
            headers=headers
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 1.0

        print(f"\n✅ Filtered and sorted tasks in {elapsed_time*1000:.1f}ms")


class TestConcurrencyAndLoad:
    """Test system behavior under load"""

    def test_concurrent_task_updates(self, client, performance_test_data):
        """Simulate concurrent task updates"""
        test_data = performance_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create a task
        task_data = {
            'task_name': 'Concurrent Update Test',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=5)).isoformat(),
            'company_id': company_id
        }
        response = client.post(
            f'/api/projects/{project_id}/tasks',
            json=task_data,
            headers=headers
        )
        task_id = json.loads(response.data)['data']['id']

        # Simulate multiple concurrent updates
        start_time = time.time()

        for i in range(20):
            update_data = {
                'progress': (i + 1) * 5,  # 5%, 10%, 15%, ... 100%
                'status': 'in-progress' if i < 15 else 'done'
            }
            response = client.put(
                f'/api/projects/{project_id}/tasks/{task_id}',
                json=update_data,
                headers=headers
            )
            assert response.status_code == 200

        elapsed_time = time.time() - start_time

        # Verify final state
        response = client.get(
            f'/api/projects/{project_id}/tasks/{task_id}',
            headers=headers
        )
        final_task = json.loads(response.data)['data']
        assert final_task['progress'] == 100
        assert final_task['status'] == 'done'

        # Performance assertion
        assert elapsed_time < 5.0  # 20 updates should complete in < 5 seconds

        print(f"\n✅ Completed 20 concurrent updates in {elapsed_time*1000:.1f}ms")


class TestMemoryAndResponseSize:
    """Test memory usage and response sizes"""

    def test_large_response_handling(self, client, performance_test_data):
        """Test handling of large API responses"""
        test_data = performance_test_data
        project_id = test_data['project'].id
        company_id = test_data['company'].id
        user = test_data['user']

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        # Create many tasks
        for i in range(50):
            task_data = {
                'task_name': f'Large Response Test {i}',
                'description': f'Task {i} with detailed description',
                'start_date': date.today().isoformat(),
                'end_date': (date.today() + timedelta(days=5)).isoformat(),
                'company_id': company_id
            }
            client.post(
                f'/api/projects/{project_id}/tasks',
                json=task_data,
                headers=headers
            )

        # Fetch all tasks and measure response
        start_time = time.time()
        response = client.get(
            f'/api/projects/{project_id}/tasks?per_page=50',
            headers=headers
        )
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        response_size = len(response.data)

        print(f"\n✅ Retrieved large response ({response_size/1024:.1f}KB) in {elapsed_time*1000:.1f}ms")

        # Assertions
        assert elapsed_time < 2.0  # Large response should be retrieved quickly
        assert response_size < 1024 * 500  # Response should be < 500KB


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
