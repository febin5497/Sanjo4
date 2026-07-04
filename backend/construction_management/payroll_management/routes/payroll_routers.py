"""
Specialized Payroll Management Routers - Using BaseResourceRouter

Auto-generates CRUD endpoints for payroll entities:
- Payroll Cycles
- Payroll Records

Consolidates explicit route implementations.
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required
from base.base_resource_router import BaseResourceRouter
from payroll_management.models.payroll import PayrollCycle, PayrollRecord


# ==================== Payroll Cycle Router ====================

class PayrollCycleRouter(BaseResourceRouter):
    """Auto-generates Payroll Cycle CRUD endpoints"""
    model = PayrollCycle
    entity_name = "Payroll Cycle"
    searchable_fields = ['month', 'year', 'status']

    @classmethod
    def schema(cls, obj):
        """Schema for Payroll Cycle responses"""
        return {
            'id': obj.id,
            'month': obj.month,
            'year': obj.year,
            'status': obj.status,
            'start_date': obj.start_date.isoformat(),
            'end_date': obj.end_date.isoformat(),
            'approved_by_id': obj.approved_by_id,
            'approved_at': obj.approved_at.isoformat() if obj.approved_at else None,
            'company_id': obj.company_id,
            'record_count': len(obj.records) if hasattr(obj, 'records') else 0,
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Payroll Cycle creation"""
        errors = []
        if not data.get('month'):
            errors.append({'field': 'month', 'message': 'Month required (1-12)'})
        if not data.get('year'):
            errors.append({'field': 'year', 'message': 'Year required'})
        if not data.get('start_date'):
            errors.append({'field': 'start_date', 'message': 'Start date required'})
        if not data.get('end_date'):
            errors.append({'field': 'end_date', 'message': 'End date required'})
        return errors


# ==================== Payroll Record Router ====================

class PayrollRecordRouter(BaseResourceRouter):
    """Auto-generates Payroll Record CRUD endpoints"""
    model = PayrollRecord
    entity_name = "Payroll Record"
    searchable_fields = ['staff_id', 'cycle_id']

    @classmethod
    def schema(cls, obj):
        """Schema for Payroll Record responses"""
        return {
            'id': obj.id,
            'cycle_id': obj.cycle_id,
            'staff_id': obj.staff_id,
            'days_worked': float(obj.days_worked) if obj.days_worked else 0,
            'gross_salary': float(obj.gross_salary),
            'pf_amount': float(obj.pf_amount) if obj.pf_amount else 0,
            'esi_amount': float(obj.esi_amount) if obj.esi_amount else 0,
            'tax_amount': float(obj.tax_amount) if obj.tax_amount else 0,
            'other_deductions': float(obj.other_deductions) if obj.other_deductions else 0,
            'total_deductions': float((obj.pf_amount or 0) + (obj.esi_amount or 0) + (obj.tax_amount or 0) + (obj.other_deductions or 0)),
            'net_salary': float(obj.net_salary),
            'created_at': obj.created_at.isoformat() if obj.created_at else None
        }

    @classmethod
    def _validate_create(cls, data):
        """Validate Payroll Record creation"""
        errors = []
        if not data.get('cycle_id'):
            errors.append({'field': 'cycle_id', 'message': 'Payroll cycle ID required'})
        if not data.get('staff_id'):
            errors.append({'field': 'staff_id', 'message': 'Staff ID required'})
        if not data.get('gross_salary'):
            errors.append({'field': 'gross_salary', 'message': 'Gross salary required'})
        if not data.get('net_salary'):
            errors.append({'field': 'net_salary', 'message': 'Net salary required'})
        return errors


# ==================== Register Routers ====================

def register_payroll_routers(app):
    """Register all payroll management routers with Flask app"""
    # Payroll Cycles
    cycle_bp = PayrollCycleRouter.create_blueprint(url_prefix='/api/payroll/cycles')
    app.register_blueprint(cycle_bp)

    # Payroll Records
    record_bp = PayrollRecordRouter.create_blueprint(url_prefix='/api/payroll/records')
    app.register_blueprint(record_bp)
