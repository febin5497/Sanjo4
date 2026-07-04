# Finance Module - All Pages & Routes

## Overview
Complete list of all finance-related pages in the construction management system.

---

## 1. MAIN FINANCE DASHBOARD

### **Finance Dashboard**
- **Route:** `/finance`
- **File:** `Finance.jsx`
- **Description:** Main finance dashboard showing:
  - Revenue vs Expenses chart
  - Income/Expense summary
  - Cash balance
  - Expense breakdown by category
  - Transaction filters
  - Financial KPIs

### **Finance Summary**
- **Component:** `FinanceSummary.jsx`
- **Description:** Quick financial overview widget

### **Finance Dashboard (Alternative)**
- **Route:** `/dashboard/finance` (alternative dashboard)
- **File:** `FinanceDashboard.jsx`
- **Description:** Alternative finance dashboard view

---

## 2. INVOICE MANAGEMENT

### **Invoices List**
- **Route:** `/invoices`
- **File:** `Invoices.jsx`
- **Description:**
  - List all invoices
  - Filter by status, date range, amount
  - View invoice details
  - Create new invoices
  - Pagination support

### **Create Invoice**
- **Route:** `/invoices/new`
- **File:** `CreateInvoice.jsx`
- **Description:**
  - Form to create new invoices
  - Client selection
  - Line items
  - Tax calculation
  - Invoice date/due date

### **Invoice Detail**
- **Route:** `/invoices/:id`
- **File:** `InvoiceDetail.jsx`
- **Description:**
  - View detailed invoice
  - Payment history
  - Approval status
  - Edit invoice (if pending)
  - Download/print invoice

---

## 3. TRANSACTION MANAGEMENT

### **Transactions List**
- **Route:** `/transactions` (may be within Finance)
- **File:** `TransactionList.jsx`
- **Description:**
  - List all financial transactions
  - Filter by type, date, amount, category
  - View transaction details
  - Export transactions
  - Pagination

### **Add Transaction**
- **Route:** `/transactions/add`
- **File:** `AddTransaction.jsx`
- **Description:**
  - Form to add new financial transaction
  - Transaction type (income/expense)
  - Category selection
  - Amount and date
  - Description

### **Edit Transaction**
- **Route:** `/transactions/:id/edit`
- **File:** `EditTransaction.jsx`
- **Description:**
  - Edit existing transaction
  - Modify amount, category, description
  - Only editable if not locked/approved

---

## 4. APPROVAL WORKFLOWS

### **Pending Approvals**
- **Route:** `/finance/pending-approvals`
- **File:** `PendingApprovalsPage.jsx`
- **Description:**
  - List all pending approval requests
  - Filter by entity type (invoice, purchase, budget, expense)
  - Approve/reject with notes
  - View approval history
  - Check who approved/rejected

### **Expense Approvals (Finance View)**
- **Route:** `/finance/approvals`
- **File:** `ExpenseList.jsx` (in approval mode)
- **Description:**
  - Finance staff approve/reject staff expense requests
  - Filter by status, category
  - View staff name and project
  - Approve single or batch expenses
  - Add approval notes

### **Attendance Photo Approvals**
- **Route:** `/attendance/approvals`
- **File:** `AttendancePhotoApprovals.jsx`
- **Description:**
  - Approve/reject attendance photos from mobile app
  - View photo with location data
  - Timestamp verification
  - Approve or request resubmission

---

## 5. BUDGET MANAGEMENT

### **Budgets**
- **Route:** `/budgets`
- **File:** `BudgetPage.jsx`
- **Description:**
  - List all project budgets
  - Create/edit budgets
  - View budget categories
  - Track budget vs actual spend
  - Budget approval status
  - Alerts for overspend

---

## 6. EXPENSE MANAGEMENT

### **Staff Expenses**
- **Route:** `/staff/expenses`
- **File:** `ExpenseList.jsx` (in staff mode)
- **Description:**
  - Staff view their own expense submissions
  - Create new expense
  - Edit pending expenses
  - Delete expenses
  - View approval status
  - See rejection reasons

---

## 7. FINANCIAL REPORTING

### **Reports Hub**
- **Route:** `/reports`
- **File:** `ReportsPage.jsx`
- **Description:**
  - Central hub for all financial reports
  - Menu of available reports
  - Date range selection
  - Project filtering
  - Download options (PDF/Excel)

### **Project Profitability Report**
- **Route:** `/reports/profitability`
- **File:** `ProjectProfitabilityReport.jsx`
- **Description:**
  - Revenue - Expenses = Profit by project
  - Profit margin percentage
  - Comparison across projects
  - Export capabilities
  - Trends over time

### **Cost vs Budget Report**
- **Route:** `/reports/budget-variance`
- **File:** `CostVsBudgetReport.jsx`
- **Description:**
  - Budget vs actual spending
  - Variance analysis by category
  - Over/under budget alerts
  - Budget utilization percentage
  - Category-wise breakdown

