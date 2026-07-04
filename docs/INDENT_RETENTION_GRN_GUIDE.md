# INDENT | RETENTION | GRN - Complete Guide

## Overview
Three critical procurement and financial concepts that work together in the construction management system to control material procurement, track deliveries, and manage payment retention.

---

## 1. INDENT (PURCHASE INDENT)

### **What is a Purchase Indent?**

A Purchase Indent is a **formal request document** for materials/items needed on a construction project. It's the first step in the procurement process.

**Key Role:** Material Request & Requirement Planning

### **Indent Workflow**

```
PROJECT MANAGER IDENTIFIES NEED
        ↓
CREATE INDENT
├─ Indent Number (auto-generated)
├─ Project Assignment
├─ List of Materials Needed
├─ Quantity & Estimated Cost
└─ Required By Date
        ↓
SUBMIT FOR APPROVAL
        ↓
[Status: SUBMITTED]
        ↓
FINANCE/MANAGER REVIEWS
├─ Budget check
├─ Necessity verification
└─ Cost approval
        ↓
├─→ APPROVED → [Status: APPROVED]
│             ↓
│         CREATE PURCHASE ORDER (PO)
│             ↓
│         [Status: PO_CREATED]
│
└─→ REJECTED → [Status: REJECTED]
               ↓
            Resubmit or revise
```

### **Indent Structure**

```
INDENT HEADER
├─ Indent Number: IND/2026/001
├─ Project: Project A
├─ Required Date: 2026-04-10
├─ Status: Approved
├─ Requested By: Project Manager (John)
└─ Approval Date: 2026-04-01

INDENT ITEMS (Line Items)
├─ Item 1: Cement - 100 bags @ ₹450 = ₹45,000
├─ Item 2: Steel - 50 tons @ ₹60,000 = ₹3,000,000
├─ Item 3: Sand - 200 cubic meters @ ₹2,000 = ₹400,000
└─ Item 4: Bricks - 10,000 units @ ₹15 = ₹150,000

TOTAL INDENT VALUE: ₹3,595,000
```

### **Indent Database Fields**

| Field | Purpose | Example |
|-------|---------|---------|
| `indent_number` | Unique ID | IND/2026/001 |
| `indent_date` | When created | 2026-04-01 |
| `required_by_date` | When needed | 2026-04-10 |
| `description` | What needed | "Materials for foundation" |
| `justification` | Why needed | "Excavation phase requires..." |
| `status` | Current state | draft, submitted, approved, po_created |
| `approved_by_id` | Who approved | User ID |
| `project_id` | Which project | Project ID |

### **Indent Status States**

```
DRAFT → SUBMITTED → APPROVED → PO_CREATED → COMPLETED
            ↓                        ↑
            └────→ REJECTED ─────────┘
```

| Status | Meaning | Can Edit? |
|--------|---------|-----------|
| **draft** | Not yet submitted | Yes |
| **submitted** | Awaiting approval | No |
| **approved** | Ready for PO | No |
| **po_created** | PO created from indent | No |
| **completed** | All items received | No |
| **rejected** | Approval denied | Yes (resubmit) |

### **Indent Items**

Each indent contains multiple line items:

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | Item name | Cement Bags |
| `quantity` | How many | 100 |
| `unit` | Unit of measure | bags, tons, meters, etc. |
| `estimated_rate` | Expected price per unit | ₹450 |
| `estimated_cost` | Total for item | ₹45,000 |
| `notes` | Special requirements | "OPC 53 grade only" |

### **Indent Role in Workflow**

```
INDENT APPROVAL
     ↓
SIGNALS BUDGET COMMITMENT
     ↓
CREATES PO (Purchase Order)
     ↓
VENDOR FULFILLS
     ↓
CREATES GRN (Goods Receipt Note)
     ↓
MATCHES INVOICE
     ↓
PAYMENT (with Retention)
```

---

## 2. RETENTION (PAYMENT RETENTION)

### **What is Retention?**

Retention is a **percentage of payment withheld** from vendor invoices until project completion or terms are met. It's a financial safeguard.

**Key Role:** Quality Assurance & Performance Guarantee

### **Retention Concept**

```
INVOICE TOTAL: ₹1,000,000
RETENTION PERCENTAGE: 5%
RETENTION AMOUNT: ₹50,000

PAYMENT RELEASED: ₹950,000
AMOUNT HELD: ₹50,000

STATUS: Held until:
├─ Project completion
├─ All defects fixed
├─ Warranty period expires
└─ Final inspection passes
```

