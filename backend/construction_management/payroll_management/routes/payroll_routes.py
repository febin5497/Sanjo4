from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from extensions import db
from payroll_management.models.payroll import PayrollCycle, PayrollRecord
from staff_management.models import Staff
from attendance_management.models import Attendance
from user_management.models import User
from admin_management.utils.activity_logger import log_entity_action
from utils.response_formatter import success_response, error_response, paginated_response
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import csv

payroll_bp = Blueprint('payroll', __name__)


@payroll_bp.route('/cycles', methods=['GET'])
@jwt_required()
def get_payroll_cycles():
    """Get all payroll cycles"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = PayrollCycle.query.filter_by(company_id=user.company_id).order_by(PayrollCycle.id.desc())
        paginated = query.paginate(page=page, per_page=per_page)

        data = {
            'cycles': [cycle.to_dict() for cycle in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages
        }

        return success_response(data, "Payroll cycles retrieved")

    except Exception as e:
        return error_response(str(e), 500)


@payroll_bp.route('/cycles', methods=['POST'])
@jwt_required()
def create_payroll_cycle():
    """Create new payroll cycle"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()

        month = data.get('month')
        year = data.get('year')

        if not month or not year:
            return error_response("Month and year required", 400)

        # Check if cycle already exists
        existing = PayrollCycle.query.filter_by(
            month=month, year=year, company_id=user.company_id
        ).first()

        if existing:
            return error_response("Payroll cycle already exists", 400)

        cycle = PayrollCycle(
            month=month,
            year=year,
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            company_id=user.company_id
        )

        db.session.add(cycle)
        db.session.commit()

        log_entity_action(
            user_id=current_user_id,
            entity_type='PayrollCycle',
            entity_id=cycle.id,
            action='create',
            description=f'Created payroll cycle for {month}/{year}'
        )

        return success_response(cycle.to_dict(), "Cycle created", 201)

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@payroll_bp.route('/cycles/<int:cycle_id>/calculate', methods=['POST'])
@jwt_required()
def calculate_payroll(cycle_id):
    """Calculate payroll from attendance"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        cycle = PayrollCycle.query.filter_by(
            id=cycle_id, company_id=user.company_id
        ).first()

        if not cycle:
            return error_response("Cycle not found", 404)

        # Get all staff members
        staff_members = Staff.query.filter_by(company_id=user.company_id).all()

        for staff in staff_members:
            # Get attendance from simple attendance table
            attendance_days = Attendance.query.filter(
                Attendance.staff_id == staff.id,
                Attendance.date >= cycle.start_date,
                Attendance.date <= cycle.end_date,
                Attendance.status.in_(['present', 'half_day'])
            ).count()

            # Also count photo-based attendance records (approved/completed)
            try:
                from attendance_management.models.attendance_record import AttendanceRecord
                photo_attendance_days = AttendanceRecord.query.filter(
                    AttendanceRecord.staff_id == staff.id,
                    AttendanceRecord.date >= cycle.start_date,
                    AttendanceRecord.date <= cycle.end_date,
                    AttendanceRecord.status.in_(['approved', 'completed'])
                ).count()
                # Use the higher count (avoids double-counting if both exist)
                attendance_days = max(attendance_days, photo_attendance_days)
            except Exception:
                pass  # attendance_records table may not exist yet

            # Calculate salary
            monthly_salary = staff.salary or 0
            days_in_month = 26  # Working days
            days_worked = min(attendance_days, days_in_month)

            gross_salary = (monthly_salary / days_in_month) * days_worked
            pf_amount = gross_salary * 0.12 if gross_salary > 15000 else 0
            esi_amount = gross_salary * 0.0075 if gross_salary < 21000 else 0
            tax_amount = max(0, (gross_salary - 50000) * 0.10) if gross_salary > 50000 else 0
            net_salary = gross_salary - pf_amount - esi_amount - tax_amount

            # Create or update payroll record
            record = PayrollRecord.query.filter_by(
                cycle_id=cycle_id, staff_id=staff.id
            ).first()

            if not record:
                record = PayrollRecord(cycle_id=cycle_id, staff_id=staff.id)
                db.session.add(record)

            record.days_worked = days_worked
            record.gross_salary = gross_salary
            record.pf_amount = pf_amount
            record.esi_amount = esi_amount
            record.tax_amount = tax_amount
            record.net_salary = net_salary

        cycle.status = 'calculated'
        db.session.commit()

        log_entity_action(
            user_id=current_user_id,
            entity_type='PayrollCycle',
            entity_id=cycle_id,
            action='calculate',
            description=f'Calculated payroll for cycle {cycle_id}'
        )

        return success_response(cycle.to_dict(), "Payroll calculated")

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@payroll_bp.route('/cycles/<int:cycle_id>/records', methods=['GET'])
@jwt_required()
def get_payroll_records(cycle_id):
    """Get payroll records for a cycle"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        records = PayrollRecord.query.filter_by(cycle_id=cycle_id).all()
        data = [rec.to_dict() for rec in records]

        return success_response(data, "Payroll records retrieved")

    except Exception as e:
        return error_response(str(e), 500)


