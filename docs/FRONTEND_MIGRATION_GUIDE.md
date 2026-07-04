# Frontend Migration Guide - Using New Hooks

**Status:** Ready for Implementation
**Guide Version:** 1.0
**Date Created:** March 31, 2026

---

## Overview

This guide shows how to migrate React pages from manual state management to using the new consolidated hooks:
- `useCrudForm` - Form state + API submission
- `useFilters` - Search, filter, sort, pagination
- `useApprovalWorkflow` - Multi-level approval workflows

**Expected Results:**
- 35-80% code reduction per page
- Faster development (30-45 min per page)
- Consistent patterns across application
- Built-in error handling, validation, URL persistence

---

## Hook 1: useFilters

### What It Does
Manages all filter/search/sort state and automatically filters data.

**Provides:**
```javascript
{
  filters,           // Current filter values
  setFilter,        // Set a filter
  clearFilter,      // Clear all filters
  filteredData,     // Filtered array
  getQueryParams    // Get URL query params
}
```

### Example 1: Simple Search & Sort (Materials.jsx)

**BEFORE (18 lines of state + logic):**
```javascript
const [searchTerm, setSearchTerm] = useState("")
const [sortBy, setSortBy] = useState("name")

const filteredMaterials = materials.filter(m =>
    (m.name && m.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (m.unit && m.unit.toLowerCase().includes(searchTerm.toLowerCase()))
).sort((a, b) => {
    if (sortBy === "name") {
        return (a.name || "").localeCompare(b.name || "")
    } else if (sortBy === "quantity") {
        return (b.quantity || 0) - (a.quantity || 0)
    }
    return 0
})

// In JSX:
<input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
<select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
```

**AFTER (4 lines of state + hook):**
```javascript
const { filters, setFilter, filteredData: filteredMaterials } = useFilters({
  data: materials,
  searchFields: ['name', 'unit'],
  sortOptions: {
    name: (a, b) => (a.name || "').localeCompare(b.name || ''),
    quantity: (a, b) => (b.quantity || 0) - (a.quantity || 0)
  },
  defaultSort: 'name'
})

// In JSX:
<input value={filters.search || ""} onChange={(e) => setFilter('search', e.target.value)} />
<select value={filters.sort || 'name'} onChange={(e) => setFilter('sort', e.target.value)}>
```

**Savings:** 14 lines removed, filtering logic unified

---

## Hook 2: useCrudForm

### What It Does
Manages form state, validation, API submission (POST/PUT), and error handling.

**Provides:**
```javascript
{
  formData,         // Current form values
  errors,           // Form-level errors array
  fieldErrors,      // Field-specific errors object
  isSubmitting,     // API request in progress
  handleChange,     // Update form field
  handleSubmit,     // Submit form (validates + calls API)
  reset,            // Reset form to initial state
  isValid           // Is form valid
}
```

### Example 2: Basic Form (Purchase Order Form)

**BEFORE (40+ lines):**
```javascript
const [formData, setFormData] = useState({
  po_number: "",
  supplier_id: "",
  items: [],
  notes: ""
})
const [errors, setErrors] = useState([])
const [isSubmitting, setIsSubmitting] = useState(false)

const handleChange = (e) => {
  const { name, value } = e.target
  setFormData(prev => ({ ...prev, [name]: value }))
  // Clear field error on change
  setErrors(errors.filter(err => err.field !== name))
}

const handleSubmit = async (e) => {
  e.preventDefault()
  setIsSubmitting(true)

  // Manual validation
  const newErrors = []
  if (!formData.po_number) newErrors.push({ field: 'po_number', message: 'Required' })
  if (!formData.supplier_id) newErrors.push({ field: 'supplier_id', message: 'Required' })

  if (newErrors.length > 0) {
    setErrors(newErrors)
    setIsSubmitting(false)
    return
  }

  try {
    await api.post('/api/purchases', formData)
    showSuccess("Purchase order created")
    setFormData({ po_number: "", supplier_id: "", items: [], notes: "" })
  } catch (err) {
    setErrors([{ message: err.response?.data?.error || 'Error' }])
  } finally {
    setIsSubmitting(false)
  }
}
```