### **Cash Flow Report**
- **Route:** `/reports/cash-flow`
- **File:** `CashFlowReport.jsx`
- **Description:**
  - Daily/weekly/monthly cash inflows
  - Cash outflows
  - Net cash position
  - Cash flow trends
  - Forecasting

### **Receivables Aging Report**
- **Route:** `/reports/receivables-aging`
- **File:** `ReceivablesAgingReport.jsx`
- **Description:**
  - Aging buckets (0-30, 31-90, 90+)
  - Outstanding invoices by age
  - Total receivables
  - Collection status
  - Late payment alerts

### **Attendance Report**
- **Route:** `/attendance/report`
- **File:** `AttendanceReport.jsx`
- **Description:**
  - Staff attendance summary
  - Present/absent breakdown
  - Overtime hours
  - Monthly attendance trends

---

## 8. PAYROLL MANAGEMENT

### **Payroll Cycles**
- **Route:** `/payroll/cycles` (may vary)
- **File:** `PayrollCyclePage.jsx`
- **Description:**
  - Create/manage payroll cycles
  - Monthly salary calculations
  - Deductions management
  - Salary slip generation
  - Bank transfer file export

---

## QUICK REFERENCE - ALL FINANCE PAGES

1. **Finance Dashboard** - `/finance` (Finance.jsx)
2. **Invoices List** - `/invoices` (Invoices.jsx)
3. **Create Invoice** - `/invoices/new` (CreateInvoice.jsx)
4. **Invoice Detail** - `/invoices/:id` (InvoiceDetail.jsx)
5. **Transactions** - `/transactions` (TransactionList.jsx)
6. **Add Transaction** - `/transactions/add` (AddTransaction.jsx)
7. **Edit Transaction** - `/transactions/:id/edit` (EditTransaction.jsx)
8. **Pending Approvals** - `/finance/pending-approvals` (PendingApprovalsPage.jsx)
9. **Expense Approvals** - `/finance/approvals` (ExpenseList.jsx)
10. **Staff Expenses** - `/staff/expenses` (ExpenseList.jsx)
11. **Budgets** - `/budgets` (BudgetPage.jsx)
12. **Reports Hub** - `/reports` (ReportsPage.jsx)
13. **Profitability Report** - `/reports/profitability` (ProjectProfitabilityReport.jsx)
14. **Budget vs Actual Report** - `/reports/budget-variance` (CostVsBudgetReport.jsx)
15. **Cash Flow Report** - `/reports/cash-flow` (CashFlowReport.jsx)
16. **Receivables Aging Report** - `/reports/receivables-aging` (ReceivablesAgingReport.jsx)
17. **Payroll Cycles** - `/payroll/cycles` (PayrollCyclePage.jsx)
18. **Attendance Report** - `/attendance/report` (AttendanceReport.jsx)

---

## ROLE-BASED ACCESS

### Staff
- View own expenses: `/staff/expenses`
- Submit new expense
- Track approval status

### Finance Manager
- Finance Dashboard: `/finance`
- Manage Invoices: `/invoices`
- Approve Expenses: `/finance/approvals`
- View Reports: `/reports/*`
- Manage Budgets: `/budgets`
- Pending Approvals: `/finance/pending-approvals`

### Admin
- Access to ALL pages
- Can override approvals
- Configure workflows
- Access audit logs

---

## BACKEND API ENDPOINTS

### Finance Endpoints
- `GET /api/finance/summary` - Dashboard data
- `GET /api/finance/invoices` - Invoice list
- `POST /api/finance/invoices` - Create invoice
- `GET /api/finance/transactions` - Transaction list
- `POST /api/finance/transactions` - Create transaction
- `GET /api/finance/pending-approvals` - Approvals list
- `POST /api/finance/approve/<entity_type>/<entity_id>` - Approve
- `POST /api/finance/reject/<entity_type>/<entity_id>` - Reject
- `GET /api/finance/budgets` - Budgets list
- `POST /api/finance/budgets` - Create budget

### Reports Endpoints
- `GET /api/finance/reports/project-profitability` - Profitability data
- `GET /api/finance/reports/cost-vs-budget` - Budget variance
- `GET /api/finance/reports/cash-flow` - Cash flow data
- `GET /api/finance/reports/receivables-aging` - Aging report

### Expense Endpoints
- `GET /api/staff/expenses` - Staff expenses
- `POST /api/staff/expenses` - Create expense (ALWAYS Pending)
- `GET /api/staff/approvals/expenses` - Expenses for approval
- `POST /api/staff/expenses/:id/approve` - Approve expense
- `POST /api/staff/expenses/:id/reject` - Reject expense

---

## STATUS: ALL PAGES FUNCTIONAL ✓
- Finance Dashboard: Working
- Invoice Management: Working
- Transaction Management: Working
- Approval Workflows: Working (fixed auto-approval issue)
- Budget Management: Working
- Expense Management: Working (fixed auto-approval)
- Reports: All 4 reports working
- Payroll: Implemented

**Last Updated:** April 1, 2026
