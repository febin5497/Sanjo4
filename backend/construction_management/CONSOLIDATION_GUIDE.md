# Code Consolidation Implementation Guide

**Status:** Phase 1/3 - Foundation Complete
**Created:** March 31, 2026
**Target:** 25-35% code reduction with improved maintainability

---

## Overview

This guide documents the systematic consolidation of duplicated code patterns across the construction finance management system. The consolidation is being executed in three phases over 8-10 weeks.

### What's Been Done (Phase 1) ✅

1. **Constants Module** (`constants/`)
   - `statuses.py` - All status enums with validation
   - `config.py` - GST rates, defaults, configurations
   - Replaces 50+ hardcoded strings across codebase

2. **Base Model Mixins** (`models/base.py`)
   - `TimestampMixin` - created_at, updated_at
   - `CompanyMixin` - company_id for multi-tenancy
   - `AuditMixin` - created_by_id, updated_by_id
   - `ApprovalFieldsMixin` - approval workflow fields
   - `AmountMixin` - amount, tax, discount calculations
   - `StatusMixin` - status field with validation
   - `SearchableMixin` - common search methods
   - `PaginationMixin` - pagination helpers

3. **Frontend Hooks** (`src/hooks/`)
   - `usePaginatedData` - Consolidates 40+ pagination implementations
   - `useFormInput` - Consolidates 40+ form input handlers
   - `useModalState` - Consolidates 57+ modal state managers

### Target: All Three Phases

```
Phase 1: Foundation              → COMPLETE ✅
├─ Constants module
├─ Base model mixins
└─ Essential frontend hooks

Phase 2: Core Refactoring        → IN PROGRESS
├─ Unified approval framework
├─ BaseResourceRouter for CRUD
├─ Advanced frontend hooks
└─ LineItemsManager component

Phase 3: Utilities & Components  → PENDING
├─ Form validation framework
├─ Utility library
├─ Dashboard components
└─ Mobile dashboard consolidation
```

---

## Backend Consolidation Patterns

### Pattern 1: Model Changes - Before & After

#### BEFORE (Old Pattern)
```python
from datetime import datetime
from extensions import db

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='draft')  # Hardcoded

    # Repeated audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer)

    # Approval fields
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
```

#### AFTER (New Pattern with Mixins)
```python
from extensions import db
from models.base import AuditMixin, ApprovalFieldsMixin
from constants import InvoiceStatus

class Invoice(db.Model, AuditMixin, ApprovalFieldsMixin):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(
        db.String(20),
        default=InvoiceStatus.DRAFT.value,
        nullable=False
    )
    # All audit and approval fields inherited from mixins!
```

**Benefit:** 10-15 lines removed per model × 30 models = 300-450 lines saved

---

### Pattern 2: Route Validation - Before & After

#### BEFORE (Old Pattern)
```python
@finance_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    data = request.get_json()

    # Manual validation repeated in 40+ routes
    errors = []
    if not data.get('invoice_id'):
        errors.append({"field": "invoice_id", "message": "Invoice ID required"})
    if not data.get('client'):
        errors.append({"field": "client", "message": "Client name required"})
    if not data.get('total') or data.get('total') <= 0:
        errors.append({"field": "total", "message": "Total must be > 0"})

    if errors:
        return validation_error_response(errors)

    # IP and logging repeated in 40+ routes
    user = User.query.get(current_user_id)
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')

    invoice = Invoice(...)
    db.session.add(invoice)
    db.session.commit()

    log_entity_action(
        user_id=current_user_id,
        entity_type='Invoice',
        action='CREATE',
        ip_address=ip_address,
        user_agent=user_agent
    )
```

#### AFTER (With Decorators - Phase 2)
```python
from decorators import validate_request, audit_log

@finance_bp.route('/invoices', methods=['POST'])
@jwt_required()
@validate_request(InvoiceValidator)  # Auto-validates against schema
@audit_log('Invoice', 'CREATE')      # Auto-logs action
def create_invoice():
    data = request.get_json()  # Already validated!

    invoice = Invoice(...)
    db.session.add(invoice)
    db.session.commit()

    return success_response(invoice.to_dict(), "Invoice created", 201)
```

**Benefit:** 30-50 lines removed per route × 40 routes = 1,200-2,000 lines saved

---

### Pattern 3: Status Constants Usage