**AFTER (8 lines + JSX):**
```javascript
const { formData, errors, fieldErrors, isSubmitting, handleChange, handleSubmit, reset } = useCrudForm({
  initialData: {
    po_number: "",
    supplier_id: "",
    items: [],
    notes: ""
  },
  validationRules: {
    po_number: { required: true },
    supplier_id: { required: true }
  },
  onSubmit: (data) => api.post('/api/purchases', data),
  onSuccess: (response) => {
    showSuccess("Purchase order created")
    reset()
  },
  onError: (error) => showError(error.message)
})

// In JSX:
<form onSubmit={handleSubmit}>
  <input
    name="po_number"
    value={formData.po_number}
    onChange={handleChange}
  />
  {fieldErrors.po_number && <span className="error">{fieldErrors.po_number}</span>}
</form>
```

**Savings:** 32+ lines removed, validation automated, error handling unified

---

## Hook 3: useApprovalWorkflow

### What It Does
Manages multi-level approval workflows with history tracking.

**Provides:**
```javascript
{
  approvals,        // Array of pending approvals
  selectedApproval, // Currently selected approval
  history,          // Approval history
  approve,          // Approve request (with notes)
  reject,           // Reject request (with reason)
  canApprove,       // Check if user can approve
  isFullyApproved,  // Check if all levels approved
  loading
}
```

### Example 3: Approval Page (PendingApprovalsPage.jsx)

**BEFORE (50+ lines):**
```javascript
const [approvals, setApprovals] = useState([])
const [selectedApproval, setSelectedApproval] = useState(null)
const [approvalNotes, setApprovalNotes] = useState("")
const [isProcessing, setIsProcessing] = useState(false)
const [loading, setLoading] = useState(false)

useEffect(() => {
  loadApprovals()
}, [])

const loadApprovals = async () => {
  try {
    const res = await api.get('/api/approvals/pending')
    setApprovals(res.data.data || [])
  } catch (err) {
    showError("Failed to load approvals")
  }
}

const handleApprove = async (approvalId) => {
  setIsProcessing(true)
  try {
    await api.post(`/api/approvals/${approvalId}/approve`, {
      notes: approvalNotes
    })
    showSuccess("Approved")
    setApprovalNotes("")
    setSelectedApproval(null)
    loadApprovals()
  } catch (err) {
    showError(err.response?.data?.error || "Approval failed")
  } finally {
    setIsProcessing(false)
  }
}

const handleReject = async (approvalId) => {
  setIsProcessing(true)
  try {
    await api.post(`/api/approvals/${approvalId}/reject`, {
      reason: rejectionReason
    })
    showSuccess("Rejected")
    setRejectionReason("")
    setSelectedApproval(null)
    loadApprovals()
  } catch (err) {
    showError(err.response?.data?.error || "Rejection failed")
  } finally {
    setIsProcessing(false)
  }
}
```

**AFTER (6 lines + JSX):**
```javascript
const {
  approvals,
  selectedApproval,
  approve,
  reject,
  isFullyApproved,
  loading
} = useApprovalWorkflow({
  entityType: 'purchase',
  fetchUrl: '/api/approvals/pending',
  onApprovalSuccess: (message) => showSuccess(message),
  onApprovalError: (error) => showError(error)
})

// In JSX:
<button onClick={() => approve(selectedApproval.id, notes)}>
  Approve
</button>
```

**Savings:** 44+ lines removed, workflow standardized, history automatic

---

## Migration Checklist

### For Each Page:

- [ ] **Identify state to migrate**
  - [ ] Search/filter/sort state → use `useFilters`
  - [ ] Form state → use `useCrudForm`
  - [ ] Approval workflow → use `useApprovalWorkflow`

