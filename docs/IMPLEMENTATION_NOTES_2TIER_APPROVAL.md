# 2-Tier Expense Approval System - Implementation Summary

## Overview
A dual-tier approval workflow for expenses based on amount:
- **Tier 1**: Expenses ≤₹50,000 → Single approval required
- **Tier 2**: Expenses >₹50,000 → Two approvals required from different users

---

## Backend Implementation

### 1. Expense Model Updates
**File**: `staff_management/expense_model.py`

Added fields:
- `approval_tier` (VARCHAR(10)): 'Tier1' or 'Tier2' based on amount
- `approvals_required` (INTEGER): 1 for Tier1, 2 for Tier2
- `approvals_received` (INTEGER): Tracks number of approvals received
- `first_approver_id` (FK): User ID of first approver
- `first_approval_date` (DATETIME): Timestamp of first approval
- `second_approver_id` (FK): User ID of second approver (Tier2 only)
- `second_approval_date` (DATETIME): Timestamp of second approval

### 2. Create Expense Endpoint
**Endpoint**: `POST /api/staff/expenses`
**Change**: Automatically determines approval tier based on amount

```
if amount > 50000:
    tier = 'Tier2'
    approvals_required = 2
else:
    tier = 'Tier1'
    approvals_required = 1
```

### 3. Approve Expense Endpoint
**Endpoint**: `POST /api/staff/expenses/<id>/approve`
**Enhanced workflow**:

**For Tier 1**:
- Single approval immediately marks expense as 'Approved'
- Creates CashTransaction if needed

**For Tier 2**:
- **First approval**: Sets `first_approver_id`, `approvals_received=1`, status remains 'Pending'
- **Second approval**: Requires different user, marks as 'Approved', sets `second_approver_id`
- **Safety**: Prevents same person from approving twice

### 4. Get Approvals Endpoint
**Endpoint**: `GET /api/staff/approvals/expenses`
**New query parameter**: `approval_tier` (Tier1 or Tier2)

Examples:
- `GET /api/staff/approvals/expenses?approval_tier=Tier1` → Tier1 expenses only
- `GET /api/staff/approvals/expenses?approval_tier=Tier2` → Tier2 expenses only

---

## Frontend Implementation

### 1. Expense Approvals Page (Tier 1)
**File**: `src/pages/ExpenseApprovalsPage.jsx`
**Route**: `/finance/approvals`
**Purpose**: Review and approve Tier 1 expenses (≤₹50,000)

Features:
- Shows only Tier1 expenses
- Single approval badge showing "1/1"
- Category filter
- Pagination
- Review modal for approval/rejection

### 2. Pending Approvals Page (Tier 2)
**File**: `src/pages/PendingApprovalsPage.jsx`
**Route**: `/finance/pending-approvals`
**Purpose**: Review and approve Tier 2 expenses (>₹50,000)

Features:
- Shows only Tier2 expenses awaiting approvals
- Approval status badge showing "1/2" or "2/2"
- Visual indicator when both approvals are complete (green badge)
- Category filter
- Pagination
- Review modal showing approval progress

### 3. Approval Modal Enhancement
**File**: `src/components/ApprovalModal.jsx`
**Changes**:
- Displays approval tier information
- Shows current approval status (e.g., "1/2")
- Special message for Tier2 expenses: "First approval received. This is the second approval phase..."
- Staff and project names displayed

### 4. Routing
**File**: `src/App.jsx`

Routes configured:
- `/finance/approvals` → ExpenseApprovalsPage (Tier 1 single approvals)
- `/finance/pending-approvals` → PendingApprovalsPage (Tier 2 multi-approvals)

---

## Database Changes

### Migration File
**File**: `migrations/versions/add_approval_tier_to_expenses.py`

Adds 7 new columns to `expenses` table with proper constraints and defaults.

### Data Initialization
All existing expenses automatically categorized:
- Expense 1 (Rs.7,500) → Tier1 ✓
- Expense 2 (Rs.120,000) → Tier2 ✓

---

## Workflow Example

### Scenario 1: Tier 1 Approval (≤₹50,000)
```
1. User creates expense for Rs.25,000
   → System sets approval_tier='Tier1', approvals_required=1

2. Finance/Manager visits /finance/approvals
   → Sees the Rs.25,000 expense (Tier 1 badge: 1/1)

3. Clicks "Review" → Approval Modal
   → Approves with notes

4. System updates:
   → status = 'Approved'
   → approvals_received = 1
   → Creates CashTransaction
   → Action complete ✓
```