#### BEFORE (Hardcoded)
```python
# Hardcoded in 40+ locations
if invoice.status == 'pending':
    can_approve = True
elif invoice.status == 'draft':
    can_approve = False

if invoice.status not in ['draft', 'sent']:
    return error_response("Cannot edit in current status")

transaction.status = 'approved'  # Magic string
```

#### AFTER (Using Constants)
```python
from constants import InvoiceStatus, is_valid_status_transition

# Clear and validated
if invoice.status == InvoiceStatus.PENDING.value:
    can_approve = True
elif invoice.status == InvoiceStatus.DRAFT.value:
    can_approve = False

# Built-in validation
if not is_valid_status_transition('invoice', invoice.status, 'approved'):
    return error_response("Invalid status transition")

transaction.status = TransactionStatus.APPROVED.value
```

**Benefit:** Type safety, IDE autocomplete, centralized validation

---

## Frontend Consolidation Patterns

### Pattern 1: Pagination Hook - Before & After

#### BEFORE (Duplicated in 40+ Pages)
```javascript
// Staff.jsx
const [staff, setStaff] = useState([])
const [loading, setLoading] = useState(true)
const [currentPage, setCurrentPage] = useState(1)
const [perPage, setPerPage] = useState(10)
const [totalPages, setTotalPages] = useState(0)
const [total, setTotal] = useState(0)

useEffect(() => {
  loadStaff()
}, [currentPage, perPage])

const loadStaff = async () => {
  setLoading(true)
  try {
    const params = new URLSearchParams({
      page: currentPage,
      per_page: perPage,
      search: searchQuery
    })
    const res = await api.get(`/api/staff?${params}`)
    setStaff(res.data?.data || [])
    setTotal(res.data?.pagination?.total || 0)
    setTotalPages(res.data?.pagination?.pages || 0)
  } catch (error) {
    showToast('Error loading staff', 'error')
  } finally {
    setLoading(false)
  }
}

// ... repeat in Materials.jsx, Equipment.jsx, etc.
```

#### AFTER (Using Hook)
```javascript
// Staff.jsx
import { usePaginatedData } from '../hooks'

function Staff() {
  const { data: staff, loading, page, setPage, totalPages }
    = usePaginatedData('/api/staff', { search: searchQuery })

  // That's it! Pagination handled automatically
}

// Materials.jsx, Equipment.jsx - same 3 lines of code!
```

**Benefit:** 25-35 lines removed per page × 40 pages = 1,000-1,400 lines saved

---

### Pattern 2: Form Input Hook - Before & After

#### BEFORE (Duplicated in 40+ Pages)
```javascript
const [formData, setFormData] = useState({
  name: '',
  email: '',
  active: true
})

const handleInputChange = (e) => {
  const { name, value, type, checked } = e.target
  setFormData(prev => ({
    ...prev,
    [name]: type === 'checkbox' ? checked : value
  }))
}

// ... same in 40+ pages
```

#### AFTER (Using Hook)
```javascript
import { useFormInput } from '../hooks'

const { formData, handleChange } = useFormInput({
  name: '',
  email: '',
  active: true
})

// In JSX:
// <input name="name" value={formData.name} onChange={handleChange} />
// That's it!
```

**Benefit:** 10-15 lines removed per page × 40 pages = 400-600 lines saved

---

### Pattern 3: Modal State - Before & After

#### BEFORE (Duplicated in 57+ Pages)
```javascript
const [showCreateModal, setShowCreateModal] = useState(false)
const [showEditModal, setShowEditModal] = useState(false)
const [showDetailModal, setShowDetailModal] = useState(false)
const [showConfirmModal, setShowConfirmModal] = useState(false)

const openCreateModal = () => setShowCreateModal(true)
const closeCreateModal = () => setShowCreateModal(false)
// ... 10+ more toggles

// ... same in 57+ pages
```

#### AFTER (Using Hook)
```javascript
import { useSimpleModalState } from '../hooks'

const {
  showCreateModal, setShowCreateModal,
  showEditModal, setShowEditModal,
  showDetailModal, setShowDetailModal,
  showConfirmModal, setShowConfirmModal
} = useSimpleModalState()

// All state managed automatically!
```

**Benefit:** 15-20 lines removed per page × 57 pages = 855-1,140 lines saved

---

## Implementation Roadmap

### Week 1-2: Phase 1 (CURRENT)
- ✅ Create constants module
- ✅ Create base model mixins
- ✅ Create frontend hooks
- [ ] Apply to 10 sample models (Invoice, Purchase, Budget, etc.)
- [ ] Apply to 10 sample pages (Staff, Materials, Equipment, etc.)

