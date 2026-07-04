# Staff API 500 Error - Diagnostic & Fix Guide

**Error:** `POST http://localhost:5000/api/staff 500 (INTERNAL SERVER ERROR)`

**Root Cause:** Backend server is not running, or backend is crashing on the create staff endpoint

---

## SOLUTION

### Step 1: Start the Backend Server

```bash
cd D:\Projects\backend
python -m flask run --port=5000
```

**Expected output:**
```
WARNING in werkzeug: This is a development server. Do not use it in production deployments.
INFO in werkzeug: Running on http://127.0.0.1:5000
```

### Step 2: Verify Backend is Running

Open a new terminal and test:
```bash
curl http://localhost:5000/api/health
```

Should return: `{"status": "ok"}`

### Step 3: Test Staff Creation

Try adding staff through the UI and watch the backend terminal for error messages.

---

## If Backend is Running but Still Getting 500 Error

### Check Backend Logs

Look for detailed error message in the Flask terminal output. Common issues:

#### Issue 1: Missing Required Fields
**Error message:** "Validation failed"
**Solution:** Ensure form includes:
- First Name (or Name to be split)
- Last Name (or Name to be split)
- Personal Phone (or Phone)
- Joining Date (YYYY-MM-DD format)
- Role (select from dropdown)
- Salary
- PF (percentage, 0-100)
- ESI (percentage, 0-100)

#### Issue 2: Database Connection Error
**Error message:** `(psycopg2.OperationalError)` or `(sqlite3.OperationalError)`
**Solution:** Ensure database is running and configured correctly

#### Issue 3: Duplicate Staff ID
**Error message:** `IntegrityError: duplicate key value violates unique constraint "staff_staff_id_key"`
**Solution:** Clear staff table or check for duplicate entries

#### Issue 4: Duplicate Phone Number
**Error message:** "Staff member with this phone already exists"
**Solution:** Use a different phone number for new staff

#### Issue 5: Missing Dependencies
**Error message:** `ImportError` or `ModuleNotFoundError`
**Solution:** Install missing packages:
```bash
pip install -r requirements.txt
```

---

## Detailed Validation Requirements

The backend validates staff data. All these fields are REQUIRED:

### Personal Information (Required)
- ✅ First Name OR Name (Name will be split)
- ✅ Last Name OR Name (Name will be split)
- ✅ Personal Phone OR Phone (required)
- ✅ Joining Date (format: YYYY-MM-DD)

### Employment Details (Required)
- ✅ Role (Manager, Supervisor, Engineer, Driver, Worker, etc.)

### Financial Details (Required)
- ✅ Salary (numeric value, can't be negative)
- ✅ PF (Provident Fund %, 0-100)
- ✅ ESI (Employee State Insurance %, 0-100)

### Contact Information (Optional but Recommended)
- ⭕ Personal Email (optional, must have @ if provided)
- ⭕ Phone Number (optional but field labeled required)

### Address (Optional)
- ⭕ Present Address
- ⭕ Permanent Address

### Bank Details (Optional)
- ⭕ Bank Name
- ⭕ Account Number
- ⭕ IFSC Code
- ⭕ Account Holder Name

---

## Frontend Form Checklist

When creating a new staff member, ensure form has these fields filled:

```
✅ Name (or First Name + Last Name)
✅ Phone Number
✅ Email (optional, but recommended)
✅ Department (optional, recommended)
✅ Designation / Role
✅ Joining Date (YYYY-MM-DD format)
✅ Salary (numeric)
✅ PF Percentage (0-100)
✅ ESI Percentage (0-100)
```

### Example Valid Request Body:
```json
{
  "name": "John Smith",
  "personal_phone": "+91-9876543210",
  "personal_email": "john@company.com",
  "department": "Engineering",
  "designation": "Site Engineer",
  "role": "Engineer",
  "joining_date": "2026-04-01",
  "salary": 50000,
  "pf": 12.0,
  "esi": 0.75,
  "employment_type": "Full-time"
}
```

---

## Backend API Code Analysis

### Create Staff Endpoint
**Route:** `POST /api/staff`
**Location:** `D:\Projects\backend\construction_management\staff_management\routes.py` (Line 235)

### Validation Function
**Location:** `D:\Projects\backend\construction_management\staff_management\routes.py` (Line 23)

**Validates:**
1. Name not empty (max 100 chars)
2. Role not empty (max 100 chars)
3. Phone not empty (max 20 chars)
4. Email valid if provided (max 100 chars)
5. Joining date valid (YYYY-MM-DD format)
6. Salary valid number (≥ 0)
7. PF valid percentage (0-100)
8. ESI valid percentage (0-100)

### User ID Generation
**Location:** `D:\Projects\backend\construction_management\staff_management\user_id_service.py`

**Generates:** `STF-YYYY-NNN` format (e.g., STF-2026-001)
- Automatically increments per company per year
- Ensures uniqueness with duplicate check

---

## Step-by-Step Debugging

### Step 1: Check Backend Console
When you submit staff form, watch for error in backend terminal.

### Step 2: Check Network Tab
Open browser DevTools (F12) → Network tab
- Look for failed POST to `/api/staff`
- Click request → Response tab
- Read error message returned by backend

### Step 3: Check Server Health
Test if backend responding:
```bash
curl http://localhost:5000/api
```

### Step 4: Check Database
Verify database is connected:
```bash
# If using SQLite
ls -la D:\Projects\backend\instance\

# If using PostgreSQL
psql -U username -d database_name -c "SELECT * FROM staff LIMIT 1;"
```

---

## Common Solutions

### Solution 1: Start Backend Server
```bash
cd D:\Projects\backend
python -m flask run --port=5000
```

### Solution 2: Check Python Environment
```bash
python --version  # Should be 3.8+
pip list | grep flask  # Flask should be installed
```

### Solution 3: Install Dependencies
```bash
cd D:\Projects\backend
pip install -r requirements.txt
```

### Solution 4: Reset Database (if corrupted)
```bash
# Backup existing database first!
cd D:\Projects\backend
python
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>>     print("Database reset")
>>> exit()
```

---

## Testing the Fix

### Test 1: Server Running
```bash
curl http://localhost:5000/api/health
```
Expected: `{"status": "ok"}`

### Test 2: Authentication
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "password"}'
```
Should return JWT token

### Test 3: Create Staff
```bash
curl -X POST http://localhost:5000/api/staff \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Test Employee",
    "personal_phone": "9876543210",
    "joining_date": "2026-04-01",
    "role": "Worker",
    "salary": 30000,
    "pf": 12,
    "esi": 0.75
  }'
```
Should return: `{"success": true, "message": "Staff member created successfully"}`

---

## Prevention Checklist

- ✅ Backend server running and listening on port 5000
- ✅ Database connection configured correctly
- ✅ All dependencies installed (`pip install -r requirements.txt`)
- ✅ Environment variables set (if needed)
- ✅ JWT token valid and not expired
- ✅ Required fields in request body
- ✅ Date formats correct (YYYY-MM-DD)
- ✅ Numeric fields are actual numbers (not strings)

---

## Next Steps

1. **Start Backend Server** - Run Flask development server
2. **Test Connection** - Verify API responds to health check
3. **Try Staff Creation** - Attempt to add a new staff member
4. **Monitor Logs** - Watch terminal for specific error messages
5. **Report Detailed Error** - If still failing, provide:
   - Exact error message from backend terminal
   - Request body you're sending
   - Response body from API
   - Browser DevTools Console output
   - Network tab response details

