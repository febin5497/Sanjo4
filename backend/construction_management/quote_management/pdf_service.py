from io import BytesIO
from datetime import datetime
import json

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def generate_quote_pdf(quote):
    """
    Generate a PDF document for a quote
    Returns a BytesIO object containing the PDF
    """

    if not HAS_REPORTLAB:
        raise ImportError("reportlab is not installed. Install it with: pip install reportlab")

    # Create a BytesIO buffer
    buffer = BytesIO()

    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#27ae60'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4
    )

    # Title
    elements.append(Paragraph("QUOTATION", title_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Quote Header Info
    header_data = [
        [
            f"<b>Quote Number:</b> {quote.quote_number}",
            f"<b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d')}"
        ],
        [
            f"<b>Client ID:</b> {quote.client_id}",
            f"<b>Valid Until:</b> {quote.valid_until.strftime('%Y-%m-%d') if quote.valid_until else 'N/A'}"
        ],
        [
            f"<b>Supplier:</b> {quote.supplier_id or 'N/A'}",
            f"<b>Status:</b> {quote.status}"
        ]
    ]

    header_table = Table(header_data, colWidths=[3.5 * inch, 2.5 * inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Notes section
    if quote.notes:
        elements.append(Paragraph("<b>Notes</b>", heading_style))
        elements.append(Paragraph(quote.notes, normal_style))
        elements.append(Spacer(1, 0.2 * inch))

    # Items Table
    elements.append(Paragraph("<b>Quote Items</b>", heading_style))

    items_data = [['Description', 'Qty', 'Unit Price', 'Total']]

    for item in quote.items:
        items_data.append([
            item.description,
            f"{item.quantity}",
            f"${item.unit_price:.2f}",
            f"${item.total:.2f}"
        ])

    items_table = Table(items_data, colWidths=[3 * inch, 1 * inch, 1.25 * inch, 1.25 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(items_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Totals Section
    totals_data = [
        ['Subtotal:', f"${quote.subtotal:.2f}"],
        ['Tax ({0}%):'.format(quote.tax_rate * 100), f"${quote.tax_amount:.2f}"],
        ['<b>Total:</b>', f"<b>${quote.total:.2f}</b>"]
    ]

    totals_table = Table(totals_data, colWidths=[5 * inch, 1.5 * inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (0, -1), 9),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (1, 0), (1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
    ]))

    elements.append(totals_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Terms & Conditions
    if quote.terms_and_conditions:
        elements.append(Paragraph("<b>Terms & Conditions</b>", heading_style))
        elements.append(Paragraph(quote.terms_and_conditions, normal_style))

    elements.append(Spacer(1, 0.3 * inch))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#7f8c8d'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Quote #{quote.id}",
        footer_style
    ))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and return it
    buffer.seek(0)
    return buffer


def generate_quote_csv(quotes):
    """
    Generate a CSV export for quotes
    Returns a string containing CSV data
    """

    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Quote Number',
        'Client ID',
        'Supplier ID',
        'Status',
        'Subtotal',
        'Tax Amount',
        'Total',
        'Created At',
        'Valid Until'
    ])

    # Data
    for quote in quotes:
        writer.writerow([
            quote.quote_number,
            quote.client_id,
            quote.supplier_id or '',
            quote.status,
            f"${quote.subtotal:.2f}",
            f"${quote.tax_amount:.2f}",
            f"${quote.total:.2f}",
            quote.created_at.strftime('%Y-%m-%d') if quote.created_at else '',
            quote.valid_until.strftime('%Y-%m-%d') if quote.valid_until else ''
        ])

    return output.getvalue()
