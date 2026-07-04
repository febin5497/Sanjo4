# Invoice System Design - Complete Guide

## File Paths & Storage

### Company Logo Path
**Database**: `companies.logo_url`
**Upload Directory**: `/uploads/logos/`
**Full Path**: `http://localhost:5000/uploads/logos/{company_id}/logo.png`
**Example**: `http://localhost:5000/uploads/logos/1/logo.png`

### Invoice Types
- **Sales Invoice**: To clients/customers
- **Purchase Invoice**: From vendors/suppliers

---

## Invoice Configuration

### Company Settings (In Database)
Located in `company_settings` table with these settings:

```
Setting Key: "invoice_gst_enabled"
Setting Value: "true" or "false"
Description: Enable/disable GST format on all invoices

Setting Key: "invoice_show_project_name"
Setting Value: "true" or "false"
Description: Show project name on invoices

Setting Key: "invoice_tax_type"
Setting Value: "GST" | "VAT" | "NONE"
Description: Type of tax to use

Setting Key: "invoice_cgst_rate"
Setting Value: "9"
Description: CGST percentage (Indian)

Setting Key: "invoice_sgst_rate"
Setting Value: "9"
Description: SGST percentage (Indian)

Setting Key: "invoice_igst_rate"
Setting Value: "18"
Description: IGST percentage (for Inter-state)
```

---

## Invoice Template Structure

### Header Section
```
┌─────────────────────────────────────────────────────┐
│ [Company Logo]  COMPANY NAME                        │
│                 Address Line 1                      │
│                 Address Line 2                      │
│                 Phone: +91-XXXX-XXXXX               │
│                 Email: company@example.com          │
│                 GST: XXXXXXXXXXXXXXXXX              │
└─────────────────────────────────────────────────────┘
```

### Invoice Details Section
```
┌─────────────────────────────────────────────────────┐
│ SALES INVOICE / PURCHASE INVOICE                   │
│                                                    │
│ Invoice #: INV-2026-001         Date: 01-Apr-2026 │
│ Due Date: 30-Apr-2026           [Project: Name]   │
└─────────────────────────────────────────────────────┘
```

### Party Details
```
┌──────────────────────┬──────────────────────────────┐
│ FROM:                │ TO:                          │
│ Company Name         │ Customer/Vendor Name         │
│ Address              │ Address                      │
│ Phone: XXXXXX        │ Phone: XXXXXX               │
│ Email: XXXXX         │ Email: XXXXX                │
│ GST: XXXXXXX         │ GST: XXXXXXX                │
└──────────────────────┴──────────────────────────────┘
```

### Line Items Table
```
┌────┬─────────────────┬────────┬────────┬──────────┐
│ No │ Description     │ Qty    │ Rate   │ Amount   │
├────┼─────────────────┼────────┼────────┼──────────┤
│ 1  │ Item Name       │ 5      │ 1000   │ 5000.00  │
│ 2  │ Service         │ 2      │ 5000   │ 10000.00 │
└────┴─────────────────┴────────┴────────┴──────────┘
```

### Totals Section (WITH GST)
```
┌──────────────────────────────────┐
│ Subtotal:           Rs. 15,000.00│
│ CGST (9%):          Rs. 1,350.00 │
│ SGST (9%):          Rs. 1,350.00 │
│ ────────────────────────────────  │
│ Total Amount:       Rs. 17,700.00│
│ ────────────────────────────────  │
│ [Retention: Rs. 885.00] (Optional)
│                                  │
│ NET PAYABLE:        Rs. 16,815.00│
└──────────────────────────────────┘
```

### Totals Section (WITHOUT GST)
```
┌──────────────────────────────────┐
│ Subtotal:           Rs. 15,000.00│
│ ────────────────────────────────  │
│ Total Amount:       Rs. 15,000.00│
└──────────────────────────────────┘
```

### Payment Details Section
```
┌──────────────────────────────────────┐
│ PAYMENT DETAILS                      │
│                                      │
│ Bank Name: XXXXXXXX Bank             │
│ Account Name: Company Name           │
│ Account Number: XXXXXXXXXX           │
│ IFSC Code: XXXXXX00001               │
│                                      │
│ Payment Terms: Net 30 days           │
│ Payment Due Date: 30-Apr-2026        │
└──────────────────────────────────────┘
```

### Footer Section
```
┌──────────────────────────────────────┐
│ TERMS & CONDITIONS                   │
│ - Payment should be received by due   │
│   date to avoid penalties             │
│ - Please mention invoice # in payment │
│ - For queries, contact: XXXXXX        │
│                                      │
│ Authorized By: ________________      │
│ Date: ________________               │
└──────────────────────────────────────┘
```

---

## Action Buttons

### Web Display
```
[Print] [Download PDF] [Email]
```

### Print Styles
- A4 size format
- Optimized for laser/inkjet printers
- No website header/footer
- Proper page breaks

### PDF Download
- Automatic filename: `INV-2026-001.pdf`
- Preserves all formatting
- Includes all details
- Can be stored in uploads folder

### Email
- Opens email client or shows compose box
- Pre-fills subject: `Invoice INV-2026-001`
- Invoice PDF attached or link provided

---

## Invoice Types & Fields

### SALES INVOICE (To Clients)
**From**: Your Company
**To**: Customer Details
**Items**: Products/Services sold
**Total**: Amount client needs to pay

