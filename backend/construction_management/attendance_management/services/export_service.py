import csv
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch


class ExportService:
    """Service for exporting attendance records to CSV and PDF formats."""

    @staticmethod
    def generate_csv(records):
        """
        Generate CSV content from attendance records.

        Args:
            records: List of Attendance model instances

        Returns:
            CSV string content
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Staff ID',
            'Staff Name',
            'Date',
            'Present',
            'Half Day',
            'Night Shift',
            'Punch In',
            'Punch Out',
            'Hours Worked',
            'Overtime Hours',
            'Leave Reason'
        ])

        # Write records
        for record in records:
            staff_name = record.staff.name if record.staff else 'Unknown'
            punch_in = record.punch_in_time.strftime('%H:%M:%S') if hasattr(record, 'punch_in_time') and record.punch_in_time else '-'
            punch_out = record.punch_out_time.strftime('%H:%M:%S') if hasattr(record, 'punch_out_time') and record.punch_out_time else '-'

            # Calculate hours worked
            hours_worked = '-'
            if hasattr(record, 'punch_in_time') and hasattr(record, 'punch_out_time') and record.punch_in_time and record.punch_out_time:
                delta = record.punch_out_time - record.punch_in_time
                hours_worked = f"{delta.total_seconds() / 3600:.2f}"

            writer.writerow([
                record.staff_id,
                staff_name,
                record.date.strftime('%Y-%m-%d'),
                'Yes' if record.present else 'No',
                'Yes' if record.half_day else 'No',
                'Yes' if record.night_shift else 'No',
                punch_in,
                punch_out,
                hours_worked,
                f"{record.overtime_hours:.2f}" if record.overtime_hours else '0.00',
                record.leave_reason if record.leave_reason else '-'
            ])

        return output.getvalue()

    @staticmethod
    def generate_pdf(records, start_date_str, end_date_str):
        """
        Generate PDF content from attendance records.

        Args:
            records: List of Attendance model instances
            start_date_str: Start date string (YYYY-MM-DD)
            end_date_str: End date string (YYYY-MM-DD)

        Returns:
            PDF file content (bytes)
        """
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []

        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=12,
            alignment=1  # Center
        )
        title = Paragraph('Attendance Report', title_style)
        elements.append(title)

        # Date range
        date_info = Paragraph(
            f'<font size=10>Period: {start_date_str} to {end_date_str}</font>',
            styles['Normal']
        )
        elements.append(date_info)
        elements.append(Spacer(1, 0.2*inch))

        # Prepare table data
        table_data = [[
            'Staff ID',
            'Staff Name',
            'Date',
            'Present',
            'Half Day',
            'Night Shift',
            'OT Hours',
            'Leave Reason'
        ]]

        for record in records:
            staff_name = record.staff.name if record.staff else 'Unknown'

            table_data.append([
                str(record.staff_id),
                staff_name[:20],  # Truncate long names
                record.date.strftime('%Y-%m-%d'),
                '✓' if record.present else '✗',
                '✓' if record.half_day else '✗',
                '✓' if record.night_shift else '✗',
                f"{record.overtime_hours:.1f}" if record.overtime_hours else '0.0',
                (record.leave_reason[:15] + '...') if record.leave_reason and len(record.leave_reason) > 15 else (record.leave_reason or '-')
            ])

        # Create table with styling
        table = Table(table_data, colWidths=[0.8*inch, 1.2*inch, 0.9*inch, 0.7*inch, 0.7*inch, 0.75*inch, 0.7*inch, 1.0*inch])

        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),

            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Center align Staff ID column
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Center align Date column
            ('ALIGN', (3, 1), (5, -1), 'CENTER'),  # Center align boolean columns
            ('ALIGN', (6, 1), (6, -1), 'RIGHT'),   # Right align OT Hours column

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
        ]))

        elements.append(table)

        # Summary
        elements.append(Spacer(1, 0.2*inch))
        total_records = len(records)
        present_count = sum(1 for r in records if r.present)
        summary_text = f'Total Records: {total_records} | Present: {present_count}'
        elements.append(Paragraph(
            f'<font size=9><b>{summary_text}</b></font>',
            styles['Normal']
        ))

        # Build PDF
        doc.build(elements)
        output.seek(0)
        return output.getvalue()