### **Why Retention?**

1. **Quality Control** - Incentivizes vendor to maintain quality
2. **Defect Warranty** - Covers repairs if items fail
3. **Performance** - Ensures timely delivery
4. **Financial Security** - Protection against vendor insolvency
5. **Compliance** - Common in construction contracts

### **Retention in Invoice**

```
INVOICE DETAILS
├─ Line Items Total: ₹1,000,000
├─ Taxes: ₹180,000
├─ Gross Total: ₹1,180,000
│
├─ RETENTION CALCULATION
│  ├─ Retention %: 5%
│  └─ Retention Amount: ₹59,000 (5% of ₹1,180,000)
│
├─ PAYMENT CALCULATION
│  ├─ Amount to Pay: ₹1,121,000
│  └─ Amount to Hold: ₹59,000
│
└─ INVOICE SUMMARY
   ├─ Invoice Total: ₹1,180,000
   ├─ Less Retention: -₹59,000
   └─ Net Payment: ₹1,121,000
```

### **Retention Database Fields**

| Field | Purpose | Example |
|-------|---------|---------|
| `retention_percentage` | % to hold | 5 |
| `retention_amount` | Amount held | ₹59,000 |
| `retention_status` | Status | pending, released |
| `retention_released_date` | When released | 2026-05-15 |

### **Retention Workflow**

```
INVOICE CREATED
        ↓
CALCULATE RETENTION
├─ Amount = Invoice Total × Retention %
└─ Typical: 5-10% in construction
        ↓
PAYMENT APPROVAL
├─ Amount to Pay = Invoice - Retention
└─ Retention = Held amount
        ↓
[Status: PENDING] - Amount is held
        ↓
CONDITIONS MET
├─ Project complete
├─ Defect warranty ends
└─ Final inspection passed
        ↓
RELEASE RETENTION
├─ Date recorded
├─ Amount released
└─ [Status: RELEASED]
        ↓
VENDOR RECEIVES FULL PAYMENT
├─ Original retention + interest (if applicable)
└─ Completes transaction
```

### **Typical Retention Scenarios**

**Construction Project Example:**
```
Project Duration: 6 months
Invoice Timeline: Monthly invoices
Retention: 5% held from each invoice

Month 1: Pay 95%, Hold 5%
Month 2: Pay 95%, Hold 5%
Month 3: Pay 95%, Hold 5%
Month 4: Pay 95%, Hold 5%
Month 5: Pay 95%, Hold 5%
Month 6: Pay 100% + Release all held amounts
   Total Held Released = 5 invoices × 5% = 25% of one invoice

Project Complete: Release all retentions
```

### **Retention Scenarios**

| Scenario | Retention | Held Until |
|----------|-----------|-----------|
| **Normal Vendor** | 5% | Project completion |
| **New/Unverified** | 10% | Extended warranty period |
| **High-Risk Item** | 15% | 6-month post-delivery |
| **Repeat Vendor** | 2% | 30 days post-delivery |
| **Critical Material** | 10% | Performance verified |

---

## 3. GRN (GOODS RECEIPT NOTE)

### **What is a GRN?**

A Goods Receipt Note (GRN) is an **official record document** created when materials are physically received at the project site. It tracks what was received, when, and in what condition.

**Key Role:** Goods Receipt Tracking & Quality Verification

### **GRN Purpose**

```
VENDOR SHIPS MATERIALS
        ↓
MATERIALS ARRIVE AT SITE
        ↓
CREATE GRN
├─ Record what arrived
├─ Quantity received
├─ Quality assessment
└─ Acceptance or rejection
        ↓
GRN BECOMES OFFICIAL RECORD
├─ Matched against PO
├─ Matched against Invoice
└─ Used for reconciliation
```

### **GRN Workflow**

```
MATERIALS DELIVERED
        ↓
[Status: RECEIVED]
        ↓
SITE MANAGER CREATES GRN
├─ GRN Number (auto-generated)
├─ Delivery Date
├─ Vehicle Number & Driver
├─ Supplier Reference
└─ List of Items Received
        ↓
QUALITY CHECK
├─ Inspect materials
├─ Check for damage
├─ Verify quantity
└─ [Status: INSPECTED]
        ↓
QUALITY DECISION
├─→ PASS → ACCEPT → [Status: ACCEPTED]
│                    ↓
│         Recorded as received
│         Ready for use
│         Ready to match invoice
│
├─→ FAIL → REJECT → [Status: REJECTED]
│                   ↓
│         Create credit note
│         Send back to vendor
│         Request replacement
│
└─→ PARTIAL → Accept some, reject some
             ↓
         Record discrepancy
         Partial invoice acceptance
```