### PURCHASE INVOICE (From Vendors)
**From**: Supplier/Vendor
**To**: Your Company
**Items**: Products/Services purchased
**Total**: Amount you need to pay

---

## Database Fields

### New Invoice Table
```python
class Invoice(db.Model):
    # Identifiers
    id
    invoice_number (INV-2026-001)
    invoice_date
    due_date

    # Type & Status
    invoice_type (Sales / Purchase)
    status (Draft / Sent / Paid / Overdue)

    # Parties
    company_id
    customer_id (for Sales)
    vendor_id (for Purchase)

    # Amounts
    subtotal
    cgst_amount
    sgst_amount
    igst_amount
    total_amount
    retention_amount (optional)
    net_payable

    # GST Settings
    gst_applicable (boolean)
    cgst_rate
    sgst_rate
    igst_rate

    # Project
    project_id (optional)
    project_name

    # Payment
    payment_terms
    payment_method
    paid_date (nullable)

    # Audit
    created_by_id
    created_at
    updated_at
```

---

## Invoice Generation Flow

### Step 1: Select Invoice Type
- Sales Invoice OR Purchase Invoice

### Step 2: Select Party
- Customer/Vendor

### Step 3: Add Line Items
- Product/Service
- Quantity
- Rate
- (Amount auto-calculated)

### Step 4: Configure GST
- Enable/Disable GST (from company settings)
- Select state (for CGST/SGST/IGST)
- Rates auto-filled from settings

### Step 5: Add Optional Details
- Project name (if enabled)
- Retention amount
- Payment terms
- Notes

### Step 6: Preview & Generate
- Preview invoice
- Print
- Download PDF
- Email

---

## GST Configuration Options

### Option 1: WITH GST (Indian Tax)
```
Subtotal: Rs. 10,000
CGST (9%): Rs. 900
SGST (9%): Rs. 900
─────────────────
Total: Rs. 11,800
```

### Option 2: WITHOUT GST
```
Subtotal: Rs. 10,000
─────────────────
Total: Rs. 10,000
```

### Option 3: Custom Tax
```
Subtotal: Rs. 10,000
Tax (X%): Rs. XXX
─────────────────
Total: Rs. XXXXX
```

---

## API Endpoints (To Be Created)

### Invoice CRUD
```
POST   /api/finance/invoices                    (Create invoice)
GET    /api/finance/invoices                    (List invoices)
GET    /api/finance/invoices/{id}               (Get invoice)
PUT    /api/finance/invoices/{id}               (Update invoice)
DELETE /api/finance/invoices/{id}               (Delete invoice)
```

### Invoice Actions
```
GET    /api/finance/invoices/{id}/preview       (Preview HTML)
GET    /api/finance/invoices/{id}/pdf           (Download PDF)
POST   /api/finance/invoices/{id}/email         (Send email)
POST   /api/finance/invoices/{id}/mark-paid     (Mark as paid)
```

### Settings
```
GET    /api/company/settings/invoice            (Get invoice settings)
PUT    /api/company/settings/invoice            (Update invoice settings)
```

---

## Frontend Components (To Be Created)

### Pages
- `InvoiceListPage.jsx` - List all invoices
- `InvoiceCreatePage.jsx` - Create new invoice
- `InvoiceDetailPage.jsx` - View/edit invoice
- `InvoicePreviewPage.jsx` - Preview before sending

### Components
- `InvoiceTemplate.jsx` - Reusable invoice display
- `InvoiceForm.jsx` - Form for creating/editing
- `LineItemsTable.jsx` - Add/edit line items
- `GSTConfigPanel.jsx` - Configure GST settings

### Features
- Print button (uses CSS @media print)
- Download PDF button (uses jsPDF/html2pdf library)
- Email button (opens email compose or API call)
- Share link button (generates shareable link)

---

## Technology Stack

### Frontend
- React (Display)
- Tailwind CSS (Styling)
- html2pdf or jsPDF (PDF generation)
- React-to-print (Print functionality)

### Backend
- Flask (API)
- SQLAlchemy (Database)
- reportlab or weasyprint (PDF generation)
- Email library (Email sending)

### Storage
- `/uploads/invoices/` - Invoice PDFs
- `/uploads/logos/` - Company logos
- Database - Invoice details

---

## Implementation Priority

**Phase 1** (Now):
- [ ] Invoice display template (HTML)
- [ ] Print functionality
- [ ] Basic invoice CRUD

**Phase 2** (Next):
- [ ] PDF download
- [ ] Email functionality
- [ ] GST configuration UI

**Phase 3** (Future):
- [ ] Recurring invoices
- [ ] Invoice templates
- [ ] Automated reminders
- [ ] Payment tracking

---

## Summary

**Company Logo**:
- Path: `company.logo_url`
- Upload to: `/uploads/logos/{company_id}/logo.png`
- Access: `http://localhost:5000/uploads/logos/{company_id}/logo.png`

**GST Options**:
- Enable/Disable: via company settings
- Without GST: Just show subtotal and total
- With GST: Show CGST + SGST + IGST

**Project Name**:
- Optional field (enable/disable in settings)
- Shows in invoice header if enabled

**Invoice Types**:
- Sales Invoice (to customers)
- Purchase Invoice (from vendors)

**Output Formats**:
- Web Display (browser view)
- Print (uses print stylesheet)
- PDF Download (saved file)
- Email (sends via email)