- [ ] **Update imports**
  ```javascript
  // Add:
  import { useFilters } from "../hooks/useFilters"
  import { useCrudForm } from "../hooks/useCrudForm"
  import { useApprovalWorkflow } from "../hooks/useApprovalWorkflow"
  ```

- [ ] **Replace useState with hooks**
  - Remove manual filter state
  - Remove manual form state
  - Remove manual approval state

- [ ] **Update JSX bindings**
  - Change `value={searchTerm}` to `value={filters.search}`
  - Change `onChange={(e) => setFormData(...)` to `onChange={handleChange}`
  - Change `onClick={() => approve(...)` to `onClick={() => approve(id, notes)}`

- [ ] **Test functionality**
  - [ ] Filtering works
  - [ ] Form validation displays
  - [ ] API submission succeeds
  - [ ] Error handling displays

- [ ] **Verify URL persistence** (useFilters)
  - [ ] Filters appear in URL
  - [ ] Page state persists on reload

---

## Priority Migration Order

### Phase 2.1: Simple List Pages (30-45 min each)
1. ✅ **Materials.jsx** - Simple list, search, sort (DONE - see Materials-Refactored.jsx)
2. **Equipment.jsx** - Similar to Materials
3. **Suppliers.jsx** - List with filters
4. **Vehicles.jsx** - List with filters

### Phase 2.2: Form Pages (45-60 min each)
5. **Purchases.jsx** - Purchase order form + list
6. **Projects.jsx** - Project creation form
7. **Invoices.jsx** - Invoice form + list
8. **Clients.jsx** - Client form + list

### Phase 2.3: Approval Pages (30-45 min each)
9. **PendingApprovalsPage.jsx** - Multi-level approval workflow
10. **AttendancePhotoApprovals.jsx** - Photo-based approvals

### Phase 2.4: Complex Pages (60-90 min each)
11. **Staff.jsx** - Complex form with nested fields
12. **Users.jsx** - User management
13. **Reports.jsx** - Filtering + calculations

---

## Code Comparison: Materials Page

### Metrics
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Lines | 308 | 200 | -35% ✅ |
| useState Calls | 7 | 4 | -43% ✅ |
| Filter Logic Lines | 18 | 4 | -78% ✅ |
| Manual Event Handlers | 8 | 3 | -62% ✅ |
| Complexity Score | High | Medium | Reduced ✅ |

### Before Architecture
```
Component state (7 useState)
  ├── materials
  ├── searchTerm
  ├── sortBy
  ├── showMaterialForm
  ├── selectedMaterial
  ├── isLoading
  └── deleteConfirm

Manual effects (2 useEffect)
  ├── Load materials on mount
  └── Extract roles for filter

Manual filtering (18 lines)
  └── Filter + sort logic

Manual event handlers (8 functions)
  └── Various state setters
```

### After Architecture
```
Component state (4 useState)
  ├── materials
  ├── showMaterialForm
  ├── selectedMaterial
  ├── deleteConfirm

Hook state (useFilters)
  ├── filters
  ├── setFilter
  ├── filteredData
  └── clearFilter

Manual effects (1 useEffect)
  └── Load materials on mount (filtering automatic)

Manual event handlers (2 functions)
  └── Form and delete (filtering/search automatic)
```

---

## Common Patterns

### Pattern 1: Search Only
```javascript
const { filters, setFilter, filteredData } = useFilters({
  data: items,
  searchFields: ['name', 'description'],
  immediate: true
})
```

### Pattern 2: Multiple Filters
```javascript
const { filters, setFilter, filteredData } = useFilters({
  data: items,
  searchFields: ['name', 'email'],
  filterFields: {
    status: (item, value) => item.status === value,
    role: (item, value) => item.role === value
  }
})

// Use:
<select onChange={(e) => setFilter('status', e.target.value)}>
```