### **GRN Structure**

```
GRN HEADER
├─ GRN Number: GRN/2026/001
├─ Related PO: PO/2026/001
├─ Receipt Date: 2026-04-05
├─ Status: Accepted
├─ Vehicle: TR-KA-123
└─ Driver: Ramesh Kumar

DELIVERY DETAILS
├─ Supplier Reference: INV-2026-123
├─ Delivery Address: Project Site, Location
└─ Received By: Site Manager (Anil)

GRN ITEMS (What was received)
├─ Item 1: Cement Bags
│  ├─ Ordered: 100 bags
│  ├─ Received: 100 bags
│  ├─ Damaged: 0 bags
│  ├─ Status: OK ✓
│  └─ Quality Notes: "All sealed, good condition"
│
├─ Item 2: Steel Rods
│  ├─ Ordered: 50 tons
│  ├─ Received: 49.5 tons
│  ├─ Damaged: 0.5 tons (bent)
│  ├─ Status: PARTIAL ⚠
│  └─ Quality Notes: "Some rods bent, requesting replacement"
│
└─ Item 3: Sand
   ├─ Ordered: 200 m³
   ├─ Received: 200 m³
   ├─ Damaged: 0 m³
   ├─ Status: OK ✓
   └─ Quality Notes: "Correct grade, clean"

QUALITY ASSESSMENT
├─ Overall Status: PARTIAL (some items have issues)
├─ Quality Check Date: 2026-04-05
├─ Inspected By: Anil Kumar (Site Manager)
└─ Quality Notes: "Steel needs partial replacement for bent units"
```

### **GRN Database Fields**

| Field | Purpose | Example |
|-------|---------|---------|
| `grn_number` | Unique ID | GRN/2026/001 |
| `purchase_order_id` | Linked PO | PO ID |
| `receipt_date` | When received | 2026-04-05 |
| `vehicle_number` | Delivery vehicle | TR-KA-123 |
| `driver_name` | Driver name | Ramesh Kumar |
| `supplier_reference` | Vendor invoice ref | SUP-INV-2026 |
| `quality_check_status` | QC result | pending, pass, fail, partial |
| `status` | Overall status | received, inspected, accepted, rejected |

### **GRN Items**

Each GRN contains items received:

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | Item name | Cement Bags |
| `quantity_ordered` | Expected qty | 100 |
| `quantity_received` | Actually received | 100 |
| `unit` | Unit of measure | bags |
| `is_damaged` | Any damage? | false/true |
| `damaged_quantity` | How many damaged | 0 |
| `quality_remarks` | Inspection notes | "All good" |

### **GRN Status States**

```
RECEIVED → INSPECTED → ACCEPTED
                            ↓
                    Used in production
                    Matched to invoice
                    Ready for payment

             ↓ (Issues found)

          → REJECTED
             ↓
        Request replacement
        Credit note issued
        Return process
```

| Status | Meaning | Next Step |
|--------|---------|-----------|
| **received** | Just arrived | Quality check |
| **inspected** | Checked | Accept/Reject decision |
| **accepted** | QC passed | Match to invoice |
| **rejected** | QC failed | Return/credit |

---

## 4. HOW THEY WORK TOGETHER

### **Complete Procurement Workflow**

```
STEP 1: MATERIAL NEED IDENTIFIED
             ↓
         CREATE INDENT
         (Request Materials)
             ↓
STEP 2: INDENT APPROVAL
        Finance reviews budget
        Approves requirement
             ↓
STEP 3: CREATE PURCHASE ORDER
        From approved indent
        Send to vendor
             ↓
STEP 4: VENDOR FULFILLS PO
        Manufactures/Prepares materials
        Ships to site
             ↓
STEP 5: MATERIALS ARRIVE
        Create GRN
        Record receipt
             ↓
STEP 6: QUALITY CHECK
        Inspect materials
        Check damage
        Verify quantity
             ↓
STEP 7: QUALITY DECISION
        ├─→ PASS: Accept, proceed
        └─→ FAIL: Reject, return
             ↓
STEP 8: INVOICE RECEIVED
        Vendor sends invoice
        Shows amount due
        Specifies retention %
             ↓
STEP 9: RECONCILIATION
        Match GRN to Invoice
        Check quantities match
        Check amounts match
        Flag discrepancies
             ↓
STEP 10: RETENTION CALCULATION
         Amount to pay = Invoice - (Invoice × Retention %)
         Amount to hold = Invoice × Retention %
             ↓
STEP 11: PAYMENT RELEASE
         Pay: Invoice - Retention
         Hold: Retention
             ↓
STEP 12: RETENTION RELEASE
         When project complete
         Defects fixed
         Warranty satisfied
         Release held retention
             ↓
STEP 13: FINAL PAYMENT
         Vendor receives complete payment
         All amounts cleared
```