### Week 3-4: Phase 2
- [ ] Consolidate approval workflows (3 → 1)
- [ ] Create BaseResourceRouter
- [ ] Create useCrudForm hook
- [ ] Create LineItemsManager component
- [ ] Apply to all resource routes (20+ routes)
- [ ] Apply to all CRUD pages (30+ pages)

### Week 5-7: Phase 3
- [ ] Create validation framework
- [ ] Create utility library (date, number, export)
- [ ] Create dashboard component library
- [ ] Consolidate mobile dashboards (14 → 1 config)
- [ ] Create API module consolidation

### Week 8-10: Testing & Documentation
- [ ] Write unit tests for base classes
- [ ] Write tests for hooks
- [ ] Create developer guide
- [ ] Create migration checklist
- [ ] Train team on new patterns

---

## How to Use These Consolidations

### Using Constants

```python
# Instead of this:
if status == 'pending':
    pass

# Do this:
from constants import InvoiceStatus
if status == InvoiceStatus.PENDING.value:
    pass
```

### Using Base Mixins

```python
from models.base import AuditMixin, ApprovalFieldsMixin
from extensions import db

class MyModel(db.Model, AuditMixin, ApprovalFieldsMixin):
    __tablename__ = 'my_table'
    id = db.Column(db.Integer, primary_key=True)
    # created_at, updated_at inherited
    # created_by_id, updated_by_id inherited
    # approval_status, approved_by_id, etc. inherited
```

### Using Frontend Hooks

```javascript
import { usePaginatedData, useFormInput, useModalState } from '../hooks'

function MyComponent() {
  const { data, loading, page, setPage } = usePaginatedData('/api/endpoint')
  const { formData, handleChange } = useFormInput({ name: '' })
  const { showCreateModal, setShowCreateModal } = useModalState()

  // Use state in JSX...
}
```

---

## Migration Checklist

### For Each Model File:
- [ ] Add imports: `from models.base import AuditMixin, ApprovalFieldsMixin`
- [ ] Add imports: `from constants import [RelevantStatus]`
- [ ] Remove manual timestamp fields
- [ ] Remove manual audit fields
- [ ] Remove manual approval fields (if applicable)
- [ ] Update status default to use constant
- [ ] Update any status validation to use constants
- [ ] Test to_dict() serialization
- [ ] Update any status checks in model methods

### For Each Route File:
- [ ] Replace hardcoded status strings with constants
- [ ] Replace validation logic with decorator (Phase 2)
- [ ] Replace logging code with decorator (Phase 2)
- [ ] Test all endpoints

### For Each Page Component:
- [ ] Replace pagination state with `usePaginatedData` hook
- [ ] Replace form state with `useFormInput` hook
- [ ] Replace modal state with `useModalState` hook
- [ ] Test component functionality
- [ ] Verify API calls still work

---

## Next Steps

1. **Review This Guide** - Understand the patterns
2. **Try on Sample Model** - Apply to Invoice model
3. **Try on Sample Route** - Update a finance route
4. **Try on Sample Page** - Update Staff page
5. **Feedback & Refinement** - Adjust patterns if needed
6. **Scale to Remaining Code** - Apply systematically

---

## Questions & Support

For questions about:
- **Constants usage** → See `constants/` directory
- **Base mixins** → See `models/base.py`
- **Frontend hooks** → See `src/hooks/`
- **Implementation examples** → See next section

---

## Detailed Examples

### Example 1: Converting a Model

**File:** `purchase_management/models/purchase.py`

**Before:**
```python
class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
```

**After:**
```python
from constants import PurchaseStatus
from models.base import AuditMixin, ApprovalFieldsMixin

class Purchase(db.Model, AuditMixin, ApprovalFieldsMixin):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default=PurchaseStatus.DRAFT.value)
    # Everything else inherited!
```

**Lines saved:** 10 lines per model × 20+ models = 200+ lines

---

## Success Metrics

After complete consolidation:

| Metric | Current | Target | Improvement |
|--------|---------|--------|------------|
| Backend Lines | ~15,000 | ~12,000 | -20% |
| Frontend Lines | ~19,600 | ~13,000 | -33% |
| Duplicate Code | ~3,000+ | <500 | -80% |
| New Feature Time | 1 week | 3-4 days | -40% |
| Bug Fix Time | 2-3 hours | 1-1.5 hours | -40% |

---

**Last Updated:** March 31, 2026
**Phase Status:** 1/3 Complete
**Next Review:** After 10 sample models/pages converted
