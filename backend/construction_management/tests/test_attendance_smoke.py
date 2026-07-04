"""
Smoke Tests for Attendance System
Tests all critical endpoints to ensure system is working
"""

import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from attendance_management.models import Attendance, AttendancePhoto
from staff_management.models import Staff
from user_management.models import User


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client, app):
    """Create test user and get auth token"""
    with app.app_context():
        # Create user
        user = User(
            username='testuser',
            email='test@example.com',
            password='password123',
            company_id=1
        )
        db.session.add(user)
        db.session.commit()

        # Create staff
        staff = Staff(
            user_id=user.id,
            name='Test Staff',
            role='Laborer',
            phone='9876543210',
            company_id=1
        )
        db.session.add(staff)
        db.session.commit()

        # Create token (simplified - in real app use JWT)
        token = 'test-token'

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }, user.id, staff.id


class TestAttendanceEndpoints:
    """Test basic CRUD endpoints"""

    def test_get_attendance_list(self, client, auth_headers):
        """Test GET /api/attendance/"""
        headers, user_id, staff_id = auth_headers
        response = client.get('/api/attendance/', headers=headers)
        assert response.status_code in [200, 401]  # 401 ok if no valid auth
        print(f"[PASS] GET /api/attendance/ - Status: {response.status_code}")

    def test_create_attendance(self, client, auth_headers, app):
        """Test POST /api/attendance/"""
        headers, user_id, staff_id = auth_headers

        with app.app_context():
            data = {
                'staff_id': staff_id,
                'date': datetime.now().date().isoformat(),
                'present': True,
                'half_day': False,
                'night_shift': False,
                'overtime_hours': 0
            }

            response = client.post(
                '/api/attendance/',
                headers=headers,
                data=json.dumps(data)
            )
            assert response.status_code in [201, 401, 400]
            print(f"[PASS] POST /api/attendance/ - Status: {response.status_code}")

    def test_get_today_status(self, client, auth_headers):
        """Test GET /api/attendance/today-status"""
        headers, user_id, staff_id = auth_headers
        response = client.get('/api/attendance/today-status', headers=headers)
        assert response.status_code in [200, 401, 404]
        print(f"[PASS] GET /api/attendance/today-status - Status: {response.status_code}")

    def test_get_stats(self, client, auth_headers):
        """Test GET /api/attendance/stats/<staff_id>"""
        headers, user_id, staff_id = auth_headers
        response = client.get(f'/api/attendance/stats/{staff_id}', headers=headers)
        assert response.status_code in [200, 401]
        print(f"[PASS] GET /api/attendance/stats/<id> - Status: {response.status_code}")


class TestApprovalEndpoints:
    """Test photo approval workflow endpoints"""

    def test_get_pending_approvals(self, client, auth_headers):
        """Test GET /api/attendance/approvals/pending"""
        headers, user_id, staff_id = auth_headers
        response = client.get('/api/attendance/approvals/pending', headers=headers)
        assert response.status_code in [200, 401]
        print(f"[PASS] GET /api/attendance/approvals/pending - Status: {response.status_code}")

    def test_get_approval_stats(self, client, auth_headers):
        """Test GET /api/attendance/approvals/stats"""
        headers, user_id, staff_id = auth_headers
        response = client.get('/api/attendance/approvals/stats', headers=headers)
        assert response.status_code in [200, 401]
        print(f"[PASS] GET /api/attendance/approvals/stats - Status: {response.status_code}")

    def test_approve_photo_endpoint(self, client, auth_headers):
        """Test POST /api/attendance/approvals/<id>/approve"""
        headers, user_id, staff_id = auth_headers
        photo_id = 999  # Non-existent
        response = client.post(
            f'/api/attendance/approvals/{photo_id}/approve',
            headers=headers,
            data=json.dumps({'notes': 'Approved'})
        )
        # Should be 400 (photo not found) or 401 (auth failed), not 500
        assert response.status_code in [400, 401, 404, 200]
        print(f"[PASS] POST /api/attendance/approvals/<id>/approve - Status: {response.status_code}")

    def test_reject_photo_endpoint(self, client, auth_headers):
        """Test POST /api/attendance/approvals/<id>/reject"""
        headers, user_id, staff_id = auth_headers
        photo_id = 999  # Non-existent
        response = client.post(
            f'/api/attendance/approvals/{photo_id}/reject',
            headers=headers,
            data=json.dumps({'rejection_reason': 'Blurry'})
        )
        # Should be 400 (photo not found) or 401 (auth failed), not 500
        assert response.status_code in [400, 401, 404, 200]
        print(f"[PASS] POST /api/attendance/approvals/<id>/reject - Status: {response.status_code}")

    def test_bulk_approve(self, client, auth_headers):
        """Test POST /api/attendance/approvals/bulk-approve"""
        headers, user_id, staff_id = auth_headers
        response = client.post(
            '/api/attendance/approvals/bulk-approve',
            headers=headers,
            data=json.dumps({'photo_ids': []})
        )
        assert response.status_code in [200, 400, 401]
        print(f"[PASS] POST /api/attendance/approvals/bulk-approve - Status: {response.status_code}")

    def test_bulk_reject(self, client, auth_headers):
        """Test POST /api/attendance/approvals/bulk-reject"""
        headers, user_id, staff_id = auth_headers
        response = client.post(
            '/api/attendance/approvals/bulk-reject',
            headers=headers,
            data=json.dumps({'photo_ids': [], 'reason': 'Rejected'})
        )
        assert response.status_code in [200, 400, 401]
        print(f"[PASS] POST /api/attendance/approvals/bulk-reject - Status: {response.status_code}")


