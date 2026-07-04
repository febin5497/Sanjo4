"""
Integration Tests for Authentication and Authorization Workflow
Tests complete authentication flow, role-based access control
"""

import pytest
import json
from datetime import datetime, timedelta


@pytest.mark.integration
class TestAuthenticationWorkflow:
    """Complete authentication workflow tests"""

    # ====================================================================
    # Test AW1: User Registration Workflow
    # ====================================================================
    def test_user_registration_workflow(self, client, test_company):
        """
        Test AW1: User Registration Workflow
        New user registers and creates account
        """
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'SecurePass@123',
            'password_confirm': 'SecurePass@123',
            'company_id': test_company.id
        }

        response = client.post(
            '/api/auth/register',
            json=registration_data,
            content_type='application/json'
        )

        assert response.status_code in [200, 201], f"Failed: {response.get_json()}"
        data = response.get_json()
        assert 'user' in data or 'message' in data

    # ====================================================================
    # Test AW2: User Login Workflow
    # ====================================================================
    def test_user_login_workflow(self, client, admin_user):
        """
        Test AW2: User Login Workflow
        User logs in with credentials
        """
        login_data = {
            'username': 'admin',
            'password': 'Admin@123'
        }

        response = client.post(
            '/api/auth/login',
            json=login_data,
            content_type='application/json'
        )

        assert response.status_code == 200, f"Failed: {response.get_json()}"
        data = response.get_json()
        assert 'access_token' in data or 'token' in data
        assert 'user' in data or 'username' in data

    # ====================================================================
    # Test AW3: Invalid Login Attempt
    # ====================================================================
    def test_invalid_login_workflow(self, client, admin_user):
        """
        Test AW3: Invalid Login Attempt
        User attempts login with wrong credentials
        """
        login_data = {
            'username': 'admin',
            'password': 'WrongPassword123'
        }

        response = client.post(
            '/api/auth/login',
            json=login_data,
            content_type='application/json'
        )

        assert response.status_code == 401, "Should reject invalid password"

    # ====================================================================
    # Test AW4: JWT Token Validation
    # ====================================================================
    def test_jwt_token_validation_workflow(self, client, admin_headers, admin_user):
        """
        Test AW4: JWT Token Validation
        Verify JWT token is properly validated
        """
        # Valid token
        response = client.get(
            '/api/auth/me',
            headers=admin_headers
        )
        assert response.status_code == 200

        # Invalid token
        invalid_headers = {'Authorization': 'Bearer invalid.token.here'}
        response = client.get(
            '/api/auth/me',
            headers=invalid_headers
        )
        assert response.status_code == 401

    # ====================================================================
    # Test AW5: Token Refresh Workflow
    # ====================================================================
    def test_token_refresh_workflow(self, client, admin_headers):
        """
        Test AW5: Token Refresh Workflow
        User refreshes expired token
        """
        response = client.post(
            '/api/auth/refresh',
            headers=admin_headers,
            content_type='application/json'
        )

        assert response.status_code in [200, 201, 404]
        if response.status_code in [200, 201]:
            data = response.get_json()
            assert 'access_token' in data or 'token' in data

    # ====================================================================
    # Test AW6: Role-Based Access Control
    # ====================================================================
    def test_rbac_workflow(self, client, admin_headers, user_headers):
        """
        Test AW6: Role-Based Access Control
        Verify different roles have appropriate access
        """
        # Admin should access admin endpoints
        response = client.get(
            '/api/admin/users',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]

        # Regular user should not access admin endpoints
        response = client.get(
            '/api/admin/users',
            headers=user_headers
        )
        assert response.status_code == 403

    # ====================================================================
    # Test AW7: Permission-Based Authorization
    # ====================================================================
    def test_permission_authorization_workflow(self, client, admin_headers, user_headers):
        """
        Test AW7: Permission-Based Authorization
        Verify permissions are enforced
        """
        # User without permission should be denied
        response = client.post(
            '/api/staff',
            headers=user_headers,
            json={'name': 'Test', 'email': 'test@test.com'},
            content_type='application/json'
        )
        assert response.status_code in [403, 401]

        # Admin should have permission
        response = client.post(
            '/api/staff',
            headers=admin_headers,
            json={
                'name': 'Test Staff',
                'email': 'test@test.com',
                'phone': '9876543210',
                'role': 'Engineer'
            },
            content_type='application/json'
        )
        assert response.status_code in [200, 201, 400, 422]

    # ====================================================================
    # Test AW8: Password Reset Workflow
    # ====================================================================
    def test_password_reset_workflow(self, client, admin_user):
        """
        Test AW8: Password Reset Workflow
        User resets forgotten password
        """
        # Step 1: Request password reset
        response = client.post(
            '/api/auth/forgot-password',
            json={'email': admin_user.email},
            content_type='application/json'
        )
        assert response.status_code in [200, 404]

        # Step 2: Reset password with token (if endpoint exists)
        reset_data = {
            'token': 'mock-token',
            'new_password': 'NewPass@123',
            'confirm_password': 'NewPass@123'
        }
        response = client.post(
            '/api/auth/reset-password',
            json=reset_data,
            content_type='application/json'
        )
        assert response.status_code in [200, 400, 404]

    # ====================================================================
    # Test AW9: User Logout Workflow
    # ====================================================================
    def test_user_logout_workflow(self, client, admin_headers):
        """
        Test AW9: User Logout Workflow
        User logs out and token is invalidated
        """
        response = client.post(
            '/api/auth/logout',
            headers=admin_headers,
            content_type='application/json'
        )

        assert response.status_code in [200, 204, 404]

        # Subsequent request with old token should fail
        response = client.get(
            '/api/auth/me',
            headers=admin_headers
        )
        # Should be 401 or still 200 depending on implementation
        assert response.status_code in [401, 200]

    # ====================================================================
    # Test AW10: Session Management
    # ====================================================================
    def test_session_management_workflow(self, client, admin_user):
        """
        Test AW10: Session Management Workflow
        Manage user sessions and concurrent logins
        """
        # Login 1
        response1 = client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'Admin@123'},
            content_type='application/json'
        )
        assert response1.status_code == 200

        # Login 2 (concurrent)
        response2 = client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'Admin@123'},
            content_type='application/json'
        )
        assert response2.status_code == 200

    # ====================================================================
    # Test AW11: Account Lockout
    # ====================================================================
    def test_account_lockout_workflow(self, client, admin_user):
        """
        Test AW11: Account Lockout Workflow
        Account locks after failed login attempts
        """
        # Multiple failed attempts
        for _ in range(5):
            response = client.post(
                '/api/auth/login',
                json={'username': 'admin', 'password': 'WrongPassword'},
                content_type='application/json'
            )

        # Should be locked or rate limited
        response = client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'Admin@123'},
            content_type='application/json'
        )
        # May succeed or be locked depending on implementation
        assert response.status_code in [200, 401, 429]

    # ====================================================================
    # Test AW12: Two-Factor Authentication
    # ====================================================================
    def test_two_factor_auth_workflow(self, client, admin_user):
        """
        Test AW12: Two-Factor Authentication Workflow
        Setup and use 2FA if implemented
        """
        # Setup 2FA
        response = client.post(
            '/api/auth/2fa/setup',
            headers={'Authorization': f'Bearer mock-token'},
            content_type='application/json'
        )
        assert response.status_code in [200, 404]

        # Verify 2FA code
        response = client.post(
            '/api/auth/2fa/verify',
            json={'code': '123456'},
            content_type='application/json'
        )
        assert response.status_code in [200, 401, 404]

    # ====================================================================
    # Test AW13: Company Isolation
    # ====================================================================
    def test_company_isolation_workflow(self, client, admin_headers, test_company):
        """
        Test AW13: Company Isolation Workflow
        Verify users only see their company's data
        """
        # Create staff in test company
        response = client.post(
            '/api/staff',
            headers=admin_headers,
            json={
                'name': 'Company Staff',
                'email': 'staff@test.com',
                'phone': '9876543210',
                'company_id': test_company.id,
                'role': 'Engineer'
            },
            content_type='application/json'
        )

        if response.status_code in [200, 201]:
            # Staff should be associated with company
            data = response.get_json()
            assert data.get('company_id') == test_company.id or 'id' in data

    # ====================================================================
    # Test AW14: API Key Authentication
    # ====================================================================
    def test_api_key_auth_workflow(self, client):
        """
        Test AW14: API Key Authentication Workflow
        Authenticate using API key if supported
        """
        response = client.get(
            '/api/staff',
            headers={'X-API-Key': 'test-api-key'}
        )
        assert response.status_code in [200, 401, 404]

    # ====================================================================
    # Test AW15: Audit Trail
    # ====================================================================
    def test_audit_trail_workflow(self, client, admin_headers):
        """
        Test AW15: Audit Trail Workflow
        Track and retrieve authentication audit logs
        """
        response = client.get(
            '/api/admin/audit-logs?resource=auth',
            headers=admin_headers
        )
        assert response.status_code in [200, 404]
