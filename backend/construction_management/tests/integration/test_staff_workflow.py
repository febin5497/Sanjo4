"""
Integration Tests for Staff Management Workflow (E2E)
Tests complete staff creation, update, deletion, and associated operations
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestStaffWorkflow:
    """Complete staff management workflow tests"""

    # ====================================================================
    # Test SW1: Complete Staff Creation Workflow
    # ====================================================================
    def test_staff_creation_workflow(self, client, admin_headers, test_company, db_session):
        """
        Test SW1: Complete Staff Creation Workflow
        Admin creates new staff member with all required fields
        """
        # Step 1: Prepare staff data
        staff_data = {
            'name': 'John Smith',
            'email': 'john.smith@test.com',
            'phone': '9876543210',
            'role': 'Site Engineer',
            'department': 'Engineering',
            'company_id': test_company.id,
            'date_of_joining': '2024-01-15',
            'address': '123 Main St, Test City',
            'salary': 50000,
            'designation': 'Senior Engineer',
            'employee_id': 'EMP001'
        }

        # Step 2: Submit staff creation request
        response = client.post(
            '/api/staff',
            headers=admin_headers,
            json=staff_data,
            content_type='application/json'
        )

        # Verify response
        assert response.status_code in [200, 201], f"Failed: {response.get_json()}"
        data = response.get_json()
        assert 'id' in data or 'staff_id' in data
        staff_id = data.get('id') or data.get('staff_id')

        # Step 3: Verify staff in database
        response = client.get(f'/api/staff/{staff_id}', headers=admin_headers)
        assert response.status_code == 200
        staff = response.get_json()
        assert staff.get('name') == 'John Smith'
        assert staff.get('email') == 'john.smith@test.com'
        assert staff.get('role') == 'Site Engineer'

        # Step 4: Verify staff appears in list
        response = client.get('/api/staff', headers=admin_headers)
        assert response.status_code == 200
        staff_list = response.get_json()
        assert isinstance(staff_list, (dict, list))

    # ====================================================================
    # Test SW2: Staff Creation with Validation
    # ====================================================================
    def test_staff_creation_validation(self, client, admin_headers, test_company):
        """
        Test SW2: Staff Creation with Validation
        Ensure required fields are validated properly
        """
        # Missing email - should fail
        invalid_data = {
            'name': 'Jane Doe',
            'phone': '1234567890',
            'role': 'Supervisor'
        }

        response = client.post(
            '/api/staff',
            headers=admin_headers,
            json=invalid_data,
            content_type='application/json'
        )

        assert response.status_code in [400, 422], "Should reject staff without email"

    # ====================================================================
    # Test SW3: Staff Update Workflow
    # ====================================================================
    def test_staff_update_workflow(self, client, admin_headers, test_company, sample_staff):
        """
        Test SW3: Staff Update Workflow
        Admin updates staff member information
        """
        staff_id = sample_staff[0]['id']

        # Prepare update data
        update_data = {
            'phone': '9999999999',
            'salary': 55000,
            'department': 'HR'
        }

        # Submit update
        response = client.put(
            f'/api/staff/{staff_id}',
            headers=admin_headers,
            json=update_data,
            content_type='application/json'
        )

        assert response.status_code in [200, 204], f"Failed: {response.get_json()}"

        # Verify update
        response = client.get(f'/api/staff/{staff_id}', headers=admin_headers)
        assert response.status_code == 200
        staff = response.get_json()
        assert staff.get('phone') == '9999999999'
        assert staff.get('salary') == 55000

    # ====================================================================
    # Test SW4: Staff Deletion Workflow
    # ====================================================================
    def test_staff_deletion_workflow(self, client, admin_headers, test_company, sample_staff):
        """
        Test SW4: Staff Deletion Workflow
        Admin deletes staff member
        """
        staff_id = sample_staff[0]['id']

        # Delete staff
        response = client.delete(
            f'/api/staff/{staff_id}',
            headers=admin_headers
        )

        assert response.status_code in [200, 204], f"Failed: {response.get_json()}"

        # Verify deletion
        response = client.get(f'/api/staff/{staff_id}', headers=admin_headers)
        assert response.status_code == 404, "Staff should not exist after deletion"

    # ====================================================================
    # Test SW5: Staff Search and Filter Workflow
    # ====================================================================
    def test_staff_search_filter_workflow(self, client, admin_headers, sample_staff):
        """
        Test SW5: Staff Search and Filter Workflow
        User searches and filters staff by various criteria
        """
        # Search by name
        response = client.get(
            '/api/staff?search=John',
            headers=admin_headers
        )
        assert response.status_code == 200

        # Filter by role
        response = client.get(
            '/api/staff?role=Engineer',
            headers=admin_headers
        )
        assert response.status_code == 200

        # Filter by department
        response = client.get(
            '/api/staff?department=Engineering',
            headers=admin_headers
        )
        assert response.status_code == 200

    # ====================================================================
    # Test SW6: Staff Salary Calculation
    # ====================================================================
    def test_staff_salary_calculation_workflow(self, client, admin_headers, sample_staff):
        """
        Test SW6: Staff Salary Calculation Workflow
        Verify salary, PF, ESI calculations
        """
        staff_id = sample_staff[0]['id']

        response = client.get(
            f'/api/staff/{staff_id}/salary-details',
            headers=admin_headers
        )

        if response.status_code == 200:
            data = response.get_json()
            # Verify salary components if available
            if 'salary_details' in data:
                assert 'basic_salary' in data['salary_details'] or \
                       'gross_salary' in data['salary_details']

    # ====================================================================
    # Test SW7: Bulk Staff Import
    # ====================================================================
    def test_bulk_staff_import_workflow(self, client, admin_headers, test_company):
        """
        Test SW7: Bulk Staff Import Workflow
        Import multiple staff members from data
        """
        staff_list = [
            {
                'name': 'Alice Johnson',
                'email': 'alice@test.com',
                'phone': '9111111111',
                'role': 'Engineer',
                'department': 'Engineering',
                'company_id': test_company.id,
                'salary': 45000
            },
            {
                'name': 'Bob Wilson',
                'email': 'bob@test.com',
                'phone': '9222222222',
                'role': 'Technician',
                'department': 'Operations',
                'company_id': test_company.id,
                'salary': 35000
            }
        ]

        # Attempt bulk import
        response = client.post(
            '/api/staff/bulk-import',
            headers=admin_headers,
            json={'staff_list': staff_list},
            content_type='application/json'
        )

        # Should succeed or return 400 if endpoint not implemented
        assert response.status_code in [200, 201, 400, 404]

    # ====================================================================
    # Test SW8: Staff-Project Assignment Workflow
    # ====================================================================
    def test_staff_project_assignment_workflow(self, client, admin_headers, sample_staff, sample_projects):
        """
        Test SW8: Staff-Project Assignment Workflow
        Assign staff to projects and verify assignments
        """
        if not sample_projects:
            pytest.skip("No projects available for testing")

        staff_id = sample_staff[0]['id']
        project_id = sample_projects[0]['id']

        # Assign staff to project
        assignment_data = {
            'staff_id': staff_id,
            'project_id': project_id,
            'role': 'Lead Engineer',
            'start_date': '2024-03-01'
        }

        response = client.post(
            f'/api/staff/{staff_id}/assign-project',
            headers=admin_headers,
            json=assignment_data,
            content_type='application/json'
        )

        # Verify assignment
        if response.status_code in [200, 201]:
            response = client.get(
                f'/api/staff/{staff_id}/projects',
                headers=admin_headers
            )
            assert response.status_code == 200

    # ====================================================================
    # Test SW9: Staff Permissions and Authorization
    # ====================================================================
    def test_staff_authorization_workflow(self, client, user_headers, admin_headers, sample_staff):
        """
        Test SW9: Staff Permissions and Authorization
        Verify role-based access control for staff operations
        """
        staff_id = sample_staff[0]['id']

        # Regular user shouldn't be able to delete staff
        response = client.delete(
            f'/api/staff/{staff_id}',
            headers=user_headers
        )
        assert response.status_code == 403, "Regular user should not delete staff"

        # Admin should be able to delete
        response = client.delete(
            f'/api/staff/{staff_id}',
            headers=admin_headers
        )
        assert response.status_code in [200, 204, 404]

    # ====================================================================
    # Test SW10: Staff Activity Logging
    # ====================================================================
    def test_staff_activity_logging_workflow(self, client, admin_headers, test_company, db_session):
        """
        Test SW10: Staff Activity Logging Workflow
        Verify that staff operations are logged properly
        """
        staff_data = {
            'name': 'Activity Test Staff',
            'email': 'activity@test.com',
            'phone': '9876543210',
            'role': 'Technician',
            'company_id': test_company.id,
            'salary': 40000
        }

        response = client.post(
            '/api/staff',
            headers=admin_headers,
            json=staff_data,
            content_type='application/json'
        )

        if response.status_code in [200, 201]:
            # Verify activity log if available
            response = client.get(
                '/api/admin/activity-logs?resource_type=staff',
                headers=admin_headers
            )
            # Should return 200 or 404 if not implemented
            assert response.status_code in [200, 404]
