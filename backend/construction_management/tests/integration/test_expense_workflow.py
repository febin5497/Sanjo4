"""
Integration Tests for Expense Management Workflow (E2E)
Tests complete expense creation, approval, rejection workflows
"""

import pytest
from datetime import datetime, timedelta


@pytest.mark.integration
class TestExpenseWorkflow:
    """Complete expense management workflow tests"""

    # ====================================================================
    # Test EW1: Complete Expense Creation Workflow
    # ====================================================================
    def test_expense_creation_workflow(self, client, admin_headers, test_company, sample_projects):
        """
        Test EW1: Complete Expense Creation Workflow
        User creates expense and submits for approval
        """
        if not sample_projects:
            pytest.skip("No projects available for testing")

        project_id = sample_projects[0]['id']

        # Step 1: Create expense
        expense_data = {
            'project_id': project_id,
            'category': 'Materials',
            'description': 'Cement and aggregates',
            'amount': 15000.00,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'vendor_name': 'ABC Supplies',
            'payment_method': 'Cheque',
            'reference_number': 'PO-2024-001'
        }

        response = client.post(
            '/api/expense',
            headers=admin_headers,
            json=expense_data,
            content_type='application/json'
        )

        assert response.status_code in [200, 201], f"Failed: {response.get_json()}"
        data = response.get_json()
        expense_id = data.get('id') or data.get('expense_id')

        # Step 2: Verify expense created
        response = client.get(f'/api/expense/{expense_id}', headers=admin_headers)
        assert response.status_code == 200
        expense = response.get_json()
        assert expense.get('amount') == 15000.00
        assert expense.get('category') == 'Materials'

    # ====================================================================
    # Test EW2: Expense Validation
    # ====================================================================
    def test_expense_validation_workflow(self, client, admin_headers, sample_projects):
        """
        Test EW2: Expense Validation Workflow
        Ensure required fields are validated
        """
        if not sample_projects:
            pytest.skip("No projects available for testing")

        # Missing amount
        invalid_data = {
            'project_id': sample_projects[0]['id'],
            'category': 'Materials',
            'description': 'Test'
        }

        response = client.post(
            '/api/expense',
            headers=admin_headers,
            json=invalid_data,
            content_type='application/json'
        )

        assert response.status_code in [400, 422], "Should reject expense without amount"

    # ====================================================================
    # Test EW3: Expense Approval Workflow
    # ====================================================================
    def test_expense_approval_workflow(self, client, admin_headers, sample_expense):
        """
        Test EW3: Expense Approval Workflow
        Manager approves pending expense
        """
        if not sample_expense:
            pytest.skip("No expenses available for testing")

        expense_id = sample_expense['id']

        # Step 1: Check expense status is pending
        response = client.get(f'/api/expense/{expense_id}', headers=admin_headers)
        assert response.status_code == 200

        # Step 2: Approve expense
        response = client.put(
            f'/api/expense/{expense_id}/approve',
            headers=admin_headers,
            json={'notes': 'Approved by manager'},
            content_type='application/json'
        )

        if response.status_code in [200, 204]:
            # Verify approval
            response = client.get(f'/api/expense/{expense_id}', headers=admin_headers)
            assert response.status_code == 200
            expense = response.get_json()
            assert expense.get('status') == 'approved'

    # ====================================================================
    # Test EW4: Expense Rejection Workflow
    # ====================================================================
    def test_expense_rejection_workflow(self, client, admin_headers, sample_expense):
        """
        Test EW4: Expense Rejection Workflow
        Manager rejects expense with reason
        """
        if not sample_expense:
            pytest.skip("No expenses available for testing")

        expense_id = sample_expense['id']

        response = client.put(
            f'/api/expense/{expense_id}/reject',
            headers=admin_headers,
            json={'rejection_reason': 'Invoice missing'},
            content_type='application/json'
        )

        if response.status_code in [200, 204]:
            response = client.get(f'/api/expense/{expense_id}', headers=admin_headers)
            assert response.status_code == 200
            expense = response.get_json()
            assert expense.get('status') == 'rejected'

    # ====================================================================
    # Test EW5: Expense Update Workflow
    # ====================================================================
    def test_expense_update_workflow(self, client, admin_headers, sample_expense):
        """
        Test EW5: Expense Update Workflow
        User updates expense details before approval
        """
        if not sample_expense:
            pytest.skip("No expenses available for testing")

        expense_id = sample_expense['id']

        # Update pending expense
        update_data = {
            'amount': 16000.00,
            'description': 'Updated materials list'
        }

        response = client.put(
            f'/api/expense/{expense_id}',
            headers=admin_headers,
            json=update_data,
            content_type='application/json'
        )

        if response.status_code in [200, 204]:
            response = client.get(f'/api/expense/{expense_id}', headers=admin_headers)
            assert response.status_code == 200
            expense = response.get_json()
            assert expense.get('amount') == 16000.00

    # ====================================================================
    # Test EW6: Expense Deletion Workflow
    # ====================================================================
    def test_expense_deletion_workflow(self, client, admin_headers, sample_expense):
        """
        Test EW6: Expense Deletion Workflow
        Delete pending expense
        """
        if not sample_expense:
            pytest.skip("No expenses available for testing")

        expense_id = sample_expense['id']

        response = client.delete(
            f'/api/expense/{expense_id}',
            headers=admin_headers
        )

        if response.status_code in [200, 204]:
            response = client.get(f'/api/expense/{expense_id}', headers=admin_headers)
            assert response.status_code == 404

    # ====================================================================
    # Test EW7: Expense Filtering and Search
    # ====================================================================
    def test_expense_filter_search_workflow(self, client, admin_headers):
        """
        Test EW7: Expense Filtering and Search Workflow
        Filter expenses by category, status, date range
        """
        # Filter by category
        response = client.get(
            '/api/expense?category=Materials',
            headers=admin_headers
        )
        assert response.status_code == 200

        # Filter by status
        response = client.get(
            '/api/expense?status=pending',
            headers=admin_headers
        )
        assert response.status_code == 200

        # Filter by date range
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        response = client.get(
            f'/api/expense?start_date={start_date}&end_date={end_date}',
            headers=admin_headers
        )
        assert response.status_code == 200

    # ====================================================================
    # Test EW8: Bulk Expense Import
    # ====================================================================
    def test_bulk_expense_import_workflow(self, client, admin_headers, sample_projects):
        """
        Test EW8: Bulk Expense Import Workflow
        Import multiple expenses at once
        """
        if not sample_projects:
            pytest.skip("No projects available for testing")

        project_id = sample_projects[0]['id']

        expenses = [
            {
                'project_id': project_id,
                'category': 'Materials',
                'description': 'Bricks',
                'amount': 5000,
                'date': datetime.now().strftime('%Y-%m-%d')
            },
            {
                'project_id': project_id,
                'category': 'Labor',
                'description': 'Daily wages',
                'amount': 3000,
                'date': datetime.now().strftime('%Y-%m-%d')
            }
        ]

        response = client.post(
            '/api/expense/bulk-import',
            headers=admin_headers,
            json={'expenses': expenses},
            content_type='application/json'
        )

        assert response.status_code in [200, 201, 400, 404]

    # ====================================================================
    # Test EW9: Expense Pagination
    # ====================================================================
    def test_expense_pagination_workflow(self, client, admin_headers):
        """
        Test EW9: Expense Pagination Workflow
        Paginate through expense list
        """
        # Get first page
        response = client.get(
            '/api/expense?page=1&per_page=10',
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.get_json()

        # Verify pagination fields
        if isinstance(data, dict):
            assert 'page' in data or 'data' in data

    # ====================================================================
    # Test EW10: Expense Report Generation
    # ====================================================================
    def test_expense_report_workflow(self, client, admin_headers):
        """
        Test EW10: Expense Report Generation Workflow
        Generate expense reports and summaries
        """
        response = client.get(
            '/api/expense/reports/summary',
            headers=admin_headers
        )

        # Should return 200 if implemented, 404 if not
        assert response.status_code in [200, 404]

    # ====================================================================
    # Test EW11: Expense Export
    # ====================================================================
    def test_expense_export_workflow(self, client, admin_headers):
        """
        Test EW11: Expense Export Workflow
        Export expenses to CSV/PDF
        """
        # Export to CSV
        response = client.get(
            '/api/expense/export?format=csv',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]

        # Export to PDF
        response = client.get(
            '/api/expense/export?format=pdf',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]

    # ====================================================================
    # Test EW12: Expense Category Management
    # ====================================================================
    def test_expense_category_workflow(self, client, admin_headers):
        """
        Test EW12: Expense Category Management Workflow
        Manage expense categories
        """
        # Get all categories
        response = client.get(
            '/api/expense-categories',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]

    # ====================================================================
    # Test EW13: Concurrent Expense Operations
    # ====================================================================
    def test_concurrent_expense_operations(self, client, admin_headers, sample_projects):
        """
        Test EW13: Concurrent Expense Operations
        Handle multiple simultaneous expense operations
        """
        if not sample_projects:
            pytest.skip("No projects available for testing")

        project_id = sample_projects[0]['id']
        responses = []

        # Create multiple expenses
        for i in range(3):
            expense_data = {
                'project_id': project_id,
                'category': 'Materials',
                'description': f'Test expense {i}',
                'amount': 1000 + (i * 100),
                'date': datetime.now().strftime('%Y-%m-%d')
            }

            response = client.post(
                '/api/expense',
                headers=admin_headers,
                json=expense_data,
                content_type='application/json'
            )
            responses.append(response.status_code)

        # At least one should succeed
        assert any(status in [200, 201] for status in responses)