@payroll_bp.route('/cycles/<int:cycle_id>/approve', methods=['POST'])
@jwt_required()
def approve_payroll(cycle_id):
    """Approve payroll cycle and create finance transactions"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        cycle = PayrollCycle.query.filter_by(
            id=cycle_id, company_id=user.company_id
        ).first()

        if not cycle:
            return error_response("Cycle not found", 404)

        if cycle.status != 'calculated':
            return error_response("Only calculated cycles can be approved", 400)

        cycle.status = 'approved'
        cycle.approved_by_id = current_user_id
        cycle.approved_at = datetime.utcnow()

        db.session.commit()

        # Create CashTransaction for each payroll record (salary expense)
        try:
            from finance_management.models.cash_transaction import CashTransaction
            from staff_management.models import Staff as StaffModel

            records = PayrollRecord.query.filter_by(cycle_id=cycle_id).all()
            tx_count = 0
            for record in records:
                if record.net_salary and record.net_salary > 0:
                    staff = StaffModel.query.get(record.staff_id)
                    staff_name = f"{staff.first_name} {staff.last_name}".strip() if staff else "Unknown"

                    cash_tx = CashTransaction(
                        amount=record.net_salary,
                        type='expense',
                        category='Salary',
                        date=cycle.end_date,
                        description=f"Salary - {staff_name} - {cycle.month}/{cycle.year}",
                        staff_id=record.staff_id,
                        staff_name=staff_name,
                        created_by=int(current_user_id)
                    )
                    db.session.add(cash_tx)
                    tx_count += 1

            db.session.commit()
            print(f"Created {tx_count} CashTransaction records for payroll cycle {cycle_id}")
        except Exception as tx_error:
            print(f"Warning: Could not create cash transactions for payroll: {str(tx_error)}")
            db.session.rollback()

        log_entity_action(
            user_id=current_user_id,
            entity_type='PayrollCycle',
            entity_id=cycle_id,
            action='approve',
            description=f'Approved payroll cycle {cycle_id}'
        )

        # Notify all staff members in the payroll cycle
        try:
            from notifications.models import Notification
            from staff_management.models import Staff as StaffModel
            records = PayrollRecord.query.filter_by(cycle_id=cycle_id).all()
            for record in records:
                staff = StaffModel.query.get(record.staff_id)
                if staff and staff.user_id:
                    notif = Notification(
                        user_id=staff.user_id,
                        company_id=user.company_id,
                        title='Salary Approved',
                        message=f'Your salary for {cycle.month}/{cycle.year} has been approved. Net pay: Rs.{record.net_salary:.2f}',
                        notification_type='payroll',
                        related_model='payroll',
                        related_id=record.id
                    )
                    db.session.add(notif)
            db.session.commit()
            print(f"[NOTIFICATION] Payroll notifications sent for cycle #{cycle_id}")
        except Exception as e:
            print(f"[NOTIFICATION ERROR] Could not send payroll notifications: {str(e)}")
            db.session.rollback()

        return success_response(cycle.to_dict(), "Payroll approved")

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@payroll_bp.route('/cycles/<int:cycle_id>/reject', methods=['POST'])
@jwt_required()
def reject_payroll(cycle_id):
    """Reject payroll cycle with reason"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json(silent=True) or {}

        cycle = PayrollCycle.query.filter_by(
            id=cycle_id, company_id=user.company_id
        ).first()

        if not cycle:
            return error_response("Cycle not found", 404)

        cycle.status = 'rejected'
        cycle.rejection_reason = data.get('reason', '')
        cycle.rejected_by_id = current_user_id
        cycle.rejected_at = datetime.utcnow()

        db.session.commit()

        log_entity_action(
            user_id=current_user_id,
            entity_type='PayrollCycle',
            entity_id=cycle_id,
            action='reject',
            description=f'Rejected payroll cycle {cycle_id}: {data.get("reason", "")}'
        )

        return success_response(cycle.to_dict(), "Payroll rejected")

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@payroll_bp.route('/cycles/<int:cycle_id>/generate-slips', methods=['POST'])
@jwt_required()
def generate_salary_slips(cycle_id):
    """Generate PDF salary slips for all staff in cycle"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        cycle = PayrollCycle.query.filter_by(
            id=cycle_id, company_id=user.company_id
        ).first()

        if not cycle:
            return error_response("Cycle not found", 404)

        records = PayrollRecord.query.filter_by(cycle_id=cycle_id).all()

        if not records:
            return error_response("No payroll records found for this cycle", 404)

        # Create ZIP file with individual PDFs
        pdf_buffer = BytesIO()

        # Create a combined PDF with all salary slips
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        for record in records:
            staff = Staff.query.get(record.staff_id)
            if not staff:
                continue

            # Add salary slip for this staff member
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=14,
                textColor=colors.HexColor('#0052CC'),
                spaceAfter=6,
            )

            story.append(Paragraph(f"SALARY SLIP - {staff.name}", title_style))
            story.append(Paragraph(f"Month: {cycle.month}/{cycle.year}", styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))

            # Create slip data
            slip_data = [
                ['Description', 'Amount'],
                ['Days Worked', str(record.days_worked or 0)],
                ['Gross Salary', f"₹{record.gross_salary or 0:.2f}"],
                ['Deductions:', ''],
                ['  PF (12%)', f"₹{record.pf_amount or 0:.2f}"],
                ['  ESI (0.75%)', f"₹{record.esi_amount or 0:.2f}"],
                ['  Income Tax', f"₹{record.tax_amount or 0:.2f}"],
                ['Net Salary', f"₹{record.net_salary or 0:.2f}"],
            ]

            table = Table(slip_data, colWidths=[3 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f5ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ]))

            story.append(table)
            story.append(Spacer(1, 0.4 * inch))

        # Build PDF
        doc.build(story)
        pdf_buffer.seek(0)

        log_entity_action(
            user_id=current_user_id,
            entity_type='PayrollCycle',
            entity_id=cycle_id,
            action='generate_slips',
            description=f'Generated salary slips for cycle {cycle_id}'
        )

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Salary_Slips_{cycle.month}_{cycle.year}.pdf'
        )

    except Exception as e:
        return error_response(f"Error generating salary slips: {str(e)}", 500)


@payroll_bp.route('/cycles/<int:cycle_id>/transfer', methods=['POST'])
@jwt_required()
def export_bank_transfer(cycle_id):
    """Export bank transfer file (CSV) for payroll disbursement"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        cycle = PayrollCycle.query.filter_by(
            id=cycle_id, company_id=user.company_id
        ).first()

        if not cycle:
            return error_response("Cycle not found", 404)

        records = PayrollRecord.query.filter_by(cycle_id=cycle_id).all()

        if not records:
            return error_response("No payroll records found for this cycle", 404)

        # Create CSV buffer
        csv_buffer = BytesIO()
        csv_text = 'Staff Name,Account Number,IFSC Code,Net Amount,Payroll Record ID\n'

        for record in records:
            staff = Staff.query.get(record.staff_id)
            if not staff:
                continue

            # Get bank details from staff record (if available)
            account_number = getattr(staff, 'account_number', '')
            ifsc_code = getattr(staff, 'ifsc_code', '')

            if not account_number or not ifsc_code:
                # Skip staff without bank details
                continue

            net_amount = record.net_salary or 0
            csv_text += f'{staff.name},{account_number},{ifsc_code},{net_amount:.2f},{record.id}\n'

        csv_buffer.write(csv_text.encode())
        csv_buffer.seek(0)

        log_entity_action(
            user_id=current_user_id,
            entity_type='PayrollCycle',
            entity_id=cycle_id,
            action='export_transfer',
            description=f'Exported bank transfer file for cycle {cycle_id}'
        )

        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'Bank_Transfer_{cycle.month}_{cycle.year}.csv'
        )

    except Exception as e:
        return error_response(f"Error exporting bank transfer: {str(e)}", 500)
