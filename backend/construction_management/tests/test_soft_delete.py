"""Soft-Delete Integration Tests (SD1-SD8)

Tests soft-delete functionality across all major model types.
"""

import pytest
from datetime import datetime, date


@pytest.mark.integration
class TestSoftDeleteUnit:

    def test_sd1_basic_soft_delete(self, db_session, test_company):
        """SD1: Basic soft delete marks record as deleted"""
        from staff_management.models import Staff
        staff = Staff(
            staff_id='SD-TEST-001', name='Delete Test',
            first_name='Delete', last_name='Test',
            email='delete@test.com', phone='9990000001',
            personal_phone='9990000001',
            role='Laborer', salary=30000, pf=12, esi=0.75,
            joining_date=date(2026, 1, 1), company_id=test_company.id
        )
        db_session.add(staff)
        db_session.commit()
        staff_id = staff.id

        staff.soft_delete(user_id=1)
        db_session.commit()

        still_there = db_session.get(Staff, staff_id)
        assert still_there is not None
        assert still_there.is_deleted is True
        assert still_there.deleted_at is not None
        assert still_there.deleted_by == 1

    def test_sd2_restore_soft_deleted(self, db_session, test_company):
        """SD2: Restore brings back a soft-deleted record"""
        from staff_management.models import Staff
        staff = Staff(
            staff_id='SD-TEST-002', name='Restore Test',
            first_name='Restore', last_name='Test',
            email='restore@test.com', phone='9990000002',
            personal_phone='9990000002',
            role='Foreman', salary=35000, pf=12, esi=0.75,
            joining_date=date(2026, 1, 1), company_id=test_company.id
        )
        db_session.add(staff)
        db_session.commit()

        staff.soft_delete(user_id=1)
        db_session.commit()
        assert staff.is_deleted is True

        staff.restore()
        db_session.commit()
        assert staff.is_deleted is False
        assert staff.deleted_at is None
        assert staff.deleted_by is None

    def test_sd3_get_active_filters_deleted(self, db_session, test_company):
        """SD3: get_active() returns None for deleted records"""
        from staff_management.models import Staff
        staff = Staff(
            staff_id='SD-TEST-003', name='Active Test',
            first_name='Active', last_name='Test',
            email='active@test.com', phone='9990000003',
            personal_phone='9990000003',
            role='Engineer', salary=40000, pf=12, esi=0.75,
            joining_date=date(2026, 1, 1), company_id=test_company.id
        )
        db_session.add(staff)
        db_session.commit()
        sid = staff.id

        assert Staff.get_active(sid) is not None
        staff.soft_delete(user_id=1)
        db_session.commit()
        assert Staff.get_active(sid) is None

    def test_sd4_get_all_active_excludes_deleted(self, db_session, test_company):
        """SD4: get_all_active() excludes deleted records"""
        from staff_management.models import Staff
        for i in range(3):
            s = Staff(
                staff_id=f'SD-TEST-00{i+4}', name=f'Active{i}',
                first_name=f'Active{i}', last_name='Test',
                email=f'active{i}@test.com', phone=f'99900000{i+4}',
                personal_phone=f'99900000{i+4}',
                role='Laborer', salary=30000, pf=12, esi=0.75,
                joining_date=date(2026, 1, 1), company_id=test_company.id
            )
            db_session.add(s)
        db_session.commit()

        all_active = Staff.get_all_active().all()
        assert len(all_active) == 3

        all_active[0].soft_delete(user_id=1)
        db_session.commit()

        remaining = Staff.get_all_active().all()
        assert len(remaining) == 2


@pytest.mark.integration
class TestSoftDeleteCrossModel:

    def test_sd5_soft_delete_on_company(self, db_session):
        """SD5: Soft delete works on Company model"""
        from company_settings.models import Company
        company = Company(
            name='SD Company', address='123 Test',
            phone='9990000100', email='sd@co.com', gst_number='SDGST01'
        )
        db_session.add(company)
        db_session.commit()
        cid = company.id

        company.soft_delete(user_id=1)
        db_session.commit()

        assert db_session.get(Company, cid).is_deleted is True

    def test_sd6_soft_delete_on_project(self, db_session, test_company):
        """SD6: Soft delete works on Project model"""
        from client_management.models import Client
        from project_management.models.models import Project

        client = Client(
            name='SD Client', phone='9990000101', email='sd@client.com'
        )
        db_session.add(client)
        db_session.commit()

        proj = Project(
            name='SD Project', location='Test',
            start_date=date(2026, 1, 1), user_id=1,
            company_id=test_company.id, client_id=client.id
        )
        db_session.add(proj)
        db_session.commit()
        pid = proj.id

        proj.soft_delete(user_id=1)
        db_session.commit()

        assert db_session.get(Project, pid).is_deleted is True

    def test_sd7_soft_delete_on_invoice(self, db_session, test_company):
        """SD7: Soft delete works on Invoice model"""
        from finance_management.models.invoice import Invoice

        inv = Invoice(
            invoice_id='SD-INV-001', client='SD Client',
            subtotal=10000, total=11800,
            due_date=date(2026, 6, 30), company_id=test_company.id
        )
        db_session.add(inv)
        db_session.commit()
        iid = inv.id

        inv.soft_delete(user_id=1)
        db_session.commit()

        assert db_session.get(Invoice, iid).is_deleted is True

    def test_sd8_soft_delete_on_equipment(self, db_session, test_company):
        """SD8: Soft delete works on Equipment model"""
        from equipment_management.models import Equipment

        eq = Equipment(
            name='SD Excavator', category='Heavy',
            equipment_code='EQ-SD-001',
            company_id=test_company.id
        )
        db_session.add(eq)
        db_session.commit()
        eid = eq.id

        eq.soft_delete(user_id=1)
        db_session.commit()

        assert db_session.get(Equipment, eid).is_deleted is True