### **Data Connections**

```
INDENT
  ├─ References: Project
  ├─ Contains: Multiple indent items
  └─ Links to: Purchase Order (1:1)
       │
       └─→ PURCHASE ORDER
           ├─ References: Indent, Supplier
           ├─ Contains: PO items
           └─ Links to: GRN (1:many)
                │
                └─→ GRN (Goods Receipt Note)
                    ├─ References: PO, Project
                    ├─ Contains: GRN items (received)
                    └─ Links to: Invoice Reconciliation
                         │
                         └─→ INVOICE
                             ├─ References: Supplier, Project
                             ├─ Contains: Line items
                             ├─ Contains: RETENTION fields
                             └─ Links to: GRN (reconciliation)
                                  │
                                  └─→ PAYMENT
                                      ├─ Amount = Invoice - Retention
                                      └─ Retention held until release
```

---

## 5. INVOICE-GRN RECONCILIATION

### **Three-Way Matching**

```
     INDENT
        ↓
   PO CREATED
        ↓
     GRN RECEIVED
        ↓
   INVOICE ARRIVES
        ↓
   3-WAY MATCH
   ┌────────────────┐
   │ QUANTITY MATCH │  PO qty = GRN qty = Invoice qty
   └────────────────┘
        ↓
   ┌────────────────┐
   │ AMOUNT MATCH   │  PO amount = Invoice amount
   └────────────────┘
        ↓
   ┌────────────────┐
   │ DATE MATCH     │  Invoice date reasonable vs GRN
   └────────────────┘
        ↓
   ✓ ALL MATCH → APPROVE PAYMENT
        ↓
   ✗ DISCREPANCY → FLAG FOR RESOLUTION
```

### **Reconciliation Status**

| Status | Meaning | Action |
|--------|---------|--------|
| **pending** | Checking | Compare details |
| **matched** | All OK | Approve payment |
| **discrepancy** | Issues found | Investigate |
| **resolved** | Fixed | Proceed to payment |

### **Discrepancy Types**

```
QUANTITY MISMATCH
├─ Ordered: 100 bags
├─ Received (GRN): 95 bags
├─ Invoice shows: 100 bags
└─ Action: Request credit for 5 bags

RATE MISMATCH
├─ PO rate: ₹450/bag
├─ Invoice rate: ₹475/bag
├─ Extra charge: ₹25/bag
└─ Action: Request correction or reject

DATE MISMATCH
├─ GRN date: 2026-04-05
├─ Invoice date: 2026-04-01 (before delivery!)
└─ Action: Query vendor

QUALITY MISMATCH
├─ GRN shows: 5 bags damaged
├─ Invoice shows: 0 damaged
├─ Missing credit: ₹2,250 (5 bags × ₹450)
└─ Action: Request credit note
```

---

## 6. RETENTION RELEASE WORKFLOW

### **When to Release Retention**

```
RETENTION HELD: ₹50,000

CONDITIONS FOR RELEASE:
├─ Project completed ✓
├─ All defects fixed ✓
├─ Warranty period expires ✓
├─ Final inspection passed ✓
└─ Payment approved ✓

RELEASE RETENTION
  ↓
[Status: RELEASED]
  ↓
Full payment to vendor
```

### **Retention Timeline**

```
Jan: Invoice 1 - Hold 5%
Feb: Invoice 2 - Hold 5%
Mar: Invoice 3 - Hold 5%
Apr: Invoice 4 - Hold 5%
May: Invoice 5 - Hold 5%
Jun: Project Complete
     └─→ Release all retained amounts
         Total released = 5 invoices × 5%
```

---

## 7. EXAMPLE: COMPLETE JOURNEY

### **Cement Purchase End-to-End**

