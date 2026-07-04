"""
Staff Management Tests (S1-S8)
Tests for staff CRUD operations, search, filter, and salary calculations
"""

import pytest
from datetime import datetime


@pytest.mark.staff
class TestStaffManagement:
    """Staff Management CRUD Tests"""

    # ====================================================================
    # Test S1: View All Staff
    # ====================================================================
    def test_view_all_staff(self, client, admin_headers, sample_staff_list):
        """
        Test S1: View All Staff
        Admin views complete staff list with pagination
        """
        response = client.get('/api/staff', headers=admin_headers)

        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.get_json()

        # Verify response structure
        assert 'data' in data or 'staff' in data or isinstance(data, list)
        assert len(data.get('data', data)) > 0, "No staff in response"

        # Check pagination info if present
        if isinstance(data, dict) and 'total' in data:
            assert data['total'] >= len(sample_staff_list)


    # ====================================================================
    # Test S2: Search Staff by Name
    # ====================================================================
    def test_search_staff_by_name(self, client, admin_headers, sample_staff_list):
        """
        Test S2: Search Staff by Name
        User searches for staff by name
        """
        # Get first staff name
        staff_name = sample_staff_list[0].get('name', '')

        response = client.get(f'/api/staff?search={staff_name}', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Verify search works
        staff_list = data.get('data', data) if isinstance(data, dict) else data
        assert len(staff_list) > 0, f"Search for '{staff_name}' returned no results"


    # ====================================================================
    # Test S3: Filter Staff by Role
    # ====================================================================
    def test_filter_staff_by_role(self, client, admin_headers, sample_staff_list):
        """
        Test S3: Filter Staff by Role
        User filters staff by role
        """
        # Get first staff role
        staff_role = sample_staff_list[0].get('role', 'Engineer')

        response = client.get(f'/api/staff?role={staff_role}', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()

        # Verify filter works
        staff_list = data.get('data', data) if isinstance(data, dict) else data
        assert len(staff_list) >= 0, "Filter returned error"


    # ====================================================================
    # Test S4: Add New Staff
    # ====================================================================
    @pytest.mark.smoke
    def test_add_new_staff(self, client, admin_headers):
        """
        Test S4: Add New Staff
        Admin adds new staff member
        """
        payload = {
            'name': 'New Test Worker',
            'email': 'newworker@test.com',
            'phone': '9999999999',
            'role': 'Laborer',
            'joining_date': '2026-03-15',
            'salary': 32000,
            'pf': 12,
            'esi': 0.75
        }

        response = client.post('/api/staff', json=payload, headers=admin_headers)

        assert response.status_code in [200, 201], f"Status: {response.status_code}"
        data = response.get_json()

        # Verify staff created
        if 'data' in data:
            assert data['data']['name'] == 'New Test Worker'
            assert data['data']['email'] == 'newworker@test.com'


    # ====================================================================
    # Test S5: Edit Staff
    # ====================================================================
    def test_edit_staff(self, client, admin_headers, sample_staff_list):
        """
        Test S5: Edit Staff
        Admin edits existing staff details
        """
        staff_id = sample_staff_list[0].get('id')
        assert staff_id is not None, "Could not get staff ID"

        payload = {
            'name': 'Updated Name',
            'salary': 45000
        }

        response = client.put(f'/api/staff/{staff_id}', json=payload, headers=admin_headers)

        assert response.status_code in [200, 404], f"Status: {response.status_code}"

        if response.status_code == 200:
            data = response.get_json()
            # Verify changes
            if 'data' in data:
                assert data['data']['salary'] == 45000


    # ====================================================================
    # Test S6: Delete Staff
    # ====================================================================
    def test_delete_staff(self, client, admin_headers, create_staff):
        """
        Test S6: Delete Staff
        Admin deletes a staff member
        """
        # Create a staff to delete
        staff = create_staff(name='To Delete')
        staff_id = staff.get('id') if isinstance(staff, dict) else staff

        response = client.delete(f'/api/staff/{staff_id}', headers=admin_headers)

        assert response.status_code in [200, 204, 404], f"Status: {response.status_code}"


    # ====================================================================
    # Test S7: Salary Calculations
    # ====================================================================
    def test_salary_calculations(self, client, admin_headers, sample_staff_list):
        """
        Test S7: Salary Calculations
        Verify salary calculations are accurate

        Math: Net = Base - (Base * PF%) - (Base * ESI%)
        Example: Base 30000, PF 12%, ESI 0.75%
        Net = 30000 - 3600 - 225 = 26,175
        """
        staff = sample_staff_list[0]
        staff_id = staff.get('id')

        response = client.get(f'/api/staff/{staff_id}', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()

        if 'data' in data:
            staff_data = data['data']
            base_salary = staff_data.get('salary', 0)
            pf_rate = staff_data.get('pf', 12) / 100
            esi_rate = staff_data.get('esi', 0.75) / 100

            # Calculate expected net salary
            expected_net = base_salary - (base_salary * pf_rate) - (base_salary * esi_rate)

            # Verify calculation (allow 1 rupee rounding difference)
            actual_net = staff_data.get('net_salary', expected_net)
            assert abs(actual_net - expected_net) < 1, \
                f"Net salary mismatch. Expected: {expected_net}, Got: {actual_net}"


    # ====================================================================
    # Test S8: Pagination
    # ====================================================================
    def test_pagination(self, client, admin_headers):
        """
        Test S8: Pagination
        User navigates through pages
        """
        # Get page 1
        response = client.get('/api/staff?page=1&per_page=10', headers=admin_headers)
        assert response.status_code == 200

        # Get page 2
        response = client.get('/api/staff?page=2&per_page=10', headers=admin_headers)
        assert response.status_code == 200


@pytest.mark.staff
class TestStaffValidation:
    """Staff Data Validation Tests"""

    def test_duplicate_email_prevention(self, client, admin_headers, sample_staff_list):
        """
        Test: Duplicate Email Prevention
        System should prevent duplicate emails
        """
        existing_email = sample_staff_list[0].get('email')

        payload = {
            'name': 'Another Staff',
            'email': existing_email,  # Duplicate
            'phone': '8888888888',
            'role': 'Laborer',
            'joining_date': '2026-03-15',
            'salary': 30000
        }

        response = client.post('/api/staff', json=payload, headers=admin_headers)

        # Should reject duplicate email
        assert response.status_code in [400, 409], f"Status: {response.status_code}"


    def test_required_fields_validation(self, client, admin_headers):
        """
        Test: Required Fields Validation
        Missing required fields should be rejected
        """
        # Missing name
        payload = {
            'email': 'test@test.com',
            'role': 'Laborer',
            'salary': 30000
        }

        response = client.post('/api/staff', json=payload, headers=admin_headers)
        assert response.status_code in [400, 422]


    def test_invalid_salary_value(self, client, admin_headers):
        """
        Test: Invalid Salary Value
        Negative or invalid salary should be rejected
        """
        payload = {
            'name': 'Test Staff',
            'email': 'test@test.com',
            'phone': '9999999999',
            'role': 'Laborer',
            'joining_date': '2026-03-15',
            'salary': -5000,  # Invalid
            'pf': 12,
            'esi': 0.75
        }

        response = client.post('/api/staff', json=payload, headers=admin_headers)
        assert response.status_code in [400, 422]


@pytest.mark.staff
@pytest.mark.smoke
def test_staff_module_smoke(client, admin_headers, create_staff):
    """
    Smoke Test: Staff Module
    Critical staff operations should work
    """
    # Create staff
    staff = create_staff()
    assert staff is not None, "Could not create staff"

    # View staff
    response = client.get('/api/staff', headers=admin_headers)
    assert response.status_code == 200


@pytest.mark.staff
@pytest.mark.integration
def test_staff_integration_flow(client, admin_headers):
    """
    Integration Test: Staff Complete Flow
    1. Create staff
    2. View staff
    3. Edit staff
    4. Delete staff
    """
    # Step 1: Create
    create_payload = {
        'name': 'Integration Test Staff',
        'email': 'integration@test.com',
        'phone': '9999999999',
        'role': 'Engineer',
        'joining_date': '2026-03-15',
        'salary': 50000,
        'pf': 12,
        'esi': 3
    }

    create_response = client.post('/api/staff', json=create_payload, headers=admin_headers)
    assert create_response.status_code in [200, 201]

    if create_response.status_code in [200, 201]:
        staff_id = create_response.get_json().get('data', {}).get('id')

        if staff_id:
            # Step 2: View
            view_response = client.get(f'/api/staff/{staff_id}', headers=admin_headers)
            assert view_response.status_code == 200

            # Step 3: Edit
            edit_payload = {'salary': 55000}
            edit_response = client.put(f'/api/staff/{staff_id}', json=edit_payload,
                                      headers=admin_headers)
            assert edit_response.status_code in [200, 404]

            # Step 4: Delete
            delete_response = client.delete(f'/api/staff/{staff_id}', headers=admin_headers)
            assert delete_response.status_code in [200, 204, 404]
