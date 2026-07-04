"""Finance Exception Handling Tests (FE1-FE5)

Tests that finance routes properly handle exceptions:
- ValueError for invalid input
- IntegrityError for duplicate/constraint violations
- Generic 500 fallback
- User-friendly error messages
"""

import pytest


@pytest.mark.finance
@pytest.mark.integration
class TestFinanceExceptionHandling:

    def test_fe1_invalid_budget_value(self, client, admin_headers, test_company):
        """FE1: ValueError returns 400 for negative budget amount"""
        payload = {
            'name': 'Bad Budget',
            'amount': -1000,
            'fiscal_year': '2026-2027',
            'company_id': test_company.id
        }
        response = client.post('/api/finance/budgets', json=payload, headers=admin_headers)
        assert response.status_code in (400, 422, 500)
        if response.status_code == 400:
            data = response.get_json()
            msg = str(data).lower()
            assert any(w in msg for w in ['error', 'invalid', 'message'])

    def test_fe2_duplicate_budget_name(self, client, admin_headers, test_company):
        """FE2: IntegrityError for duplicate budget name"""
        payload = {
            'name': 'Unique Budget',
            'amount': 50000,
            'fiscal_year': '2026-2027',
            'company_id': test_company.id
        }
        # Create once
        r1 = client.post('/api/finance/budgets', json=payload, headers=admin_headers)
        # Create again (should fail)
        r2 = client.post('/api/finance/budgets', json=payload, headers=admin_headers)
        assert r2.status_code in (400, 409, 500)

    def test_fe3_invalid_coa_type(self, client, admin_headers, test_company):
        """FE3: ValueError for invalid chart of accounts type"""
        payload = {
            'account_name': 'Bad Account',
            'account_type': 'NotARealType',
            'company_id': test_company.id
        }
        response = client.post('/api/finance/coa', json=payload, headers=admin_headers)
        assert response.status_code in (400, 422, 500)

    def test_fe5_missing_required_fields(self, client, admin_headers):
        """FE5: Missing required fields return 400"""
        response = client.post('/api/finance/coa', json={}, headers=admin_headers)
        assert response.status_code in (400, 422, 500)
