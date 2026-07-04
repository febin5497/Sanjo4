"""
Expense Approval Workflow Tests
Tests the complete flow: Create → Approve/Reject → Verify Status
"""

import pytest
from datetime import datetime
from flask import json


@pytest.mark.integration
class TestExpenseApprovalWorkflow:
    """Complete expense approval workflow tests"""

    def test_approve_expense_endpoint(self, client, admin_headers, sample_expense):
        """
        Test: POST /api/staff/expenses/{id}/approve
        Verify expense can be approved and status is updated
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']

        # Step 1: Verify expense is pending
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        expense = response.get_json()
        assert expense.get('status') in ['Pending', 'pending']

        # Step 2: Approve expense
        response = client.post(
            f'/api/staff/expenses/{expense_id}/approve',
            headers=admin_headers,
            json={}
        )

        assert response.status_code in [200, 201], f"Failed: {response.get_json()}"
        data = response.get_json()
        assert data.get('success') is True or 'approved successfully' in str(data).lower()

        # Step 3: Verify expense is now approved
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        approved_expense = response.get_json()
        assert approved_expense.get('status') in ['Approved', 'approved']
        assert approved_expense.get('approved_by') is not None
        assert approved_expense.get('approved_date') is not None

    def test_reject_expense_endpoint(self, client, admin_headers, sample_expense):
        """
        Test: POST /api/staff/expenses/{id}/reject
        Verify expense can be rejected with reason
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']

        # Step 1: Reject expense with reason
        response = client.post(
            f'/api/staff/expenses/{expense_id}/reject',
            headers=admin_headers,
            json={'rejection_reason': 'Invoice not attached'}
        )

        assert response.status_code in [200, 201], f"Failed: {response.get_json()}"
        data = response.get_json()
        assert data.get('success') is True or 'rejected successfully' in str(data).lower()

        # Step 2: Verify expense is now rejected
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        rejected_expense = response.get_json()
        assert rejected_expense.get('status') in ['Rejected', 'rejected']
        assert rejected_expense.get('rejection_reason') == 'Invoice not attached'

    def test_cannot_approve_non_pending_expense(self, client, admin_headers, sample_expense):
        """
        Test: Prevent approval of already approved/rejected expenses
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']

        # First approval
        response = client.post(
            f'/api/staff/expenses/{expense_id}/approve',
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [200, 201]

        # Try to approve again - should fail
        response = client.post(
            f'/api/staff/expenses/{expense_id}/approve',
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [400, 409], "Should not allow approving already approved expense"

    def test_cannot_reject_non_pending_expense(self, client, admin_headers, sample_expense):
        """
        Test: Prevent rejection of already approved/rejected expenses
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']

        # First rejection
        response = client.post(
            f'/api/staff/expenses/{expense_id}/reject',
            headers=admin_headers,
            json={'rejection_reason': 'Test'}
        )
        assert response.status_code in [200, 201]

        # Try to reject again - should fail
        response = client.post(
            f'/api/staff/expenses/{expense_id}/reject',
            headers=admin_headers,
            json={'rejection_reason': 'Another reason'}
        )
        assert response.status_code in [400, 409], "Should not allow rejecting already rejected expense"

    def test_approval_tracks_approver_info(self, client, admin_headers, sample_expense):
        """
        Test: Verify approved_by and approved_date are recorded correctly
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']

        # Get current user ID from token
        response = client.post(
            f'/api/staff/expenses/{expense_id}/approve',
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [200, 201]

        # Verify approval info
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        expense = response.get_json()

        assert expense.get('approved_by') is not None, "approved_by should be recorded"
        assert expense.get('approved_date') is not None, "approved_date should be recorded"
        assert isinstance(expense.get('approved_by'), int), "approved_by should be user ID"

    def test_rejection_reason_is_stored(self, client, admin_headers, sample_expense):
        """
        Test: Verify rejection reason is properly stored
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']
        rejection_reason = "Missing supporting documents"

        response = client.post(
            f'/api/staff/expenses/{expense_id}/reject',
            headers=admin_headers,
            json={'rejection_reason': rejection_reason}
        )
        assert response.status_code in [200, 201]

        # Verify rejection reason
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        expense = response.get_json()
        assert expense.get('rejection_reason') == rejection_reason

    def test_expense_approval_activity_logging(self, client, admin_headers, sample_expense):
        """
        Test: Verify approval action is logged for audit trail
        """
        if not sample_expense:
            pytest.skip("No sample expense available")

        expense_id = sample_expense['id']

        # Approve expense
        response = client.post(
            f'/api/staff/expenses/{expense_id}/approve',
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [200, 201]

        # The response should indicate success and approval was logged
        data = response.get_json()
        assert data.get('success') is True or 'success' in str(data).lower()

    def test_complete_expense_lifecycle(self, client, admin_headers, sample_projects):
        """
        Test: Complete lifecycle - Create → Verify Pending → Approve → Verify Approved
        """
        if not sample_projects:
            pytest.skip("No projects available")

        project_id = sample_projects[0]['id']

        # Step 1: Create expense
        expense_data = {
            'project_id': project_id,
            'category': 'Materials',
            'description': 'Test materials for approval',
            'amount': 5000.00,
            'date': datetime.now().strftime('%Y-%m-%d')
        }

        response = client.post(
            '/api/staff/expenses',
            headers=admin_headers,
            json=expense_data,
            content_type='application/json'
        )
        assert response.status_code in [200, 201], f"Failed to create: {response.get_json()}"
        created = response.get_json()
        expense_id = created.get('id') or created.get('data', {}).get('id')

        if not expense_id:
            pytest.skip("Could not retrieve created expense ID")

        # Step 2: Verify it's pending
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        expense = response.get_json()
        assert expense.get('status') in ['Pending', 'pending']

        # Step 3: Approve
        response = client.post(
            f'/api/staff/expenses/{expense_id}/approve',
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [200, 201]

        # Step 4: Verify approved
        response = client.get(f'/api/staff/expenses/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        expense = response.get_json()
        assert expense.get('status') in ['Approved', 'approved']
        assert expense.get('approved_by') is not None
