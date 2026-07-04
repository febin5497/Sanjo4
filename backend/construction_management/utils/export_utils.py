"""
Export Utilities for Reports
Support for CSV, PDF, and Excel exports
"""

import csv
import json
from io import StringIO, BytesIO
from datetime import datetime
from flask import make_response
import json


class CSVExporter:
    """Export data to CSV format"""

    @staticmethod
    def export_staff(staff_list, filename='staff_report.csv'):
        """Export staff data to CSV"""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'ID', 'Name', 'Email', 'Phone', 'Role', 'Department',
            'Salary', 'PF', 'ESI', 'Joining Date'
        ])

        writer.writeheader()
        for staff in staff_list:
            writer.writerow({
                'ID': staff.get('id', ''),
                'Name': staff.get('name', ''),
                'Email': staff.get('email', ''),
                'Phone': staff.get('phone', ''),
                'Role': staff.get('role', ''),
                'Department': staff.get('department', ''),
                'Salary': staff.get('salary', ''),
                'PF': staff.get('pf', ''),
                'ESI': staff.get('esi', ''),
                'Joining Date': staff.get('joining_date', '')
            })

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'text/csv'
        return response

    @staticmethod
    def export_expenses(expense_list, filename='expense_report.csv'):
        """Export expense data to CSV"""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'ID', 'Project', 'Category', 'Description', 'Amount',
            'Date', 'Status', 'Vendor', 'Payment Method'
        ])

        writer.writeheader()
        for expense in expense_list:
            writer.writerow({
                'ID': expense.get('id', ''),
                'Project': expense.get('project_name', ''),
                'Category': expense.get('category', ''),
                'Description': expense.get('description', ''),
                'Amount': expense.get('amount', ''),
                'Date': expense.get('date', ''),
                'Status': expense.get('status', ''),
                'Vendor': expense.get('vendor_name', ''),
                'Payment Method': expense.get('payment_method', '')
            })

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'text/csv'
        return response

    @staticmethod
    def export_vehicles(vehicle_list, filename='vehicle_report.csv'):
        """Export vehicle data to CSV"""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'ID', 'Registration Number', 'Make', 'Model', 'Year',
            'Capacity', 'Status', 'Insurance Expiry', 'Registration Expiry',
            'Fitness Expiry'
        ])

        writer.writeheader()
        for vehicle in vehicle_list:
            writer.writerow({
                'ID': vehicle.get('id', ''),
                'Registration Number': vehicle.get('registration_number', ''),
                'Make': vehicle.get('make', ''),
                'Model': vehicle.get('model', ''),
                'Year': vehicle.get('year', ''),
                'Capacity': vehicle.get('capacity', ''),
                'Status': vehicle.get('status', ''),
                'Insurance Expiry': vehicle.get('insurance_expiry', ''),
                'Registration Expiry': vehicle.get('registration_expiry', ''),
                'Fitness Expiry': vehicle.get('fitness_expiry', '')
            })

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'text/csv'
        return response


class PDFExporter:
    """Export data to PDF format"""

    @staticmethod
    def export_staff(staff_data, filename='staff_report.pdf'):
        """Export staff report to PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#007AFF'),
                spaceAfter=30,
                alignment=1  # Center
            )
            elements.append(Paragraph('Staff Management Report', title_style))
            elements.append(Spacer(1, 0.2*inch))

            # Summary
            summary_data = [
                ['Metric', 'Value'],
                ['Total Staff', str(len(staff_data))],
                ['Report Date', datetime.now().strftime('%Y-%m-%d')]
            ]
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))

            # Staff Table
            table_data = [['ID', 'Name', 'Email', 'Role', 'Department', 'Salary']]
            for staff in staff_data[:50]:  # Limit to 50 for PDF
                table_data.append([
                    str(staff.get('id', '')),
                    staff.get('name', '')[:20],
                    staff.get('email', '')[:20],
                    staff.get('role', ''),
                    staff.get('department', ''),
                    f"₹{staff.get('salary', 0)}"
                ])

            staff_table = Table(table_data)
            staff_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(staff_table)

            # Build PDF
            doc.build(elements)
            buffer.seek(0)

            response = make_response(buffer.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = 'application/pdf'
            return response

        except ImportError:
            return None

    @staticmethod
    def export_expenses(expense_data, filename='expense_report.pdf'):
        """Export expense report to PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.lib import colors

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            elements.append(Paragraph('Expense Management Report', styles['Title']))
            elements.append(Spacer(1, 0.3*inch))

            # Summary Stats
            summary_data = [
                ['Metric', 'Value'],
                ['Total Expenses', f"₹{sum(e.get('amount', 0) for e in expense_data)}"],
                ['Total Count', str(len(expense_data))],
                ['Report Date', datetime.now().strftime('%Y-%m-%d')]
            ]
            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3*inch))

            # Expense Table
            table_data = [['ID', 'Category', 'Description', 'Amount', 'Status']]
            for exp in expense_data[:50]:  # Limit to 50
                table_data.append([
                    str(exp.get('id', '')),
                    exp.get('category', ''),
                    exp.get('description', '')[:20],
                    f"₹{exp.get('amount', 0)}",
                    exp.get('status', '')
                ])

            exp_table = Table(table_data)
            exp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8)
            ]))
            elements.append(exp_table)

            # Build
            doc.build(elements)
            buffer.seek(0)

            response = make_response(buffer.getvalue())
            response.headers['Content-Disposition'] = f'attachment; filename={filename}'
            response.headers['Content-Type'] = 'application/pdf'
            return response

        except ImportError:
            return None


class JSONExporter:
    """Export data to JSON format"""

    @staticmethod
    def export_data(data, filename='report.json'):
        """Export data to JSON"""
        json_str = json.dumps(data, indent=2, default=str)
        response = make_response(json_str)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        response.headers['Content-Type'] = 'application/json'
        return response
