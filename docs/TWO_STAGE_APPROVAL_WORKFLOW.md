# Two-Stage Approval Workflow Guide

## Overview

A sequential two-stage approval process for large expenses (>₹50,000):

```
Stage 1: /finance/approvals          Stage 2: /finance/pending-approvals
┌──────────────────────────┐         ┌──────────────────────────┐
│  First Approval (Green)   │         │ Second Approval (Purple)  │
│                          │         │                          │
│ Manager/Finance #1       │         │ Finance/Compliance #2     │
│ Approves >50K expense    │──────→  │ Confirms >50K expense     │
│                          │         │                          │
│ Button: "First Approve"  │         │ Button: "Second Approve"  │
└──────────────────────────┘         └──────────────────────────┘
      approvals: 0/2                       approvals: 1/2
      Status: Pending                       Status: Pending
         ↓                                     ↓
      FIRST APPROVAL                    FULLY APPROVED
      recorded (1/2)                     (2/2)
```

---

## Pages & Buttons

### Page 1: `/finance/approvals` (Level 1 Approval)
**Green Buttons**

**Tab 1: Tier 1 Approvals (≤₹50,000)**
- Single approval required
- Button: **"Approve"** (Green)
- After approval: Fully approved
- Example: Rs. 7,500 expense

**Tab 2: Tier 2 First Approvals (>₹50,000) - 1/2**
- First of two approvals required
- Button: **"First Approve"** (Green)
- After approval: Moves to pending-approvals
- Example: Rs. 120,000 expense

---

### Page 2: `/finance/pending-approvals` (Level 2 Approval)
**Purple Button**

**Tier 2 Second Approvals (>₹50,000)**
- Second of two approvals required
- Shows only expenses with 1/2 approvals
- Button: **"Second Approve"** (Purple)
- After approval: Fully approved
- Example: Rs. 120,000 expense (after first approval)

---

## User Workflow Example

### Scenario: ₹120,000 Expense (Tier 2)

**Step 1 - Manager Approves (First Stage)**
```
Manager logs in
→ Visits /finance/approvals
→ Clicks Tab: "Tier 2 First Approvals (>₹50K) - 1/2"
→ Sees: Rs. 120,000 expense with "0/2" badge (Orange)
→ Clicks: "First Approve" button (Green)
→ Success: "First approval recorded. Will appear in
           pending-approvals for second approval."
→ Expense disappears from this page
→ Status changes to: "1/2" badge (Orange)
```

**Step 2 - Finance Manager Confirms (Second Stage)**
```
Finance Manager logs in
→ Visits /finance/pending-approvals
→ Sees: Rs. 120,000 expense with "1/2" badge (Orange)
→ Clicks: "Second Approve" button (Purple)
→ Success: "Second approval recorded. Expense fully approved!"
→ Expense disappears from this page
→ Status changes to: "2/2" badge (Green)
→ CashTransaction automatically created
→ Fully Approved!
```

---

## Current Test Data

| ID | Amount | Tier | Status | Approvals | Location |
|----|--------|------|--------|-----------|----------|
| 1 | Rs. 7,500 | Tier1 | Approved | 1/1 | (Approved) |
| 2 | Rs. 120,000 | Tier2 | Pending | 1/2 | /finance/pending-approvals |

**Current state**: Tier2 expense #2 is ready for second approval at `/finance/pending-approvals`

---

## API Endpoints

### Get Expenses to Approve
```
GET /api/staff/approvals/expenses?approval_tier=Tier1
  → Returns all Tier1 expenses needing approval (≤₹50K)

GET /api/staff/approvals/expenses?approval_tier=Tier2_first
  → Returns Tier2 expenses with 0 approvals (>₹50K) awaiting FIRST approval

GET /api/staff/approvals/expenses?approval_tier=Tier2_second
  → Returns Tier2 expenses with 1 approval (>₹50K) awaiting SECOND approval
```

### Approve Expense
```
POST /api/staff/expenses/{id}/approve

First Approval (from /finance/approvals - Tier2_first):
  - Sets: approvals_received = 1
  - Status: Remains 'Pending'
  - Next: Appears in /finance/pending-approvals

Second Approval (from /finance/pending-approvals - Tier2_second):
  - Sets: approvals_received = 2
  - Status: Changes to 'Approved'
  - Creates: CashTransaction
  - Complete!
```

---

## Security Features

✓ **Different Users Required**: Same person cannot approve twice
  - First approver: `first_approver_id`
  - Second approver: `second_approver_id`
  - System prevents: `second_approver_id == first_approver_id`

✓ **Role-Based**: Only Finance/Manager/Admin can approve

✓ **Sequential**: Cannot do second approval without first approval

✓ **Audit Trail**: All approvals logged with timestamps

✓ **Automatic Progress**: Expense automatically moves between pages

---

## Button Summary

| Page | Button | Color | Action | Tier | Amount |
|------|--------|-------|--------|------|--------|
| `/finance/approvals` | Approve | Green | Single approval | Tier1 | ≤₹50K |
| `/finance/approvals` | First Approve | Green | 1st of 2 approvals | Tier2 | >₹50K |
| `/finance/pending-approvals` | Second Approve | Purple | 2nd of 2 approvals | Tier2 | >₹50K |

---

## Rejection Flow

**Can reject at any stage:**
```
Stage 1: Click "Reject"
  → Enter rejection reason
  → Expense marked as 'Rejected'
  → Disappears from both pages

Stage 2: Click "Reject"
  → Enter rejection reason
  → Expense marked as 'Rejected'
  → All approvals cancelled
  → Disappears from both pages
```

---

## Testing Steps

1. **Create Tier2 Expense** (>₹50K)
   - Status: Pending, 0/2 approvals
   - Location: /finance/approvals (Tab: "Tier 2 First Approvals")

2. **Manager approves**
   - Click "First Approve"
   - Expense moves to 1/2 approvals
   - Disappears from /finance/approvals

3. **Finance Manager approves**
   - Visit /finance/pending-approvals
   - See same expense with 1/2 badge
   - Click "Second Approve"
   - Status changes to Approved (2/2)
   - Expense fully approved!

---

## FAQ

**Q: Why two stages?**
A: Ensures governance - manager authorizes, finance verifies compliance before payment.

**Q: Can same person approve twice?**
A: No - system prevents it. Error: "The same person cannot approve twice."

**Q: What if second approver is unavailable?**
A: Expense waits in /finance/pending-approvals with 1/2 badge visible.

**Q: What happens after second approval?**
A: Automatically creates CashTransaction and marks as Approved.

**Q: Can I change my approval?**
A: No - approvals are final. You can reject if there's an issue.

**Q: Who can see which expenses?**
A: Only Finance/Manager/Admin roles can see approval pages.

---

## Summary

- **Simple expenses (≤₹50K)**: Single approval in /finance/approvals
- **Large expenses (>₹50K)**: Two-stage approval across two pages
- **Color coding**: Green (First) → Purple (Second)
- **Security**: Different users required for each stage
- **Transparency**: Badge shows current approval status (0/2, 1/2, 2/2)