```
DAY 1: MATERIAL NEED
Site manager: "We need 100 bags of cement for foundation"

DAY 1: CREATE INDENT
  Indent: IND/2026/001
  Items: Cement - 100 bags
  Cost: ₹45,000 (100 × ₹450)
  Status: DRAFT

DAY 2: SUBMIT FOR APPROVAL
  Finance reviews
  Budget available: YES ✓
  Status: SUBMITTED

DAY 3: INDENT APPROVED
  Status: APPROVED

DAY 3: CREATE PO
  PO: PO/2026/001
  From: Our Company
  To: ABC Cement Supplier
  Items: 100 bags cement @ ₹450
  Total: ₹45,000
  Delivery: 2026-04-05

DAY 5: MATERIALS DELIVERED
  Truck arrives with cement bags
  Site manager creates GRN
  GRN: GRN/2026/001

DAY 5: QUALITY CHECK
  Count: 100 bags ✓
  Sealing: Intact ✓
  Date of manufacture: OK ✓
  GRN Status: ACCEPTED

DAY 7: INVOICE ARRIVES
  Invoice: INV-2026-ABC-001
  Items: 100 bags cement
  Amount: ₹45,000
  Retention: 5%
  Retention Amount: ₹2,250
  Amount to Pay: ₹42,750 (Hold ₹2,250)

DAY 7: RECONCILIATION
  GRN Qty (100) vs Invoice Qty (100) ✓ MATCH
  GRN Amount (₹45,000) vs Invoice (₹45,000) ✓ MATCH
  Status: MATCHED

DAY 8: PAYMENT APPROVAL
  ✓ Approved
  Pay: ₹42,750
  Retain: ₹2,250

DAY 10: PAYMENT RELEASED
  ABC Cement Supplier receives: ₹42,750
  Retained amount: ₹2,250 (held)

DAY 30: PROJECT COMPLETION
  Foundation completed successfully
  All materials used satisfactorily
  No defects found

DAY 30: RELEASE RETENTION
  Status: RELEASED
  Amount: ₹2,250

DAY 31: FINAL PAYMENT
  ABC Cement Supplier receives: ₹2,250
  Total payment: ₹45,000 (₹42,750 + ₹2,250)
  Transaction complete ✓
```

---

## 8. KEY METRICS & MONITORING

### **Indent Metrics**

```
Total Indents Created: 250
├─ Approved: 240 (96%)
├─ Rejected: 5 (2%)
└─ Pending: 5 (2%)

Indent Value: ₹50,000,000
Average Indent: ₹200,000
Processing Time: 2-3 days
```

### **GRN Metrics**

```
Total GRNs: 240
├─ Accepted: 230 (95.8%)
├─ Rejected: 5 (2%)
└─ Partial: 5 (2%)

Quality Pass Rate: 95.8%
Average Delivery Time: 5 days
Damage Rate: 2% (acceptable)
```

### **Retention Metrics**

```
Total Retention Held: ₹5,000,000
├─ Released: ₹4,500,000 (90%)
└─ Pending: ₹500,000 (10%)

Average Retention %: 5%
Outstanding Retentions: 10 invoices
Total Payable: ₹500,000
```

---

## 9. SUMMARY TABLE

| Aspect | INDENT | GRN | RETENTION |
|--------|--------|-----|-----------|
| **Purpose** | Material request | Goods receipt | Payment safeguard |
| **Created By** | Project Manager | Site Manager | Finance (on invoice) |
| **When Created** | Before purchase | On delivery | With invoice |
| **Key Fields** | Description, Qty, Cost | Receipt date, QC | %, Amount, Status |
| **Status Types** | draft, approved, rejected | received, accepted, rejected | pending, released |
| **Links To** | PO | Invoice | Payment |
| **Role** | Planning | Tracking | Control |
| **Timeline** | Days 1-3 | Day 5 | Day 7-30 |
| **Impact** | Commits budget | Records receipt | Holds payment |

---

## 10. SYSTEM BENEFITS

### **Indent Benefits**
✅ Planned purchasing
✅ Budget control
✅ Requirement documentation
✅ Approval workflow

### **GRN Benefits**
✅ Goods tracking
✅ Quality verification
✅ Receiving documentation
✅ Discrepancy identification

### **Retention Benefits**
✅ Quality guarantee
✅ Vendor accountability
✅ Risk mitigation
✅ Legal compliance

---

## CONCLUSION

- **INDENT** = Request what you need (Planning)
- **GRN** = Verify what you received (Quality)
- **RETENTION** = Hold payment until satisfied (Control)

Together, they ensure:
✅ Organized procurement
✅ Quality materials
✅ Accurate payments
✅ Complete audit trail
✅ Risk management
