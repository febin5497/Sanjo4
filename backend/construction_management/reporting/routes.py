"""
Report Generation API Endpoints
Provides comprehensive reporting functionality
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from extensions import db
from utils.export_utils import CSVExporter, PDFExporter, JSONExporter

# Import models
from staff_management.models import Staff
from staff_management.expense_model import Expense
from project_management.models.models import Project
from vehicle_management.models import Vehicle
from attendance_management.models import Attendance
from user_management.models import User


reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


# ============================================================================
# STAFF REPORTS
# ============================================================================

@reports_bp.route('/staff', methods=['GET'])
@jwt_required()
def get_staff_report():
    """
    Get comprehensive staff report
    Query Parameters:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Default to last 30 days
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        # Get staff data
        staff_query = Staff.query
        if user.company_id:
            staff_query = staff_query.filter(Staff.company_id == user.company_id)

        staff_list = staff_query.all()

        # Calculate by role
        by_role = db.session.query(
            Staff.role,
            func.count(Staff.id).label('count')
        ).filter(Staff.company_id == user.company_id).group_by(Staff.role).all()

        # Calculate by department
        by_department = db.session.query(
            Staff.department,
            func.count(Staff.id).label('count')
        ).filter(Staff.company_id == user.company_id).group_by(Staff.department).all()

        # New hires
        new_hires = db.session.query(
            func.date(Staff.date_of_joining).label('date'),
            func.count(Staff.id).label('count')
        ).filter(
            and_(
                Staff.company_id == user.company_id,
                Staff.date_of_joining >= start_date,
                Staff.date_of_joining <= end_date
            )
        ).group_by(func.date(Staff.date_of_joining)).all()

        # Salary summary
        salary_summary = db.session.query(
            func.sum(Staff.salary).label('total_basic'),
            func.sum(Staff.pf_amount).label('total_pf'),
            func.sum(Staff.esi_amount).label('total_esi'),
            func.avg(Staff.salary).label('avg_salary')
        ).filter(Staff.company_id == user.company_id).first()

        return jsonify({
            'total_staff': len(staff_list),
            'byRole': [
                {'name': role, 'value': count}
                for role, count in by_role
            ],
            'byDepartment': [
                {'name': dept, 'value': count}
                for dept, count in by_department
            ],
            'newHires': [
                {'date': str(date), 'count': count}
                for date, count in new_hires
            ],
            'salaryData': {
                'totalBasic': float(salary_summary.total_basic or 0),
                'totalPF': float(salary_summary.total_pf or 0),
                'totalESI': float(salary_summary.total_esi or 0),
                'avgSalary': float(salary_summary.avg_salary or 0)
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error generating staff report: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500


@reports_bp.route('/staff/export/csv', methods=['GET'])
@jwt_required()
def export_staff_csv():
    """Export staff report to CSV"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        staff_list = Staff.query.filter(
            Staff.company_id == user.company_id
        ).all()

        staff_data = [
            {
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'phone': s.phone,
                'role': s.role,
                'department': s.department,
                'salary': s.salary,
                'pf': s.pf,
                'esi': s.esi,
                'joining_date': s.date_of_joining
            }
            for s in staff_list
        ]

        return CSVExporter.export_staff(staff_data)

    except Exception as e:
        return jsonify({'error': 'Failed to export'}), 500


@reports_bp.route('/staff/export/pdf', methods=['GET'])
@jwt_required()
def export_staff_pdf():
    """Export staff report to PDF"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        staff_list = Staff.query.filter(
            Staff.company_id == user.company_id
        ).all()

        staff_data = [
            {
                'id': s.id,
                'name': s.name,
                'email': s.email,
                'phone': s.phone,
                'role': s.role,
                'department': s.department,
                'salary': s.salary,
                'pf': s.pf,
                'esi': s.esi,
                'joining_date': s.date_of_joining
            }
            for s in staff_list
        ]

        return PDFExporter.export_staff(staff_data)

    except Exception as e:
        return jsonify({'error': 'Failed to export'}), 500


# ============================================================================
# EXPENSE REPORTS
# ============================================================================

@reports_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expense_report():
    """
    Get comprehensive expense report
    Query Parameters:
    - start_date: YYYY-MM-DD
    - end_date: YYYY-MM-DD
    - group_by: daily|weekly|monthly
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        # Date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'daily')

        # Default to last 30 days
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

        # Get expenses
        expenses = Expense.query.filter(
            and_(
                Expense.company_id == user.company_id,
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).all()

        # By category
        by_category = db.session.query(
            Expense.category,
            func.sum(Expense.amount).label('total')
        ).filter(
            and_(
                Expense.company_id == user.company_id,
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(Expense.category).all()

        # By project
        by_project = db.session.query(
            Project.name,
            func.sum(Expense.amount).label('total')
        ).join(Project).filter(
            and_(
                Expense.company_id == user.company_id,
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(Project.id, Project.name).all()

        # Status breakdown
        status_breakdown = db.session.query(
            Expense.status,
            func.count(Expense.id).label('count')
        ).filter(
            and_(
                Expense.company_id == user.company_id,
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(Expense.status).all()

        # Trends (based on group_by parameter)
        trends = db.session.query(
            func.date(Expense.date).label('date'),
            func.sum(Expense.amount).label('amount')
        ).filter(
            and_(
                Expense.company_id == user.company_id,
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).group_by(func.date(Expense.date)).all()

        # Calculate total
        total_amount = sum(e.amount for e in expenses)
        total_count = len(expenses)

        # Approval metrics
        approved = [e for e in expenses if e.status == 'approved']
        approved_count = len(approved)
        pending_count = len([e for e in expenses if e.status == 'pending'])
        avg_approval_time = 2  # Placeholder

        return jsonify({
            'totalAmount': total_amount,
            'totalCount': total_count,
            'byCategory': [
                {'name': cat, 'value': float(total)}
                for cat, total in by_category
            ],
            'byProject': [
                {'name': name, 'value': float(total)}
                for name, total in by_project
            ],
            'statusBreakdown': [
                {'status': status, 'count': count}
                for status, count in status_breakdown
            ],
            'trends': [
                {'date': str(date), 'amount': float(amount)}
                for date, amount in trends
            ],
            'approvalMetrics': {
                'avgApprovalTime': avg_approval_time,
                'approvalRate': (approved_count / total_count * 100) if total_count > 0 else 0,
                'rejectionRate': (len([e for e in expenses if e.status == 'rejected']) / total_count * 100) if total_count > 0 else 0
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error generating expense report: {str(e)}")
        return jsonify({'error': 'Failed to generate report'}), 500


@reports_bp.route('/expenses/export/csv', methods=['GET'])
@jwt_required()
def export_expenses_csv():
    """Export expenses to CSV"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        expenses = Expense.query.filter(
            Expense.company_id == user.company_id
        ).all()

        expense_data = [
            {
                'id': e.id,
                'project_name': e.project.name if e.project else '',
                'category': e.category,
                'description': e.description,
                'amount': e.amount,
                'date': e.date,
                'status': e.status,
                'vendor_name': e.vendor_name,
                'payment_method': e.payment_method
            }
            for e in expenses
        ]

        return CSVExporter.export_expenses(expense_data)

    except Exception as e:
        return jsonify({'error': 'Failed to export'}), 500


@reports_bp.route('/expenses/export/pdf', methods=['GET'])
@jwt_required()
def export_expenses_pdf():
    """Export expenses to PDF"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        expenses = Expense.query.filter(
            Expense.company_id == user.company_id
        ).all()

        expense_data = [
            {
                'id': e.id,
                'project_name': e.project.name if e.project else '',
                'category': e.category,
                'description': e.description,
                'amount': e.amount,
                'date': e.date,
                'status': e.status,
                'vendor_name': e.vendor_name,
                'payment_method': e.payment_method
            }
            for e in expenses
        ]

        return PDFExporter.export_expenses(expense_data)

    except Exception as e:
        return jsonify({'error': 'Failed to export'}), 500


# ============================================================================
# VEHICLE CERTIFICATE REPORTS
# ============================================================================

@reports_bp.route('/vehicles/certificates', methods=['GET'])
@jwt_required()
def get_vehicle_certificate_report():
    """Get vehicle certificate expiry report"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        vehicles = Vehicle.query.filter(
            Vehicle.company_id == user.company_id
        ).all()

        expiring_soon = []
        expired = []

        now = datetime.now()
        thirty_days = now + timedelta(days=30)

        for vehicle in vehicles:
            certificates = [
                {'name': 'Insurance', 'expiry': vehicle.insurance_expiry},
                {'name': 'Registration', 'expiry': vehicle.registration_expiry},
                {'name': 'Fitness', 'expiry': vehicle.fitness_expiry},
                {'name': 'Pollution', 'expiry': vehicle.pollution_expiry},
                {'name': 'Road Tax', 'expiry': vehicle.road_tax_expiry},
                {'name': 'Permit', 'expiry': vehicle.permit_expiry}
            ]

            for cert in certificates:
                if cert['expiry']:
                    if cert['expiry'] < now:
                        expired.append({
                            'vehicle': vehicle.registration_number,
                            'certificate': cert['name'],
                            'expiry_date': str(cert['expiry'])
                        })
                    elif cert['expiry'] <= thirty_days:
                        expiring_soon.append({
                            'vehicle': vehicle.registration_number,
                            'certificate': cert['name'],
                            'expiry_date': str(cert['expiry']),
                            'days_remaining': (cert['expiry'] - now).days
                        })

        return jsonify({
            'totalVehicles': len(vehicles),
            'expiringCertificates': len(expiring_soon),
            'expiredCertificates': len(expired),
            'expiringList': expiring_soon,
            'expiredList': expired
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to generate report'}), 500


# ============================================================================
# PROJECT REPORTS
# ============================================================================

@reports_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_project_report():
    """Get project expense breakdown report"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        projects = Project.query.filter(
            Project.company_id == user.company_id
        ).all()

        project_data = []
        for project in projects:
            expenses = Expense.query.filter(
                Expense.project_id == project.id
            ).all()

            total_expense = sum(e.amount for e in expenses)

            project_data.append({
                'id': project.id,
                'name': project.name,
                'location': project.location,
                'status': project.status,
                'totalExpense': total_expense,
                'expenseCount': len(expenses),
                'avgExpense': total_expense / len(expenses) if expenses else 0
            })

        return jsonify({
            'projects': project_data,
            'totalProjects': len(projects),
            'totalExpenses': sum(p['totalExpense'] for p in project_data)
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to generate report'}), 500