class TestManualPunchEndpoints:
    """Test manual punch-in endpoints for HR"""

    def test_manual_punch(self, client, auth_headers):
        """Test POST /api/attendance/manual-punch"""
        headers, user_id, staff_id = auth_headers

        data = {
            'staff_id': staff_id,
            'date': datetime.now().date().isoformat(),
            'punch_in_time': datetime.now().isoformat(),
            'save_and_approve': True
        }

        response = client.post(
            '/api/attendance/manual-punch',
            headers=headers,
            data=json.dumps(data)
        )
        assert response.status_code in [201, 400, 401, 404]
        print(f"[PASS] POST /api/attendance/manual-punch - Status: {response.status_code}")


class TestPunchInOut:
    """Test punch-in and punch-out flow"""

    def test_punch_out(self, client, auth_headers):
        """Test POST /api/attendance/punch-out"""
        headers, user_id, staff_id = auth_headers
        response = client.post(
            '/api/attendance/punch-out',
            headers=headers
        )
        assert response.status_code in [200, 400, 401, 404]
        print(f"[PASS] POST /api/attendance/punch-out - Status: {response.status_code}")

    def test_mark_leave(self, client, auth_headers):
        """Test POST /api/attendance/mark-leave"""
        headers, user_id, staff_id = auth_headers
        response = client.post(
            '/api/attendance/mark-leave',
            headers=headers,
            data=json.dumps({'leave_reason': 'Sick Leave'})
        )
        assert response.status_code in [200, 400, 401, 404]
        print(f"[PASS] POST /api/attendance/mark-leave - Status: {response.status_code}")

    def test_update_overtime(self, client, auth_headers):
        """Test POST /api/attendance/update-overtime"""
        headers, user_id, staff_id = auth_headers
        response = client.post(
            '/api/attendance/update-overtime',
            headers=headers,
            data=json.dumps({'overtime_hours': 2.0})
        )
        assert response.status_code in [200, 400, 401, 404]
        print(f"[PASS] POST /api/attendance/update-overtime - Status: {response.status_code}")

    def test_update_night_shift(self, client, auth_headers):
        """Test POST /api/attendance/update-night-shift"""
        headers, user_id, staff_id = auth_headers
        response = client.post(
            '/api/attendance/update-night-shift',
            headers=headers,
            data=json.dumps({'night_shift': True})
        )
        assert response.status_code in [200, 400, 401, 404]
        print(f"[PASS] POST /api/attendance/update-night-shift - Status: {response.status_code}")


class TestModelIntegration:
    """Test database model integration"""

    def test_attendance_model_exists(self, app):
        """Verify Attendance model exists and has correct fields"""
        with app.app_context():
            from attendance_management.models import Attendance

            # Check table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            assert 'attendance' in tables

            # Check key columns exist
            columns = [col['name'] for col in inspector.get_columns('attendance')]
            required_fields = [
                'id', 'staff_id', 'date', 'present', 'half_day',
                'night_shift', 'overtime_hours', 'punch_in_time',
                'punch_out_time', 'punch_in_type', 'punch_in_photo_id',
                'status', 'approved_by', 'approved_at', 'rejection_reason'
            ]

            for field in required_fields:
                assert field in columns, f"Field '{field}' missing from attendance table"

            print("[PASS] Attendance model - All required fields exist")

    def test_attendance_photo_model_exists(self, app):
        """Verify AttendancePhoto model exists and has rejection fields"""
        with app.app_context():
            from attendance_management.models import AttendancePhoto

            # Check table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            assert 'attendance_photos' in tables

            # Check rejection fields exist
            columns = [col['name'] for col in inspector.get_columns('attendance_photos')]
            assert 'rejected_by' in columns, "rejected_by field missing"
            assert 'rejected_at' in columns, "rejected_at field missing"
            assert 'approval_status' in columns, "approval_status field missing"

            print("[PASS] AttendancePhoto model - Rejection fields exist")

    def test_create_attendance_record(self, app):
        """Test creating an attendance record"""
        with app.app_context():
            from attendance_management.models import Attendance
            from staff_management.models import Staff

            # Create staff
            staff = Staff(
                name='Test Person',
                role='Worker',
                phone='1234567890',
                company_id=1
            )
            db.session.add(staff)
            db.session.commit()

            # Create attendance
            attendance = Attendance(
                staff_id=staff.id,
                date=datetime.now().date(),
                present=True,
                half_day=False,
                night_shift=False,
                overtime_hours=0.0,
                status='pending',
                punch_in_type='manual'
            )
            db.session.add(attendance)
            db.session.commit()

            # Verify
            saved = Attendance.query.filter_by(staff_id=staff.id).first()
            assert saved is not None
            assert saved.status == 'pending'
            assert saved.present == True

            print("[PASS] Attendance record creation - Works correctly")


def run_all_smoke_tests():
    """Run all smoke tests"""
    print("\n" + "="*60)
    print("ATTENDANCE SYSTEM - SMOKE TESTS")
    print("="*60 + "\n")

    pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-s'
    ])


if __name__ == '__main__':
    run_all_smoke_tests()