### Scenario 2: Tier 2 Approval (>₹50,000)
```
1. User creates expense for Rs.120,000
   → System sets approval_tier='Tier2', approvals_required=2

2. Finance Manager #1 visits /finance/pending-approvals
   → Sees the Rs.120,000 expense (Tier 2 badge: 0/2)

3. Manager #1 clicks "Review" → Approval Modal
   → Approves with notes

4. System updates (First Approval):
   → approvals_received = 1
   → first_approver_id = Manager1's ID
   → first_approval_date = timestamp
   → status = 'Pending' (still waiting for 2nd approval)
   → Badge now shows: 1/2

5. Finance Manager #2 visits /finance/pending-approvals
   → Sees the Rs.120,000 expense (Tier 2 badge: 1/2)
   → Modal shows: "First approval received. This is the second approval phase..."

6. Manager #2 clicks "Review" → Approval Modal
   → Approves with notes

7. System validates:
   → Checks: Manager2 ≠ Manager1 ✓
   → Updates (Second Approval):
      - status = 'Approved'
      - approvals_received = 2
      - second_approver_id = Manager2's ID
      - second_approval_date = timestamp
      - Creates CashTransaction
      - Badge now shows: 2/2 (green) ✓
   → Action complete ✓
```

---

## Testing Checklist

- [x] Database schema updated with 7 new columns
- [x] Expense model includes all new fields
- [x] create_expense auto-sets tier based on amount
- [x] Tier1 single approval works correctly
- [x] Tier2 first approval recorded properly
- [x] Tier2 prevents same person from approving twice
- [x] Tier2 second approval from different user completes approval
- [x] ExpenseApprovalsPage filters to Tier1 only
- [x] PendingApprovalsPage filters to Tier2 only
- [x] Approval badges display correctly
- [x] Modal shows tier and approval status
- [x] CashTransaction created only when fully approved

---

## API Response Examples

### Expense Response (Tier 2, First Approval Received)
```json
{
  "id": 2,
  "amount": 120000,
  "approval_tier": "Tier2",
  "approvals_required": 2,
  "approvals_received": 1,
  "status": "Pending",
  "first_approver_id": 5,
  "first_approval_date": "2026-04-01T14:30:00",
  "second_approver_id": null,
  "second_approval_date": null,
  "staff_name": "John Supervisor",
  "project_name": "Highway Project"
}
```

### Expense Response (Tier 1, Approved)
```json
{
  "id": 1,
  "amount": 7500,
  "approval_tier": "Tier1",
  "approvals_required": 1,
  "approvals_received": 1,
  "status": "Approved",
  "first_approver_id": 3,
  "first_approval_date": "2026-03-28T10:15:00",
  "second_approver_id": null,
  "second_approval_date": null,
  "staff_name": "Jane Engineer",
  "project_name": "Bridge Project"
}
```

---

## Security Features

1. **Role-Based**: Only Finance/Manager/Admin can approve
2. **Dual Validation**: Tier2 requires confirmation from two different users
3. **Same-Person Prevention**: Second approver must be different from first
4. **Audit Trail**: All approvals logged with timestamps and user IDs
5. **Status Enforcement**: Cannot approve already-approved expenses

---

## Files Modified/Created

### Backend
- ✓ `staff_management/expense_model.py` - Added 7 new fields
- ✓ `staff_management/routes.py` - Updated endpoints for 2-tier workflow
- ✓ `migrations/versions/add_approval_tier_to_expenses.py` - Migration file

### Frontend
- ✓ `src/pages/ExpenseApprovalsPage.jsx` - NEW: Tier1 approvals page
- ✓ `src/pages/PendingApprovalsPage.jsx` - Updated for Tier2
- ✓ `src/components/ApprovalModal.jsx` - Enhanced with tier info
- ✓ `src/App.jsx` - Added routing for new page

### Database
- ✓ `data.db` - 7 new columns added to expenses table
- ✓ All existing expenses categorized by tier

---

## Future Enhancements

1. **Conditional Approvers**: Different approver requirements based on department/project
2. **Approval History View**: Show all approvals and rejections for an expense
3. **Bulk Approvals**: Approve multiple Tier1 expenses at once
4. **Approval Delegates**: Assign approval rights to delegates
5. **Time-Based Escalation**: Auto-escalate expenses awaiting 2nd approval for >3 days
6. **Department-Specific Tiers**: Tier thresholds per department

---

## Troubleshooting

### Expense appears in wrong page
- **Issue**: Tier1 expense showing in /finance/pending-approvals
- **Solution**: Check `approval_tier` field in database, should be 'Tier1' or 'Tier2'

### Cannot approve Tier2 expense with same person twice
- **Issue**: Getting error "same person cannot approve twice"
- **Status**: This is expected behavior ✓

### CashTransaction not created after approval
- **Issue**: Approved expense but no transaction created
- **Solution**: Check logs, CashTransaction creation is optional and won't block approval

---

## Questions or Issues?

Refer to the implementation test output in the console which shows:
- All expenses properly categorized by tier
- All database columns present
- Approval workflow correctly configured
