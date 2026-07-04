import unittest
from app import create_app, db
from quote_management.models import Quote, QuoteItem, QuoteTemplate, TemplateItem
from user_management.models import User
import json

class QuoteTestCase(unittest.TestCase):
    """Test cases for Quote Management"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        """Create a test user with token"""
        user = User(
            username='testuser',
            email='test@example.com',
            company_id=1,
            role='Manager'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def get_auth_token(self):
        """Get authentication token for test user"""
        from flask_jwt_extended import create_access_token
        with self.app.app_context():
            return create_access_token(identity=self.user_id)

    def test_create_quote(self):
        """Test creating a quote"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        data = {
            'quote_number': 'QT-2024-001',
            'client_id': 1,
            'tax_rate': 0.05,
            'notes': 'Test quote',
            'items': [
                {
                    'description': 'Item 1',
                    'quantity': 2,
                    'unit_price': 100,
                    'unit_of_measure': 'Unit'
                }
            ]
        }

        response = self.client.post(
            '/api/quotes',
            json=data,
            headers=headers
        )

        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['data']['quoteNumber'], 'QT-2024-001')

    def test_get_quotes_list(self):
        """Test retrieving quotes list"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        # Create test quote
        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-002',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.05
            )
            db.session.add(quote)
            db.session.commit()

        response = self.client.get(
            '/api/quotes',
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertGreater(len(json_data['data']), 0)

    def test_get_quote_detail(self):
        """Test retrieving quote detail"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-003',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.05,
                status='Draft'
            )
            db.session.add(quote)
            db.session.commit()
            quote_id = quote.id

        response = self.client.get(
            f'/api/quotes/{quote_id}',
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['data']['quoteNumber'], 'QT-2024-003')

    def test_update_quote(self):
        """Test updating quote"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-004',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.05
            )
            db.session.add(quote)
            db.session.commit()
            quote_id = quote.id

        update_data = {'status': 'Sent', 'notes': 'Updated notes'}

        response = self.client.put(
            f'/api/quotes/{quote_id}',
            json=update_data,
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['data']['status'], 'Sent')

    def test_delete_quote(self):
        """Test deleting quote"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-005',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.05
            )
            db.session.add(quote)
            db.session.commit()
            quote_id = quote.id

        response = self.client.delete(
            f'/api/quotes/{quote_id}',
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_add_quote_item(self):
        """Test adding item to quote"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-006',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.05
            )
            db.session.add(quote)
            db.session.commit()
            quote_id = quote.id

        item_data = {
            'description': 'Building Material',
            'quantity': 100,
            'unit_price': 50,
            'unit_of_measure': 'Meter'
        }

        response = self.client.post(
            f'/api/quotes/{quote_id}/items',
            json=item_data,
            headers=headers
        )

        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_update_quote_status(self):
        """Test updating quote status"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-007',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.05,
                status='Draft'
            )
            db.session.add(quote)
            db.session.commit()
            quote_id = quote.id

        response = self.client.put(
            f'/api/quotes/{quote_id}/status',
            json={'status': 'Accepted'},
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['data']['status'], 'Accepted')

    def test_calculate_totals(self):
        """Test automatic total calculation"""
        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-2024-008',
                client_id=1,
                user_id=self.user_id,
                tax_rate=0.1
            )

            item1 = QuoteItem(
                quote=quote,
                description='Item 1',
                quantity=10,
                unit_price=100
            )
            item1.calculate_total()

            quote.items.append(item1)
            quote.calculate_totals()

            self.assertEqual(quote.subtotal, 1000)
            self.assertEqual(quote.tax_amount, 100)
            self.assertEqual(quote.total, 1100)


class QuoteTemplateTestCase(unittest.TestCase):
    """Test cases for Quote Templates"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self):
        """Create a test user"""
        user = User(
            username='testuser',
            email='test@example.com',
            company_id=1,
            role='Manager'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def get_auth_token(self):
        """Get authentication token"""
        from flask_jwt_extended import create_access_token
        with self.app.app_context():
            return create_access_token(identity=self.user_id)

    def test_create_template(self):
        """Test creating quote template"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        data = {
            'template_name': 'Standard Quote',
            'description': 'Standard quote template',
            'tax_rate': 0.05,
            'notes': 'Standard notes',
            'items': [
                {
                    'description': 'Template Item',
                    'quantity_default': 1,
                    'unit_price': 100
                }
            ]
        }

        response = self.client.post(
            '/api/quotes/templates',
            json=data,
            headers=headers
        )

        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_get_templates(self):
        """Test retrieving templates"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        response = self.client.get(
            '/api/quotes/templates',
            headers=headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_create_quote_from_template(self):
        """Test creating quote from template"""
        token = self.get_auth_token()
        headers = {'Authorization': f'Bearer {token}'}

        # Create template first
        with self.app.app_context():
            template = QuoteTemplate(
                company_id=1,
                user_id=self.user_id,
                template_name='Test Template',
                tax_rate=0.05
            )
            db.session.add(template)
            db.session.commit()
            template_id = template.id

        quote_data = {
            'quote_number': 'QT-FROM-TEMPLATE',
            'client_id': 1
        }

        response = self.client.post(
            f'/api/quotes/templates/{template_id}/use',
            json=quote_data,
            headers=headers
        )

        self.assertEqual(response.status_code, 201)
        json_data = json.loads(response.data)
        self.assertTrue(json_data['success'])

    def test_quote_status_workflow(self):
        """Test quote status workflow"""
        with self.app.app_context():
            quote = Quote(
                company_id=1,
                quote_number='QT-WORKFLOW',
                client_id=1,
                user_id=self.user_id,
                status='Draft'
            )
            db.session.add(quote)
            db.session.commit()

            self.assertEqual(quote.status, 'Draft')

            quote.status = 'Sent'
            db.session.commit()

            quote.status = 'Accepted'
            db.session.commit()

            self.assertEqual(quote.status, 'Accepted')


if __name__ == '__main__':
    unittest.main()
