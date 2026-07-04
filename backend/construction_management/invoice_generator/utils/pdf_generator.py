from fpdf import FPDF
import io

def generate_invoice_pdf(invoice):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Unizion Construction Pvt Ltd", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Invoice ID: {invoice.id}", ln=True)
    pdf.cell(200, 10, txt=f"Customer: {invoice.customer}", ln=True)
    pdf.cell(200, 10, txt=f"Amount: ₹{invoice.total_amount}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {invoice.date.strftime('%Y-%m-%d')}", ln=True)

    # You can loop over invoice items if needed
    for item in invoice.items:
        pdf.cell(200, 10, txt=f"{item.description}: ₹{item.total}", ln=True)
    
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output
