# Soft-Delete Implementation Guide

**Status**: Mixin created, migration ready, implementation in progress
**Scope**: 32 models across entire construction management system

---

## What is Soft-Delete?

Instead of permanently removing records, mark them as deleted. Benefits:
- ✓ Preserves referential integrity
- ✓ Enables audit trails
- ✓ Allows data recovery
- ✓ Supports compliance requirements
- ✓ No foreign key constraint violations

**Example**:
```
Users table BEFORE soft-delete:
┌─────┬─────────────┬────────┐
│ id  │ name        │ email  │
├─────┼─────────────┼────────┤
│ 1   │ John Doe    │ j@.... │
│ 2   │ Jane Smith  │ j@.... │
└─────┴─────────────┴────────┘

Users table AFTER soft-delete (with is_deleted flag):
┌─────┬─────────────┬────────┬────────────┬────────────┬────────────┐
│ id  │ name        │ email  │ is_deleted │ deleted_at │ deleted_by │
├─────┼─────────────┼────────┼────────────┼────────────┼────────────┤
│ 1   │ John Doe    │ j@.... │ 0          │ NULL       │ NULL       │
│ 2   │ Jane Smith  │ j@.... │ 1          │ 2026-04-04 │ 5          │
└─────┴─────────────┴────────┴────────────┴────────────┴────────────┘

Query: SELECT * FROM users WHERE is_deleted = 0
Result: Only John Doe (Jane is hidden, not deleted)
```

---

## Implementation Checklist

### ✅ Phase 1: Foundation (DONE)
- [x] Create SoftDeleteMixin in `extensions/soft_delete_mixin.py`
- [x] Create migration file `add_soft_delete_fields.py`
- [x] Document soft-delete operations

### ⏳ Phase 2: Model Updates (IN PROGRESS)
- [ ] Update all 32 models to inherit from SoftDeleteMixin
- [ ] Test model changes
- [ ] Run migration

### ⏳ Phase 3: Query Updates
- [ ] Update all GET routes to exclude deleted records
- [ ] Update all LIST/FILTER routes to exclude deleted records
- [ ] Update relationships to handle deleted records

### ⏳ Phase 4: Delete Route Updates
- [ ] Change DELETE endpoints to use `soft_delete()` instead of `db.session.delete()`
- [ ] Add user_id tracking for audit trail

### ⏳ Phase 5: Recovery (Optional)
- [ ] Create RESTORE endpoints for admin recovery
- [ ] Add soft-delete status to admin dashboard

---

## How to Update Each Model

### Template for Staff Model

**BEFORE** (Current):
```python
class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
```

**AFTER** (With Soft-Delete):
```python
from extensions.soft_delete_mixin import SoftDeleteMixin

class Staff(db.Model, SoftDeleteMixin):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    # Soft-delete fields added by mixin:
    # is_deleted = db.Column(db.Boolean, default=False)
    # deleted_at = db.Column(db.DateTime, nullable=True)
    # deleted_by = db.Column(db.Integer, nullable=True)
```

### Models Requiring Updates (32 total)

**Core Models**:
1. staff.py - Staff
2. user_management/models.py - User, Role
3. project_management/models/models.py - Project, ProjectAssignment, ProjectStaffHistory, ProjectTask
4. material_management/models.py - Material
5. supplier_management/models.py - Supplier
6. client_management/models.py - Client

**Finance Models**:
7. finance_management/models/ - CashTransaction, ApprovalRequest, BudgetAllocation, ChartOfAccounts, Invoice, Payment, Retention

**Vehicle Models**:
8. vehicle_management/models.py - Vehicle, DriverVehicleAssignment, VehicleMaintenance, FuelLog

**Purchase Models**:
9. purchase_management/models.py - PurchaseOrder, PurchaseLineItem, PurchaseReturn

**Admin/Company Models**:
10. company_settings/models.py - Company, CompanySettings
11. admin_management/models.py - ActivityLog

**Other Models**:
12. attendance/models.py - Attendance, AttendancePhotoApproval
13. expense_model.py - Expense

---

## How to Update DELETE Routes

### Template for Staff DELETE

**BEFORE** (Current - Hard Delete):
```python
@staff_bp.route('/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    try:
        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff")

        # ❌ Permanently removes record
        db.session.delete(staff)
        db.session.commit()

        return success_response(message="Staff deleted")
    except Exception as e:
        db.session.rollback()
        return server_error_response(details=str(e))
```

**AFTER** (Soft Delete):
```python
@staff_bp.route('/<int:staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff(staff_id):
    try:
        current_user_id = get_jwt_identity()
        staff = Staff.query.get(staff_id)
        if not staff:
            return not_found_response("Staff")

        # ✓ Mark as deleted, preserves record
        staff.soft_delete(user_id=current_user_id)
        db.session.commit()

        # Log activity
        log_entity_action(
            user_id=current_user_id,
            company_id=staff.company_id,
            entity_type='Staff',
            entity_id=staff_id,
            action='SOFT_DELETE',
            old_values=staff.to_dict(),
            entity_name=f"{staff.first_name} {staff.last_name}"
        )

        return success_response(message="Staff deleted")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Delete staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to delete staff")
```