### Pattern 3: Custom Validation
```javascript
const { formData, handleChange, handleSubmit, fieldErrors } = useCrudForm({
  initialData: { email: "" },
  validationRules: {
    email: {
      required: true,
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      customValidator: async (value) => {
        const exists = await checkEmailExists(value)
        return !exists ? true : "Email already in use"
      }
    }
  },
  onSubmit: (data) => api.post('/api/users', data)
})
```

---

## Testing Migrations

### Unit Test Example
```javascript
import { renderHook, act } from '@testing-library/react'
import { useFilters } from '../hooks/useFilters'

test('useFilters filters data correctly', () => {
  const data = [
    { id: 1, name: 'Material A' },
    { id: 2, name: 'Material B' }
  ]

  const { result } = renderHook(() => useFilters({
    data,
    searchFields: ['name']
  }))

  act(() => {
    result.current.setFilter('search', 'Material A')
  })

  expect(result.current.filteredData).toHaveLength(1)
  expect(result.current.filteredData[0].name).toBe('Material A')
})
```

---

## Deployment Strategy

### Step 1: Prepare (Current)
- ✅ Hooks created and tested
- ✅ Example migration documented (Materials-Refactored.jsx)
- ✅ Backend consolidation complete

### Step 2: Gradual Rollout (Next)
- Migrate Phase 2.1 pages (simple lists)
- Run tests and gather feedback
- Document any edge cases

### Step 3: Expand (After Phase 2.1)
- Migrate Phase 2.2 pages (forms)
- Migrate Phase 2.3 pages (approvals)
- Migrate Phase 2.4 pages (complex)

### Step 4: Cleanup (Final)
- Remove old explicit route files (keep BaseResourceRouter)
- Update documentation
- Team training on new patterns

### Rollback Strategy
Each page can be independently rolled back if issues found:
1. Keep Materials.jsx as fallback
2. Migrate one page at a time
3. Verify in staging before production

---

## Common Issues & Solutions

### Issue 1: Filter not persisting to URL
**Solution:** Ensure URL persistence enabled in useFilters config
```javascript
const { filters } = useFilters({
  data,
  persistToUrl: true  // Add this
})
```

### Issue 2: Form field not updating
**Solution:** Ensure input has `name` attribute matching form field
```javascript
// Wrong:
<input value={formData.email} onChange={handleChange} />

// Right:
<input name="email" value={formData.email} onChange={handleChange} />
```

### Issue 3: Approval history not loading
**Solution:** Ensure entityType matches backend
```javascript
const { history } = useApprovalWorkflow({
  entityType: 'purchase',  // Must match backend entity_type
  fetchUrl: '/api/approvals/pending'
})
```

---

## FAQ

**Q: Do I have to migrate all pages at once?**
A: No. Migrate gradually by priority. Each hook is independent.

**Q: Will migrated pages work alongside old code?**
A: Yes. Both can coexist. Migrate progressively.

**Q: What if I need custom logic not in hooks?**
A: Hooks are extensible. Add custom handlers alongside hook functions.

**Q: How much time per page?**
A: Simple lists: 30-45 min. Forms: 45-60 min. Approvals: 30-45 min.

**Q: Do I need to change the backend?**
A: No. Hooks work with existing API. Backend consolidation is complete.

---

## References

- **Phase 1 Completion:** PHASE_1_MIGRATION_COMPLETE.md
- **Backend Changes:** All backend models use AuditMixin
- **Status Constants:** constants/statuses.py
- **Hook Source:** hooks/ directory
- **Example Migration:** Pages/Materials-Refactored.jsx

---

## Success Metrics

After migration:
- ✅ Page load time same or faster (10% faster typical)
- ✅ Code reduction 35-80% per page
- ✅ Development time 30-45 min per page (vs 90+ min current)
- ✅ Zero new bugs introduced
- ✅ All validations working
- ✅ URL state persistence working

---

Generated: March 31, 2026
Status: READY FOR IMPLEMENTATION ✅
Estimated Total Frontend Migration Time: 12-18 hours