---

## How to Update GET Routes

### Template for Getting Staff (Exclude Deleted)

**BEFORE** (Shows deleted records):
```python
@staff_bp.route('/', methods=['GET'])
@jwt_required()
def get_staff():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # ❌ Includes deleted staff
        paginated = Staff.query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[s.to_dict() for s in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Staff retrieved"
        )
    except Exception as e:
        return server_error_response(details=str(e))
```

**AFTER** (Excludes deleted records):
```python
@staff_bp.route('/', methods=['GET'])
@jwt_required()
def get_staff():
    try:
        from extensions.soft_delete_mixin import apply_soft_delete_filter

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        # ✓ Filter out deleted staff
        query = Staff.query
        query = apply_soft_delete_filter(query, Staff)

        paginated = query.paginate(page=page, per_page=per_page)

        return paginated_response(
            items=[s.to_dict() for s in paginated.items],
            total=paginated.total,
            page=page,
            per_page=per_page,
            message="Staff retrieved"
        )
    except Exception as e:
        logger.error(f"Get staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to retrieve staff")
```

### Quick Alternative (Direct Filter):
```python
# Instead of using helper function, add to query directly:
query = Staff.query.filter(Staff.is_deleted == False)
# Or shorter:
query = Staff.query.filter_by(is_deleted=False)
```

---

## Restoration Endpoint (Optional)

For admin recovery of deleted records:

```python
@staff_bp.route('/<int:staff_id>/restore', methods=['POST'])
@jwt_required()
@admin_required  # Only admins can restore
def restore_staff(staff_id):
    """Restore a soft-deleted staff member"""
    try:
        # Get deleted staff (using filter with is_deleted=True)
        staff = Staff.query.filter_by(id=staff_id, is_deleted=True).first()
        if not staff:
            return error_response("No deleted staff found with this ID", status_code=404)

        staff.restore()  # Reset soft-delete fields
        db.session.commit()

        # Log restoration
        log_entity_action(
            user_id=get_jwt_identity(),
            company_id=staff.company_id,
            entity_type='Staff',
            entity_id=staff_id,
            action='RESTORE',
            new_values=staff.to_dict(),
            entity_name=f"{staff.first_name} {staff.last_name}"
        )

        return success_response(staff.to_dict(), "Staff restored")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Restore staff error: {str(e)}", exc_info=True)
        return server_error_response(details="Failed to restore staff")
```

---

## Running the Migration

```bash
# In project root:
flask db migrate -m "Add soft-delete fields to all models"
flask db upgrade

# Or manually:
from flask_migrate import Migrate
migrate = Migrate(app, db)
db.upgrade()
```

---

## Testing Soft-Delete

```python
# Test soft-delete
staff = Staff.get_active(1)  # Get non-deleted
staff.soft_delete(user_id=5)
db.session.commit()

# Verify deletion
deleted_staff = Staff.get_active(1)  # Returns None (filtered out)
all_staff = Staff.query.get(1)  # Returns the record (with is_deleted=True)

# Test restoration
staff.restore()
db.session.commit()
recovered_staff = Staff.get_active(1)  # Returns the record again
```

---

## Query Performance Considerations

**Index on is_deleted column** (added by migration):
- Ensures soft-delete filters are fast
- Most queries will have `WHERE is_deleted = 0`
- Index helps database find non-deleted records quickly

**Before & After Performance**:
```sql
-- Slow (without index):
SELECT * FROM staff WHERE is_deleted = 0;  -- Full table scan

-- Fast (with index):
SELECT * FROM staff WHERE is_deleted = 0;  -- Index scan (10x faster)
```

---

## Compliance Benefits

✅ **GDPR Compliance**:
- Keep data for audit trails
- Show deletion timestamps
- Track who deleted what

✅ **Accounting Standards**:
- Preserve transaction history
- Maintain referential integrity
- Support audit requirements

✅ **Data Recovery**:
- Recover deleted records
- Maintain historical data
- Support investigation

---

## Files Created

1. ✅ `/extensions/soft_delete_mixin.py` - Mixin implementation
2. ✅ `/migrations/versions/add_soft_delete_fields.py` - Database migration
3. 📝 This guide

## Next Steps

1. Update all 32 models to inherit SoftDeleteMixin
2. Run migration: `flask db upgrade`
3. Update DELETE routes to use `soft_delete()`
4. Update GET/LIST routes to filter with `is_deleted = 0`
5. Add restoration endpoints (optional)
6. Test end-to-end
