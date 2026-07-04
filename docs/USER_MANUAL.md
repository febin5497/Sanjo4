# CONSTRUCTION FINANCE MANAGEMENT SYSTEM
## Comprehensive User Manual

**Version:** 1.0
**Date:** April 2026
**Status:** Production Ready

---

## TABLE OF CONTENTS

1. [Getting Started](#getting-started)
2. [Dashboard & Navigation](#dashboard--navigation)
3. [Project Management](#project-management)
4. [Staff & HR Management](#staff--hr-management)
5. [Attendance System](#attendance-system)
6. [Finance Management](#finance-management)
7. [Procurement Pipeline](#procurement-pipeline)
8. [Administration & Settings](#administration--settings)
9. [Common Workflows](#common-workflows)
10. [Tips & Best Practices](#tips--best-practices)
11. [Troubleshooting](#troubleshooting)

---

# GETTING STARTED

## System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Screen resolution: 1024x768 or higher (1920x1080 recommended)

## Logging In

### Step 1: Access the Application
1. Open your web browser
2. Navigate to your organization's application URL
3. You should see the login screen

### Step 2: Enter Credentials
1. Enter your **Username/Email** in the first field
2. Enter your **Password** in the second field
3. Click **"Login"** button

### Step 3: Successful Login
- You'll be redirected to the **Dashboard**
- Your name appears in the top-right corner
- You can now access all modules based on your permissions

### Forgot Password?
- Click **"Forgot Password?"** link on login screen
- Enter your email address
- Follow the reset instructions sent to your email

---

## User Profile

### Access Your Profile
1. Click your **name/avatar** in top-right corner
2. Select **"Profile"** from dropdown menu
3. You'll see your profile page

### Profile Information Available
- **Full Name**
- **Email Address**
- **Department/Role**
- **Contact Number**
- **Profile Picture**
- **Job Title**
- **Permissions/Roles assigned**

### Update Profile
1. Click **"Edit Profile"** button
2. Modify your information
3. Click **"Save Changes"**
4. Confirmation message appears

### Change Password
1. On profile page, click **"Change Password"**
2. Enter current password
3. Enter new password (twice for confirmation)
4. Click **"Update Password"**

### Logout
1. Click your name in top-right corner
2. Select **"Logout"**
3. You'll return to login screen

---

# DASHBOARD & NAVIGATION

## Main Dashboard

### What You See
The dashboard is your central hub showing key information at a glance.

### Dashboard Cards
| Card | Shows | Purpose |
|------|-------|---------|
| **Active Projects** | Number of ongoing projects | Quick overview of project count |
| **Total Staff** | Number of employees | HR summary |
| **Pending Approvals** | Items waiting for your approval | Action items for you |
| **Finance Summary** | Income, Expenses, Balance | Financial health snapshot |
| **Overdue Tasks** | Tasks past due date | Priority alerts |
| **Low Stock Items** | Inventory below minimum | Procurement alerts |

### Dashboard Charts
- **Project Timeline** - Shows projects by stage
- **Monthly Cash Flow** - Income vs Expenses by month
- **Staff Attendance Rate** - Overall attendance percentage
- **Budget vs Actual** - Spending against budget

### Navigation Menu
The left sidebar shows all available modules:

1. **Dashboard** - Home screen
2. **Projects** - Project management
3. **Staff** - Employee management
4. **Attendance** - Punch in/out and reports
5. **Finance** - Transactions and reports
6. **Procurement** - POs and supplies
7. **Store** - Inventory management
8. **Admin** - Settings and configuration
9. **Settings** - User preferences

### Search & Filter
- **Global Search** (top of page) - Search across all modules
- **Module Filters** - Filter data within each module
- **Date Pickers** - Select date ranges for reports

---

# PROJECT MANAGEMENT

## Projects Page

### View All Projects
1. Click **"Projects"** in left menu
2. See list of all projects in table format

### Project List Columns
| Column | Information |
|--------|-------------|
| **Project Name** | Name of the construction project |
| **Location** | Geographic location |
| **Client** | Client/Owner name |
| **Status** | Active, Completed, On Hold, Cancelled |
| **Start Date** | Project start date |
| **End Date** | Expected/Actual completion date |
| **Budget** | Total project budget |
| **Progress** | % completion |
| **Manager** | Project manager assigned |

### Create New Project
1. Click **"+ Add New Project"** button
2. Fill in the form:
   - **Project Name** (required)
   - **Description** (optional)
   - **Client Name** (required)
   - **Location** (required)
   - **Start Date** (required)
   - **End Date** (required)
   - **Budget Amount** (required)
   - **Project Manager** (select from staff list)
   - **Status** (Active/On Hold)
3. Click **"Create Project"**
4. Project appears in list

### Edit Project
1. Click project name or **"Edit"** button
2. Modify any fields
3. Click **"Save Changes"**

### Delete Project
1. Click **"Delete"** button (trash icon)
2. Confirm deletion
3. Project is removed from system

### Search & Filter Projects
1. Use **"Search"** box to find by name/client
2. Use **"Filter by Status"** dropdown
3. Use **"Filter by Manager"** dropdown
4. Results update automatically

---

## Project Details Page

### Access Project Details
1. Click project name from projects list
2. You'll see complete project information

### Project Details Sections

#### 1. Project Overview
- Project name, description, client
- Location on map view
- Start/End dates with progress bar
- Budget vs actual spending
- Project status

#### 2. Project Team
**View assigned staff:**
1. Click **"Team"** tab
2. See all staff assigned to project
3. Shows role, designation, contact info

**Add staff to project:**
1. Click **"+ Add Team Member"**
2. Select staff from dropdown
3. Select their role (Supervisor, Worker, Engineer, etc.)
4. Click **"Assign"**

**Remove staff:**
1. Click **"Remove"** button next to staff member
2. Confirm removal

#### 3. Project Tasks & Gantt Chart
**View tasks:**
1. Click **"Tasks"** tab
2. See all tasks with timeline

**Create new task:**
1. Click **"+ Add Task"**
2. Fill in:
   - **Task Name** (required)
   - **Description**
   - **Assigned To** (select staff)
   - **Start Date**
   - **Duration** (days)
   - **Priority** (Low/Medium/High)
3. Click **"Create Task"**

**Update task status:**
1. Click task in list
2. Change **Status** (Not Started → In Progress → Completed)
3. Add **% Complete**
4. Click **"Update"**

#### 4. Project Progress
**Track progress visually:**
- See timeline of completed vs remaining tasks
- View milestones achieved
- Check percentage completion
- Identify bottlenecks

#### 5. Project Costs
**View financial information:**
1. Click **"Costs"** tab
2. See breakdown by category:
   - Labor costs
   - Material costs
   - Equipment costs
   - Miscellaneous costs
3. Compare budget vs actual
4. View cost variance

#### 6. Project Map
**View project location:**
1. Click **"Map"** tab
2. Interactive map showing project site
3. Zoom in/out
4. Add site photos on map

#### 7. Site Photos
**View project photos:**
1. Click **"Photos"** tab
2. See photo timeline
3. Photos organized by date
4. Before/After comparisons

**Upload photos:**
1. Click **"+ Upload Photo"**
2. Select image file
3. Add caption/description
4. Click **"Upload"**

#### 8. Transactions
**View project finances:**
1. Click **"Transactions"** tab
2. See all financial transactions for project
3. Filter by type (Income/Expense)
4. Filter by date range

---

## Project Assignment Manager

### Access Staff Assignment
1. From Project Details, click **"Assign Staff"** button
2. Or go to **"Projects"** → **"Assignment Manager"**

### Assign Staff to Project
1. Select **Project** from dropdown
2. Click **"+ Add Team Member"**
3. Select **Staff Member**
4. Select **Role/Position**
5. Set **Start Date**
6. Set **End Date** (if temporary)
7. Click **"Assign"**
8. Confirmation appears

### View Current Assignments
- **Table shows:**
  - Staff name
  - Project assigned
  - Role
  - Duration
  - Status (Active/Completed)

### Remove Assignment
1. Click **"Remove"** button
2. Confirm removal
3. Staff removed from project

### Bulk Assign
1. Click **"Bulk Assign"**
2. Select multiple staff members
3. Select target project
4. Select role
5. Click **"Assign All"**

---

## Gantt Planner

### View Gantt Chart
1. Click **"Gantt Planner"** in Projects menu
2. Visual timeline showing all project tasks
3. Each bar represents a task with duration

### Gantt Chart Features

**Timeline View:**
- Horizontal axis = time (days/weeks/months)
- Vertical axis = tasks/milestones
- Bar color = task status (Gray=Not Started, Blue=In Progress, Green=Completed)

**Zoom In/Out:**
1. Use zoom controls top-right
2. View by days, weeks, or months
3. Adjust to your preferred granularity

**Drag & Reschedule:**
1. Click and drag task bar left/right
2. Changes task start date
3. Duration adjusts automatically
4. Click **"Save"** to confirm

**Add Dependencies:**
1. Click task bar
2. Select **"Add Dependency"**
3. Choose task it depends on
4. Task automatically adjusts timing

**Mark Complete:**
1. Click task bar
2. Drag right edge to mark % complete
3. Color shifts toward green as % increases

### Export Gantt Chart
1. Click **"Export"** button
2. Select format:
   - PNG image
   - PDF document
   - CSV data
3. Chart downloads to your computer

---

## Project Progress Tracking

### Access Progress Page
1. Click **"Project Progress"** from Projects menu
2. See all projects with visual progress indicators

### Progress Indicators
- **Overall Progress Bar** - % of project completed
- **Task Breakdown** - Not Started / In Progress / Completed counts
- **Timeline Status** - On Schedule / Ahead / Behind

### Detailed Progress View
1. Click specific project
2. See task-by-task breakdown
3. View milestone achievements
4. Check timeline status

### Update Progress
1. Click **"Edit Progress"**
2. Update task statuses
3. Add completion notes
4. Click **"Save"**

### Progress Reports
1. Click **"Generate Report"**
2. Select date range
3. Select report type:
   - Progress Summary
   - Detailed Task Report
   - Milestone Report
4. View or download report

---

## Project Cost Tracking

### Access Cost Page
1. Click **"Project Cost"** from Projects menu
2. See cost analysis for all projects

### Cost Breakdown
Shows costs by category:
- **Labor** - Staff wages and costs
- **Materials** - Building materials and supplies
- **Equipment** - Machinery and tools rental
- **Miscellaneous** - Other expenses

### Budget vs Actual
1. **Budget** - Planned amount
2. **Actual** - Amount spent so far
3. **Variance** - Difference (Over/Under budget)
4. **% Used** - Percentage of budget spent

### Cost Analysis
- **Pie chart** - Visual breakdown by category
- **Bar chart** - Budget vs Actual comparison
- **Trend line** - Cost spending over time

### Actions
1. Click project to see details
2. View transaction breakdown
3. Identify cost overruns
4. Export cost report

---

# STAFF & HR MANAGEMENT

## Staff Directory

### Access Staff List
1. Click **"Staff"** in left menu
2. See all employees in table format

### Staff List Information
| Column | Shows |
|--------|-------|
| **Name** | Employee full name |
| **Email** | Work email address |
| **Phone** | Contact number |
| **Department** | Department/Team |
| **Designation** | Job title |
| **Status** | Active/Inactive |
| **Joining Date** | Start date |
| **Manager** | Reporting manager |

### Search Staff
1. Use **"Search"** box
2. Type name, email, or phone
3. Results filter automatically

### Filter Staff
1. Click **"Filter"** button
2. Filter by:
   - Department
   - Designation
   - Status (Active/Inactive)
   - Manager
3. Click **"Apply"**

### Add New Staff

**Step 1: Click "+ Add New Staff"**

**Step 2: Fill Employee Details**
- **First Name** (required)
- **Last Name** (required)
- **Email** (required, must be unique)
- **Phone Number** (required)
- **Department** (select from list)
- **Designation** (select from list)
- **Joining Date** (required)

**Step 3: Emergency Contact**
- **Contact Name**
- **Relationship**
- **Phone Number**

**Step 4: Set Reporting Manager**
- Select manager from staff list
- Or leave blank if staff is manager

**Step 5: Click "Create Employee"**
- New employee added to system
- Welcome email sent automatically

### Edit Staff Information
1. Click staff name
2. Click **"Edit"** button
3. Modify fields
4. Click **"Save Changes"**

### Deactivate Staff
1. Click staff member
2. Click **"Deactivate"** button
3. Confirm action
4. Staff marked as inactive
5. Can be reactivated later

### Delete Staff
1. Click **"Delete"** button
2. Confirm deletion
3. Employee removed from system
4. All historical data retained

### View Staff Profile
1. Click staff name
2. See complete profile:
   - Personal information
   - Contact details
   - Department/Role
   - Assigned projects
   - Attendance record
   - Performance metrics

---

## Expense Approvals (Tier 1)

### Purpose
Employees submit expenses for manager approval.
**Tier 1 handles:** Expenses ≤ ₹50,000

### View Pending Expenses
1. Click **"Expense Approvals"** in Staff menu
2. See list of pending expense requests
3. Shows submitter, amount, category, submission date

### Expense Details
Click any expense to see:
- **Submitter Name** - Who submitted
- **Amount** - Expense amount
- **Category** - Type (Travel, Materials, etc.)
- **Description** - What for
- **Date Incurred** - When it happened
- **Receipt/Documentation** - Attached files
- **Status** - Pending/Approved/Rejected

### Approve an Expense
1. Click expense in list
2. Review details and attached receipts
3. Click **"✓ Approve"** button
4. Add optional approval notes
5. Click **"Confirm Approval"**
6. Expense approved and posted to transactions

### Reject an Expense
1. Click expense in list
2. Review details
3. Click **"✗ Reject"** button
4. **Required:** Add reason for rejection
5. Click **"Confirm Rejection"**
6. Employee notified to resubmit

### Filter Expenses
- By **Status** (Pending/Approved/Rejected)
- By **Category**
- By **Date Range**
- By **Submitter**

### Bulk Approve
1. Check boxes next to expenses
2. Click **"Bulk Approve"**
3. Add notes (optional)
4. Confirm
5. All selected expenses approved

### Export Expense Report
1. Click **"Export"** button
2. Select format (PDF/Excel)
3. Report downloads with all expenses

---

## Pending Approvals (Tier 2)

### Purpose
Director-level approval for higher-value expenses.
**Tier 2 handles:** Expenses > ₹50,000

### View Tier 2 Approvals
1. Click **"Pending Approvals"** in Staff menu
2. See list of expenses awaiting director approval
3. These are expenses already approved by Tier 1

### Two-Tier Approval Workflow
```
Employee Submits Expense
  ↓
Tier 1 Manager Reviews (≤₹50K approved here)
  ↓
If > ₹50K → Tier 2 Director Review
  ↓
Director Approves/Rejects
  ↓
Posted to Transactions (if approved)
```

### Director Approval Process
1. Click expense in list
2. Review:
   - Original amount
   - Category
   - Manager's comments
   - Attachments
3. Click **"✓ Approve"** or **"✗ Reject"**
4. Add approval notes
5. Confirm decision

### Rejection at Tier 2
- If rejected by director, expense goes back to submitter
- Employee notified with director's reason
- Can be resubmitted if issue resolved

### View Approval History
1. Click expense
2. Scroll to **"Approval History"** section
3. See all approval steps and timestamps

---

## Payroll Management

### Access Payroll
1. Click **"Payroll"** in Staff menu
2. See payroll cycles list

### Payroll Cycle Overview
Shows:
- **Month/Year** - Payroll period
- **Status** - Draft/Approved/Paid
- **Total Amount** - Sum of all salaries
- **Employees** - Number of staff
- **Created Date** - When created

### Create New Payroll Cycle
1. Click **"+ New Payroll Cycle"**
2. Select **Month** and **Year**
3. Click **"Create Cycle"**
4. System generates records for all staff
5. Status = "Draft"

### Payroll Calculation
System automatically calculates:
- **Gross Salary** - Base + allowances
- **Deductions:**
  - PF (Provident Fund)
  - ESI (Employee State Insurance)
  - Professional Tax
  - Income Tax
  - Loan EMI (if applicable)
  - Other deductions
- **Net Salary** - Gross - Deductions

### View Payroll Details
1. Click payroll cycle
2. See table of all staff with:
   - Name
   - Gross Salary
   - Each deduction
   - Net Salary
   - Working days
   - Attendance record

### Edit Individual Payroll
1. Click staff member in payroll list
2. Modify:
   - **Working Days** (based on attendance)
   - **Allowances** (if any extra)
   - **Deductions** (if adjustments needed)
3. System recalculates net salary
4. Click **"Save"**

### Approve Payroll
1. Review all records
2. Click **"Submit for Approval"**
3. Status changes to "Pending Approval"
4. Manager/Director approves
5. Status changes to "Approved"

### Process Payment
1. After approval, click **"Process Payment"**
2. Review bank transfer details
3. System generates bank file
4. Click **"Download Bank File"** to send to bank
5. Status changes to "Paid"

### Generate Salary Slips
1. From payroll cycle, click **"Generate Slips"**
2. System creates PDF for each employee
3. Click **"Download All"** or download individually
4. Distribute to employees

### Export Payroll Report
1. Click **"Export"** button
2. Select format (PDF/Excel)
3. Detailed payroll report downloads

---

## Vehicles Management

### Access Vehicles
1. Click **"Vehicles"** in Staff menu
2. See list of all project vehicles

### Vehicle Information
| Column | Shows |
|--------|-------|
| **Vehicle Type** | Truck, Car, Crane, etc. |
| **Registration Number** | Vehicle plate number |
| **Assigned Project** | Which project using it |
| **Driver** | Assigned driver |
| **Fuel Status** | Current fuel level |
| **Mileage** | Current odometer reading |
| **Last Service** | Last maintenance date |
| **Status** | Available/In Use/Maintenance |

### Add New Vehicle
1. Click **"+ Add Vehicle"**
2. Fill details:
   - **Vehicle Type** (select from dropdown)
   - **Registration Number**
   - **Make/Model**
   - **Year** of manufacture
   - **Assigned Project**
   - **Driver** (select from staff)
   - **Capacity** (if applicable)
3. Click **"Add Vehicle"**

### Record Fuel Entry
1. Click vehicle
2. Click **"+ Add Fuel Entry"**
3. Fill in:
   - **Date**
   - **Fuel Quantity** (liters)
   - **Cost**
   - **Odometer Reading**
   - **Driver Name**
4. Click **"Save"**
5. Fuel history updated

### Record Maintenance
1. Click vehicle
2. Click **"+ Maintenance Log"**
3. Fill in:
   - **Date of Service**
   - **Type of Work** (Oil change, Repairs, etc.)
   - **Parts Replaced**
   - **Cost**
   - **Service Provider**
   - **Notes**
4. Click **"Save"**
5. Maintenance history updated

### View Vehicle Details
1. Click vehicle name
2. See complete information:
   - Registration details
   - Current status
   - Fuel consumption history
   - Maintenance schedule
   - Service records
   - Accident history (if any)
   - Assignment history

### Edit Vehicle
1. Click **"Edit"** button
2. Modify fields
3. Click **"Save Changes"**

### Assign Vehicle to Project
1. Click vehicle
2. Click **"Assign to Project"**
3. Select project
4. Set assignment dates
5. Click **"Assign"**

### Generate Vehicle Report
1. Click **"Reports"** button
2. Select report type:
   - Fleet Summary
   - Fuel Consumption
   - Maintenance Schedule
   - Cost Analysis
3. Select date range
4. View or download report

---

# ATTENDANCE SYSTEM

## Punch In/Out

### Access Attendance
1. Click **"Attendance"** in left menu
2. You see the Punch In/Out interface

### Punch In (Start Work)
1. Click **"Punch In"** button
2. **Current Time** shows
3. Location captured (if device has GPS)
4. **Photo Capture:**
   - Camera activates
   - Take photo of yourself
   - Click **"Capture Photo"**
   - Confirm photo looks good
5. Click **"Confirm Punch In"**
6. Success message shows
7. You're now "Clocked In"

### During Work
- **Status Shows:** "Currently Clocked In"
- **Elapsed Time** counter displays
- **Punch Out** button available

### Punch Out (End Work)
1. Click **"Punch Out"** button
2. **Current Time** shows
3. Location captured
4. **Photo Capture:**
   - Camera activates
   - Take photo of yourself
   - Click **"Capture Photo"**
   - Confirm photo looks good
5. Click **"Confirm Punch Out"**
6. Success message shows
7. Attendance recorded

### Attendance Summary
Shows today's attendance:
- **Punch In Time** - When you arrived
- **Punch Out Time** - When you left
- **Total Hours** - Time worked
- **Photo** - Proof of presence
- **Location** - Where you were

### Can't Punch In?
- Check internet connection
- Check camera permissions
- Ensure browser allows camera access
- Try refreshing page
- Contact admin if issue persists

---

## Attendance Reports

### Access Reports
1. Click **"Attendance"** in menu
2. Click **"Reports"** tab
3. Select report type

### Personal Attendance Report
**View your own attendance:**
1. Click **"My Attendance"**
2. Select date range
3. See calendar with all punch records
4. Hover over date to see times

**Information shown:**
- ✓ Present (Green)
- ✗ Absent (Red)
- ? Leave (Yellow)
- → Half Day (Blue)

### Department Attendance
**View team attendance (if manager):**
1. Click **"Department Report"**
2. Select department
3. Select date range
4. See attendance grid:
   - Rows = staff members
   - Columns = dates
   - Color coded status

### Generate Attendance Report
1. Click **"Generate Report"**
2. Select filters:
   - **Department**
   - **Staff Member** (or all)
   - **Date Range**
3. Select report format:
   - **Summary** - Present/Absent/Leave counts
   - **Detailed** - Time records
   - **With Photos** - Includes punch photos
4. Click **"Generate"**
5. Review and click **"Download"**

### Attendance Statistics
Shows:
- **Total Days** - Working days in period
- **Present Days** - Days attended
- **Absent Days** - Days absent
- **Leave Days** - Days on approved leave
- **Attendance %** - Percentage of days attended

### Export Report
1. From report, click **"Export"**
2. Select format:
   - Excel (for spreadsheet)
   - PDF (for printing/sharing)
3. File downloads to computer

---

## Photo Approval Workflow

### Purpose
Photos from punch in/out are reviewed for approval.

### For Staff Member
When you punch in/out, photo is submitted for approval.

### For HR/Admin (Photo Reviewer)

**Access Photo Approvals:**
1. Click **"Attendance"** menu
2. Click **"Photo Approvals"** tab
3. See list of pending photos

**Review Photo:**
1. Click photo in list
2. See:
   - Staff member name
   - Photo taken
   - Punch time
   - Location
3. Verify photo looks legitimate

**Approve Photo:**
1. Review photo carefully
2. Click **"✓ Approve"**
3. Add notes (optional)
4. Click **"Confirm"**
5. Photo marked as approved
6. Attendance finalized

**Reject Photo:**
1. If photo unclear/suspicious
2. Click **"✗ Reject"**
3. **Required:** Add rejection reason
4. Click **"Confirm"**
5. Staff member notified
6. Can resubmit with new photo

**Bulk Approve:**
1. Check boxes of multiple photos
2. Click **"Approve All"**
3. All selected photos approved at once

### Real-Time Updates
- Pending photos appear automatically
- System checks for photos every 30 seconds
- New photos appear without page refresh

---

## Leaves & Absences

### Request Leave
1. From attendance page, click **"Request Leave"**
2. Fill in:
   - **Leave Type** (Sick, Casual, Earned, Unpaid, etc.)
   - **Start Date**
   - **End Date**
   - **Reason** (optional)
3. Click **"Submit Request"**
4. Status = "Pending Approval"

### View Leave Balance
- Shows available days for each leave type
- Updates in real-time

### View Leave History
1. Click **"Leave History"**
2. See all past and pending leave requests
3. Shows dates, type, reason, status

### Leave Approval (for Managers)
1. Click **"Pending Leaves"** in Attendance
2. See list of leave requests from team
3. Click request to see details
4. Click **"✓ Approve"** or **"✗ Reject"**
5. Add notes if rejecting
6. Employee notified

### Report Absence (Emergency)
1. Click **"Report Absence"**
2. Select date
3. Reason for absence
4. Click **"Submit"**
5. Auto-marked as absent unless leave approved

---

## Materials Inventory (Store)

### Access Store
1. Click **"Store"** in left menu
2. See inventory management page

### Store Dashboard
Shows:
- **Total Items** - Number of different materials
- **Stock Value** - Total inventory worth
- **Low/Critical Items** - Items below minimum stock
- **Warnings** - Stock alerts

### View Inventory
1. See complete inventory table
2. Columns show:
   - **Item Name**
   - **Category**
   - **Current Quantity**
   - **Min/Max Stock Levels**
   - **Unit Price**
   - **Total Value** (Qty × Price)
   - **Supplier**
   - **Status** (In Stock/Low Stock/Critical)

### Understand Stock Status
- **In Stock** (Green) - Above minimum level
- **Low Stock** (Orange) - Between min and 1.5× min
- **Critical** (Red) - At or below minimum
  - **Action Required:** Order immediately

### Add New Item
1. Click **"+ New Item"** button
2. Fill in details:
   - **Item Name** (required)
   - **Category** (Materials/Tools/Finishing/Safety/Other)
   - **Current Quantity**
   - **Unit** (Unit/Bags/Tons/Boxes/Meters/Cubic Meters)
   - **Min Stock Level** (alert when below this)
   - **Max Stock Level** (maximum to keep)
   - **Unit Price**
   - **Supplier Name**
3. Click **"Add Item"**
4. Item added to inventory

### Edit Item
1. Click item in table
2. Click **"Edit"** button
3. Modify fields:
   - Quantity
   - Price
   - Min/Max levels
   - Supplier
4. Click **"Save Changes"**

### Delete Item
1. Click **"Delete"** (trash icon) next to item
2. Confirm deletion
3. Item removed from inventory

### Monitor Stock Levels
1. **Critical Items** highlighted in red
2. Click critical item
3. Click **"Order Now"** button
4. Automatically creates purchase request
5. Sent to procurement team

### Search Inventory
1. Use **"Search"** box
2. Type item name or category
3. Results filter instantly

### Filter & Sort
- **Filter by Category**
- **Filter by Status** (In Stock/Low/Critical)
- **Sort by:** Name, Quantity, Price, Value
- Results update immediately

### Export Inventory Report
1. Click **"Export"** button
2. Select format (PDF/Excel)
3. Report downloads with all items and values

### Stock Count/Adjustment
1. Click **"Physical Count"**
2. For each item:
   - Physically count in warehouse
   - Enter counted quantity
   - Note any discrepancy
3. Click **"Finalize Count"**
4. System adjusts records
5. Generates discrepancy report

---

# FINANCE MANAGEMENT

## Finance Dashboard

### Access Finance
1. Click **"Finance"** in left menu
2. See finance summary dashboard

### Dashboard Overview
Shows key financial metrics:
- **Total Income** - Revenue received
- **Total Expenses** - Amount spent
- **Balance** - Income minus Expenses
- **Cash Flow** - Visual chart of money flow

### Monthly Cash Flow Chart
- **X-axis** - Months
- **Y-axis** - Amount
- **Green bars** - Income by month
- **Red bars** - Expenses by month
- **Shows trend** over time

### Dashboard Actions
- **"+ Add Transaction"** - Record new transaction
- **"View All Transactions"** - See complete list
- Click chart to see detailed breakdown

---

## Transactions

### View All Transactions
1. From Finance, click **"View All Transactions"**
2. See table with all transactions

### Transaction Details
| Column | Shows |
|--------|-------|
| **Date** | When transaction occurred |
| **Description** | What it was for |
| **Type** | Income or Expense |
| **Category** | Finance category |
| **Amount** | Money amount |
| **Status** | Approved/Pending/Rejected |
| **Project** | Which project (if applicable) |

### Add New Transaction
1. Click **"+ Add Transaction"**
2. Fill in:
   - **Date** (when it occurred)
   - **Description** (what for)
   - **Type** (Income/Expense)
   - **Category** (select from list)
   - **Amount** (money value)
   - **Project** (if project-specific)
   - **Payment Method** (Cash/Bank Transfer/Check)
   - **Reference Number** (invoice #, receipt #, etc.)
   - **Attachments** (receipt, invoice, etc.)
3. Click **"Save Transaction"**
4. Transaction added to ledger

### Categorize Transactions
**Common categories:**
- **Income:** Sales, Interest, Grants
- **Expenses:**
  - Labor (wages, salaries)
  - Materials (building supplies)
  - Equipment (tools, machinery)
  - Transport (fuel, logistics)
  - Utilities (power, water)
  - Miscellaneous (other)

### Edit Transaction
1. Click transaction
2. Click **"Edit"**
3. Modify fields
4. Click **"Save Changes"**

### Delete Transaction
1. Click **"Delete"** button
2. Confirm deletion
3. Removed from ledger

### View Transaction Details
1. Click transaction row
2. See complete information:
   - Full description
   - Amount breakdown
   - Project association
   - Attached documents
   - Approval status
   - Who recorded it
   - Timestamp

---

## Invoices

### Create Invoice
1. Click **"Invoices"** in Finance menu
2. Click **"+ Create Invoice"**
3. Fill in invoice details:

**Invoice Header:**
- **Invoice Number** (auto-generated)
- **Client/Vendor Name**
- **Invoice Date**
- **Due Date**

**Invoice Items:**
1. Click **"+ Add Item"**
2. For each line item:
   - **Description** (what delivered)
   - **Quantity**
   - **Unit Price**
   - **Amount** (auto-calculates)
3. Repeat for each item

**Totals:**
- **Subtotal** (auto-calculated)
- **Tax %** (if applicable)
- **Tax Amount** (auto-calculated)
- **Final Amount** (Subtotal + Tax)

**Notes:**
- **Payment Terms** (Net 30, Net 60, etc.)
- **Notes to Client**

4. Click **"Create Invoice"**
5. Invoice saved and can be sent

### View Invoices
1. From Finance, click **"Invoices"**
2. See all invoices in list
3. Shows:
   - Invoice number
   - Client
   - Date
   - Amount
   - Status (Draft/Sent/Paid)

### Invoice Status
- **Draft** - Not yet sent
- **Sent** - Sent to client
- **Partial** - Partial payment received
- **Paid** - Fully paid
- **Overdue** - Payment past due date

### Send Invoice to Client
1. Click invoice
2. Click **"Send Invoice"**
3. Select delivery method:
   - **Email** - Send to client email
   - **Download** - Print and deliver
4. Click **"Send"**
5. Status changes to "Sent"

### Record Payment
1. Click invoice
2. Click **"Record Payment"**
3. Enter:
   - **Payment Date**
   - **Amount Paid**
   - **Payment Method** (Cash/Bank/Check)
   - **Reference** (Check #, Bank transaction)
4. Click **"Save Payment"**
5. Updates invoice status

### Track Due Dates
- **Overdue invoices** highlighted in red
- Click to see days overdue
- Follow up with client for payment

### Edit Invoice
1. Click invoice
2. Click **"Edit"** (only if not yet sent)
3. Modify items or amounts
4. Click **"Save"**

### Generate Invoice Report
1. Click **"Reports"**
2. Select:
   - Date range
   - Client (or all)
3. Click **"Generate"**
4. See summary of all invoices
5. Export to PDF/Excel

---

## Budget Management

### Create Budget
1. Click **"Budget"** in Finance menu
2. Click **"+ New Budget"**
3. Fill in:
   - **Project** (select project)
   - **Budget Amount** (total budget)
   - **Start Date**
   - **End Date**
4. Click **"Create Budget"**

### Budget Breakdown by Category
1. In budget details, click **"+ Add Category"**
2. For each category:
   - **Category Name** (Labor, Materials, etc.)
   - **Allocated Amount** - Money set aside
3. Repeat for all categories
4. Click **"Save Allocation"**

### Monitor Budget Usage
**Shows:**
- **Category** - Type of expense
- **Allocated** - Budget for this category
- **Spent** - Amount spent so far
- **Remaining** - Budget left
- **% Used** - Percentage of budget used
- **Status** - On Track/Warning/Over Budget

### Budget Alerts
- **Green** - Under 75% of budget
- **Yellow** - 75-100% of budget (warning!)
- **Red** - Over 100% (exceeded!)

### View Budget vs Actual
1. Click budget
2. Click **"Budget vs Actual"** tab
3. See chart comparing:
   - Allocated budget (blue bars)
   - Actual spending (red bars)
4. Identify over-spending immediately

### Adjust Budget
1. Click budget
2. Click **"Edit Budget"**
3. Modify:
   - Total budget amount
   - Category allocations
4. Click **"Save Changes"**
5. Changes logged for audit

### Budget Variance Report
1. Click **"Reports"**
2. Select budget date range
3. View variance analysis:
   - How much over/under budget
   - Which categories overspent
   - Spending trends

### Approve Budget Changes
If budget exceeded:
1. System alerts manager
2. Additional approval needed
3. Manager reviews variance
4. Approves or requests correction

---

## Chart of Accounts

### View Chart of Accounts
1. Click **"Chart of Accounts"** in Finance menu
2. See hierarchical account structure

### Account Hierarchy
- **Level 1:** Account Types
  - Assets (Cash, Inventory, Equipment)
  - Liabilities (Loans, Payables)
  - Equity (Owner's investment)
  - Revenue (Sales, Income)
  - Expenses (Labor, Materials, etc.)

- **Level 2:** Accounts
  - Each type has sub-accounts
  - Click to expand/collapse

### Account Information
Shows for each account:
- **Account Code** (e.g., 1001)
- **Account Name**
- **Account Type**
- **Current Balance**
- **No. of Transactions**

### Search Accounts
1. Use **"Search"** box
2. Type code or name
3. Find account instantly

### View Account Details
1. Click account name
2. See:
   - Account information
   - Current balance
   - All transactions for this account
   - Month-by-month breakdown
   - Running balance

### Create Custom Account
1. Click **"+ Add Account"**
2. Fill in:
   - **Account Code** (must be unique)
   - **Account Name**
   - **Account Type**
   - **Category**
3. Click **"Create"**
4. New account added to CoA

---

## Financial Reports

### Access Reports
1. Click **"Finance"** menu
2. Click **"Reports"**
3. See list of available reports

### Available Reports

#### 1. Profit & Loss (P&L) Statement
**Shows:**
- Revenue (all income)
- Cost of Goods Sold (COGS)
- Gross Profit
- Operating Expenses
- Net Profit
- Profit Margin %

**Use:** See profitability

#### 2. Cash Flow Report
**Shows:**
- Operating cash inflows
- Operating cash outflows
- Net cash from operations
- Cash trends
- Beginning and ending cash

**Use:** Understand cash position

#### 3. Balance Sheet
**Shows:**
- Assets (what you own)
- Liabilities (what you owe)
- Equity (owner's stake)
- Assets = Liabilities + Equity

**Use:** Overall financial position

#### 4. Receivables Aging
**Shows:**
- Invoices not yet paid
- Grouped by age:
  - Current (0-30 days due)
  - 30-60 days overdue
  - 60-90 days overdue
  - 90+ days overdue
- Amount in each category

**Use:** Track unpaid invoices

#### 5. Payables Aging
**Shows:**
- Bills you haven't paid
- Grouped by age
- Vendors waiting for payment

**Use:** Plan cash for payments

#### 6. Project Profitability
**Shows:**
- Revenue for each project
- Total costs for each project
- Gross profit per project
- Profit margin %

**Use:** See which projects most profitable

#### 7. Cost vs Budget
**Shows:**
- Budget allocated
- Actual spending
- Variance (over/under)
- By category and project

**Use:** Monitor budget adherence

### Generate Report
1. Click report type
2. Select filters:
   - **Date Range** (start and end date)
   - **Project** (if project-specific)
   - **Department** (if applicable)
3. Click **"Generate"**
4. Report displays with:
   - Summary statistics
   - Detailed breakdown
   - Charts and graphs

### View Report Details
- **Drill down:** Click any line to see details
- **Sort:** Click column headers to sort
- **Filter:** Use column filters

### Export Report
1. From report, click **"Export"**
2. Select format:
   - **PDF** - For printing/sharing
   - **Excel** - For further analysis
3. File downloads to computer

### Schedule Reports
1. Click **"Schedule Report"**
2. Select report type
3. Select frequency:
   - Daily
   - Weekly
   - Monthly
4. Choose delivery method:
   - Email
   - Download folder
5. Click **"Schedule"**
6. Report auto-generates and sends

---

## Retention Tracking

### Purpose
Construction contracts often retain a percentage (5-10%) of invoice payment until project completion.

### Record Retention
When creating invoice:
1. Set **"Retention Percentage"** (e.g., 5%)
2. System calculates:
   - Invoice amount: ₹100,000
   - Retention (5%): ₹5,000
   - Payment due: ₹95,000
3. Retention held until release date

### Track Pending Retentions
1. Click **"Retention Tracking"** in Finance menu
2. See table of all pending retentions:
   - **Invoice** - Which invoice retained
   - **Amount Retained** - ₹ amount
   - **Release Date** - When to release
   - **Days Until Release** - Countdown
   - **Status** - Pending/Released

### Release Retention
When project completed and release date reached:
1. Click retention entry
2. Click **"Release Retention"**
3. Confirm amount to release
4. Click **"Process Release"**
5. Amount added to payment
6. Retention marked as released

### Retention Liability
- Retention shown as "Payable" on balance sheet
- Reduces cash available
- Monitored carefully to ensure payment

### Retention Schedule Report
1. Click **"Reports"**
2. See schedule of when retentions release
3. Plan cash accordingly
4. Export for accounting records

---

# PROCUREMENT PIPELINE

## Indents (Material Requests)

### Create Indent
1. Click **"Procurement"** in left menu
2. Click **"Indents"**
3. Click **"+ Create Indent"**

**Fill in Indent Details:**
- **Project** (select project needing materials)
- **For Department** (which department needs it)
- **Required Date** (when needed by)
- **Add Items:**
  - Click **"+ Add Item"**
  - **Material Name**
  - **Description**
  - **Quantity Required**
  - **Unit** (Tons/Boxes/Bags/etc.)
  - **Estimated Unit Price**
  - **Justification** (why needed)
  - Repeat for each item
- **Notes** (any special instructions)

4. Click **"Submit Indent"**
5. Indent created with status "Submitted"

### View Indents
1. From Procurement, click **"Indents"**
2. See list of all indents
3. Shows:
   - **Indent ID** - Reference number
   - **Project** - Which project
   - **Requested By** - Who created
   - **Date** - When created
   - **Status** - Submitted/Approved/Rejected/PO Created

### Filter Indents
- By **Status** (Submitted/Approved/Rejected)
- By **Project**
- By **Date Range**
- By **Requestor**

### Approve Indent (Procurement Manager)
1. Click indent
2. Review details:
   - Materials needed
   - Quantities
   - Estimated costs
   - Justification
3. Click **"✓ Approve Indent"**
4. Add approval notes (optional)
5. Status changes to "Approved"
6. Ready for PO creation

### Reject Indent
1. Click indent
2. Click **"✗ Reject"**
3. **Required:** Add rejection reason
4. Click **"Confirm"**
5. Requestor notified to revise

### Create Purchase Order from Indent
1. After indent approved, click **"Create PO"**
2. System pre-fills from indent
3. Add vendor/supplier details:
   - **Supplier Name**
   - **Address**
   - **Contact**
   - **Payment Terms**
4. Verify items and quantities
5. Click **"Create PO"**
6. PO created, status "Draft"

---

## Purchase Orders (POs)

### View All POs
1. From Procurement, click **"Purchase Orders"** (or **"Purchases"**)
2. See table of all POs
3. Shows:
   - **PO Number** - Reference
   - **Supplier** - Vendor name
   - **Project** - What for
   - **Date** - When created
   - **Amount** - Total PO value
   - **Status** - Draft/Sent/Confirmed/Received/Invoiced

### PO Status Workflow
```
Draft → Sent to Supplier → Confirmed by Supplier →
Goods Received → Invoice Received → Payment Made
```

### Create Purchase Order (Direct)
1. Click **"+ New PO"**
2. Fill in:

**PO Header:**
- **PO Number** (auto or manual)
- **Date**
- **Supplier** (select from vendors)
- **Project** (what it's for)
- **Delivery Address**
- **Delivery Date**

**PO Items:**
1. Click **"+ Add Item"**
2. For each item:
   - **Item Description**
   - **HSN/SAC Code** (if applicable)
   - **Quantity**
   - **Unit**
   - **Unit Price**
   - **Amount** (auto-calculates)
   - **Tax %** (if applicable)
3. System calculates totals:
   - Subtotal
   - Tax
   - Total Amount

**Terms:**
- **Payment Terms** (Net 30, Advance, etc.)
- **Delivery Terms**
- **Special Instructions**

3. Click **"Save PO as Draft"**

### Finalize PO
1. Review details
2. Click **"Finalize"**
3. Status changes to "Ready to Send"

### Send PO to Supplier
1. Click PO
2. Click **"Send to Supplier"**
3. Choose delivery method:
   - **Email** - Automatic email with PO
   - **Print** - Print to deliver manually
4. Click **"Confirm Send"**
5. Status changes to "Sent"

### Track PO Status
1. Click PO in list
2. Status shows:
   - ✓ Sent
   - ✓ Acknowledged by supplier
   - ✓ Confirmed (ready to deliver)
   - → In Transit
   - ✓ Received
   - ✓ Invoiced
   - ✓ Paid

### PO Actions
- **Edit** - Modify before sending (Draft only)
- **Cancel** - Cancel order (with reason)
- **Print** - Print for records
- **Email** - Resend to supplier

### Partial Receipts
If goods arrive in multiple shipments:
1. Click PO
2. Click **"Record Receipt"**
3. For each shipment:
   - Enter items received
   - Quantities
   - Condition
   - Receipt date
4. System tracks what's received
5. Shows pending items

---

## Goods Receipt Notes (GRN)

### What is GRN?
GRN records when goods physically arrive from supplier.

### Create GRN
1. From Procurement, click **"GRN"** (or **"Goods Receipts"**)
2. Click **"+ Create GRN"**
3. Fill in:

**GRN Header:**
- **GRN Number** (auto-generated)
- **GRN Date** (today's date)
- **Linked PO** (select PO being received)
- **Supplier Name** (auto-filled from PO)
- **Receipt Location** (site warehouse)
- **Receiving Person** (who's receiving)

**Goods Received:**
1. System shows items from PO
2. For each item:
   - **Quantity Ordered** (from PO)
   - **Quantity Received** (physically received)
   - **Unit** (Tons, Boxes, etc.)
   - **Condition** (Good/Damaged/Partial)
   - **Notes** (any issues)
3. Click **"Add Receipt"**

**Quality Check:**
- **Inspection Status** (Pass/Fail/Hold)
- **Inspector Name**
- **Issues Found** (if any)
- **Approval** (Quality checked and OK?)

4. Click **"Create GRN"**
5. GRN recorded and status "Created"

### View GRNs
1. From Procurement, click **"GRN"**
2. See list of all goods receipts
3. Shows:
   - GRN number
   - PO reference
   - Supplier
   - Received date
   - Items received
   - Quantity variance (if any)
   - Status

### GRN Status
- **Received** - Goods physically received
- **Inspected** - Quality check completed
- **Accepted** - Quality OK, ready for use/storage
- **Rejected** - Quality issue, return required
- **Partial** - Some items missing

### Goods Discrepancy
If quantity received ≠ quantity ordered:

**Example:**
- PO ordered: 100 bags of cement
- GRN received: 98 bags
- Discrepancy: 2 bags short

**Action:**
1. GRN flags discrepancy automatically
2. Create return/credit note
3. Contact supplier
4. Follow up for shortage

### Match Invoice to GRN
When invoice received:
1. Click GRN
2. Click **"Link Invoice"**
3. Select supplier invoice
4. System verifies:
   - Quantity matches
   - Unit price matches
   - Total matches
4. If OK, status "Invoice Matched"
5. Ready for payment

### Aging Analysis
- **GRN not yet invoiced** - Goods received but bill not yet
- **GRN invoiced not yet paid** - Bill received but not paid
- Use to track payables

---

## Suppliers Management

### View All Suppliers
1. Click **"Procurement"** menu
2. Click **"Suppliers"**
3. See list of all vendors

### Supplier Information
| Column | Shows |
|--------|-------|
| **Name** | Company name |
| **Contact Person** | Primary contact |
| **Phone** | Contact number |
| **Email** | Email address |
| **Category** | Type (Materials, Equipment, etc.) |
| **Location** | City/Region |
| **Rating** | Star rating (1-5) |
| **Status** | Active/Inactive |

### Add New Supplier
1. Click **"+ Add Supplier"**
2. Fill in details:

**Company Details:**
- **Company Name** (required)
- **Contact Person** (primary contact)
- **Designation**
- **Phone Number** (required)
- **Email** (required)
- **Website**

**Address:**
- **Street Address**
- **City**
- **State**
- **PIN Code**
- **Country**

**Business Details:**
- **Category** (Materials/Equipment/Services)
- **Specialization** (what they supply)
- **GST Number** (if in India)
- **PAN/Tax ID**
- **Bank Details** (for payments)

**Payment Terms:**
- **Standard Payment Terms** (Net 30, Net 60, etc.)
- **Credit Limit** (max we'll owe them)
- **Discount %** (if negotiated)

**Performance:**
- **Lead Time** (days to deliver)
- **Quality Rating** (assessment)
- **Delivery Rating** (on-time delivery %)
- **Notes**

3. Click **"Add Supplier"**

### Edit Supplier
1. Click supplier name
2. Click **"Edit"**
3. Modify information
4. Click **"Save Changes"**

### Supplier Performance
1. Click supplier
2. Click **"Performance"** tab
3. See metrics:
   - **On-Time Delivery %** - How often on time
   - **Quality Score** - Product quality rating
   - **No. of Orders** - Total orders placed
   - **Total Spent** - Amount we've paid
   - **Average Order Value** - Typical order size
   - **Payment Record** - Do they invoice correctly?

### Supplier Rating
1. After receiving goods from supplier
2. Click supplier
3. Click **"Rate Supplier"**
4. Rate on:
   - **Delivery** (1-5 stars)
   - **Quality** (1-5 stars)
   - **Communication** (1-5 stars)
   - **Value for Money** (1-5 stars)
   - **Comments** (optional)
5. Click **"Submit Rating"**

### Supplier History
1. Click supplier
2. Click **"History"** tab
3. See:
   - All POs placed with them
   - All GRNs from them
   - All invoices received
   - Payment records
   - Performance over time

### Deactivate Supplier
1. Click supplier
2. Click **"Deactivate"**
3. Confirm action
4. Supplier marked inactive
5. Can't select for new POs
6. Can reactivate if needed

---

## Procurement Pipeline Dashboard

### Access Pipeline Dashboard
1. Click **"Procurement"** menu
2. Click **"Pipeline Dashboard"** (or **"Procurement Overview"**)
3. See visual pipeline of all procurements

### Pipeline View
Shows stages of procurement:

```
Stage 1: INDENTS
├─ Submitted: 5 items
├─ Approved: 8 items
└─ Rejected: 1 item

Stage 2: PURCHASE ORDERS
├─ Draft: 3 POs
├─ Sent: 5 POs
└─ Confirmed: 8 POs

Stage 3: GOODS RECEIPT
├─ In Transit: 6 GRNs
├─ Received: 10 GRNs
└─ Inspected: 9 GRNs

Stage 4: INVOICING
├─ Pending Invoice: 3 GRNs
├─ Invoice Received: 8 GRNs
└─ Matched: 7 GRNs

Stage 5: PAYMENT
├─ Ready to Pay: 6 invoices
├─ Paid: 12 invoices
└─ Overdue: 1 invoice
```

### Pipeline Statistics
Shows:
- **Total Items in Pipeline** - All items count
- **Average Lead Time** - Days from indent to receipt
- **Pending Approvals** - Items awaiting approval
- **Outstanding Receipts** - Goods not yet received
- **Pending Payments** - Invoices not yet paid

### Bottleneck Identification
- **Red alerts** for delayed items
- Shows which items stuck at which stage
- Helps identify delays

### Filter Pipeline
1. By **Status** (any stage)
2. By **Project**
3. By **Supplier**
4. By **Date Range**
5. Results update immediately

### Pipeline Reports
1. Click **"Generate Report"**
2. Select report type:
   - Pipeline Summary
   - Pending Approvals
   - Lead Time Analysis
   - Supplier Performance
3. Select date range
4. View or download report

---

## Estimates & Quotes

### Create Estimate/Quote
1. Click **"Procurement"** menu
2. Click **"Estimates"** or **"Quotes"**
3. Click **"+ Create Estimate"**

**Fill in:**
- **Client Name** (who receiving quote)
- **Project** (related project)
- **Quote Date**
- **Valid Until** (expiry date)

**Quote Items:**
1. Click **"+ Add Item"**
2. For each item:
   - **Description** (what we're quoting)
   - **Quantity**
   - **Unit**
   - **Unit Price**
   - **Amount** (auto-calculates)
   - **Tax** (if applicable)
3. System calculates:
   - Subtotal
   - Total Tax
   - Grand Total

**Discount (if applicable):**
- **Discount %** or **Amount**
- Final total recalculates

3. Click **"Create Quote"**
4. Status = "Draft"

### Send Quote to Client
1. Click quote
2. Click **"Send Quote"**
3. Choose method:
   - **Email** - Send via email
   - **Download** - Get PDF to send
4. Click **"Send"**
5. Status changes to "Sent"

### Track Quote Status
- **Draft** - Not yet sent
- **Sent** - Sent to client
- **Accepted** - Client approved
- **Rejected** - Client declined
- **Quoted** - Done (no further action)

### Convert Quote to PO
1. When client accepts quote
2. Click quote
3. Click **"Convert to PO"**
4. System creates PO from quote details
5. PO status = "Draft"
6. Ready to send to supplier

### Edit Quote
1. Click quote
2. Click **"Edit"** (while Draft/Sent)
3. Modify items/prices
4. Click **"Save"**

---

## Quote Templates

### Purpose
Pre-built templates for common quotes (speeds up process)

### View Templates
1. From Procurement, click **"Quote Templates"**
2. See list of existing templates

### Create Template
1. Click **"+ Create Template"**
2. Fill in:
   - **Template Name** (e.g., "Cement Supply")
   - **Description**
   - **Add Items:**
     - Item description
     - Standard quantity
     - Standard unit price
     - Repeat for each item
3. Click **"Save Template"**

### Use Template
1. When creating new quote
2. Click **"Use Template"**
3. Select template
4. System pre-fills items
5. Modify quantities/prices if needed
6. Continue with quote

### Edit Template
1. Click template
2. Click **"Edit"**
3. Modify items/details
4. Click **"Save"**

---

# ADMINISTRATION & SETTINGS

## Users Management

### View All Users
1. Click **"Admin"** in left menu
2. Click **"Users"**
3. See list of all system users

### User Information
| Column | Shows |
|--------|-------|
| **Name** | Full name |
| **Email** | Email address |
| **Role** | Position/Role |
| **Department** | Which department |
| **Status** | Active/Inactive |
| **Last Login** | Last access time |

### Add New User
1. Click **"+ Add User"**
2. Fill in:
   - **Full Name** (required)
   - **Email** (required, unique)
   - **Phone** (required)
   - **Department** (select)
   - **Role/Position** (select)
   - **Password** (auto-generated or set)
   - **Temporary Password** checkbox (user sets on first login)
3. Click **"Create User"**
4. Welcome email sent

### Edit User
1. Click user name
2. Click **"Edit"**
3. Modify:
   - Name
   - Email
   - Department
   - Role
   - Status
4. Click **"Save Changes"**

### Reset Password
1. Click user
2. Click **"Reset Password"**
3. System generates temporary password
4. User notified via email
5. User sets new password on first login

### Deactivate User
1. Click user
2. Click **"Deactivate"**
3. Confirm action
4. User can't login
5. Can be reactivated later

### Delete User
1. Click **"Delete"** button
2. Confirm deletion
3. User removed from system
4. Historical records retained

### User Permissions
1. Click user
2. Click **"Permissions"** tab
3. See all permissions granted
4. Check/uncheck to add/remove
5. Click **"Save"**

---

## Roles & Permissions

### Role-Based Access Control (RBAC)
The system uses roles to control what users can do.

### Standard Roles
| Role | Can Do |
|------|--------|
| **Admin** | Everything - full system access |
| **Manager** | Projects, Staff, Approvals |
| **Finance** | Finance, Reports, Budgets |
| **Procurement** | Purchase Orders, Suppliers |
| **HR** | Staff, Payroll, Attendance |
| **User** | Basic features, Own profile |

### View Roles
1. Click **"Admin"** menu
2. Click **"Roles"**
3. See all defined roles

### Create Custom Role
1. Click **"+ Create Role"**
2. Fill in:
   - **Role Name** (e.g., "Site Manager")
   - **Description**
3. Click **"Add Permissions"**
4. Check permissions:
   - Projects (View/Create/Edit/Delete)
   - Staff (View/Create/Edit)
   - Finance (View/Create)
   - Etc.
5. Click **"Create Role"**
6. Role available for assignment

### Assign Permissions to Role
1. Click role name
2. Click **"Edit Permissions"**
3. Check/uncheck permissions:
   - **View** - Can see data
   - **Create** - Can add new records
   - **Edit** - Can modify existing
   - **Delete** - Can remove records
   - **Approve** - Can approve/reject
4. Click **"Save Permissions"**

### Edit Role
1. Click role
2. Click **"Edit"**
3. Modify permissions
4. Click **"Save"**

### Assign Role to User
1. Click user
2. Select **Role** from dropdown
3. Click **"Save"**
4. User gets all role permissions

### View Permission Details
For each role, shows:
- **Modules accessible**
- **Actions allowed** (View/Create/Edit/Delete/Approve)
- **Reports can access**
- **Users with this role**

---

## Activity Logs & Audit Trail

### Purpose
Track all changes for audit and security.

### Access Activity Logs
1. Click **"Admin"** menu
2. Click **"Activity Logs"**
3. See chronological log of all system changes

### Activity Log Details
| Column | Shows |
|--------|-------|
| **Date & Time** | When action occurred |
| **User** | Who did it |
| **Action** | What they did (Created/Edited/Deleted) |
| **Entity** | What was affected (Invoice #123, Project ABC) |
| **Change Details** | Before and after values |
| **IP Address** | Where they accessed from |

### Understand Activity Log
**Examples:**
- "John created Invoice INV-001"
- "Sarah updated Project Budget from ₹500K to ₹550K"
- "Admin deleted User Account: xyz@email.com"

### Filter Activity Logs
1. By **Date Range**
2. By **User**
3. By **Action Type** (Create/Edit/Delete/Approve)
4. By **Module** (Projects/Finance/etc.)
5. By **Entity** (specific project/invoice/etc.)

### View Full Details
1. Click log entry
2. See complete information:
   - Before/after comparison
   - All changed fields
   - Who made change
   - When and from where
   - Reason (if provided)

### Export Activity Report
1. Click **"Export"**
2. Select date range
3. Select filters
4. Download PDF/Excel
5. Report ready for audit

### Compliance
- All changes tracked permanently
- Can't be deleted or modified
- Proves who did what and when
- Helpful for disputes/investigations

---

## Company Settings

### Access Company Settings
1. Click **"Admin"** menu
2. Click **"Company Settings"** or **"Company Info"**
3. See company configuration

### Company Information
Edit company details:
- **Company Name**
- **Address**
- **City, State, PIN**
- **Country**
- **Phone Number**
- **Email Address**
- **Website** (if any)
- **Logo** (company logo image)
- **Legal Registration** (if applicable)
- **Tax ID/GST Number** (India)
- **PAN** (if applicable)

### Financial Settings
Configure financial defaults:
- **Fiscal Year Start** (April 1, January 1, etc.)
- **Default Currency** (₹, $, €)
- **Decimal Places** (2 digits typically)
- **Tax Rate** (default GST %, can override)
- **Approval Limits** (who approves what amount)

### Operational Settings
- **Working Days** (Monday-Friday typically)
- **Working Hours** (9 AM - 6 PM)
- **Week Off** (Saturday/Sunday)
- **Holidays** (national/local holidays)
- **Default Project Manager** (auto-assign)

### Document Templates
Upload customized templates:
- **Invoice Template**
- **PO Template**
- **Quote Template**
- **Letter Head**

### Email Configuration
- **SMTP Server Settings**
- **Default From Email**
- **Email for notifications**
- **Email for alerts**

### Save Settings
After any changes:
1. Click **"Save Settings"**
2. Confirmation appears
3. Changes take effect immediately

---

## Document Management

### View Documents
1. Click **"Admin"** menu
2. Click **"Documents"**
3. See all uploaded documents

### Document Types
- **Company Documents** (Registration, licenses, etc.)
- **Project Documents** (Designs, specifications)
- **Financial Documents** (Bank statements, tax records)
- **Compliance Documents** (Permits, approvals)

### Upload Document
1. Click **"+ Upload Document"**
2. Fill in:
   - **Document Name**
   - **Document Type** (select category)
   - **Related Project** (if applicable)
   - **Related Person** (if applicable)
   - **Description**
   - **Select File** (upload from computer)
3. Click **"Upload"**
4. Document stored in system

### View Document
1. Click document name
2. Preview opens
3. Shows:
   - Document content
   - Upload date
   - Uploaded by
   - File size
   - File type

### Download Document
1. Click document
2. Click **"Download"** button
3. File saved to computer

### Delete Document
1. Click **"Delete"** button
2. Confirm deletion
3. Document removed

### Organize Documents
- Organized by type
- Organized by project
- Search by name/keywords
- Filter by date

### Document Retention
- Keep important documents safely
- Auto-backup to cloud (if configured)
- Version history available (if multiple uploads)

---

## Settings & Preferences

### Access Settings
1. Click your **name** (top right)
2. Click **"Settings"**
3. See user settings page

### User Preferences
Customize your experience:

**Notifications:**
- ☐ Email notifications (checklist)
- ☐ Push notifications
- ☐ Auto-save documents

**Appearance:**
- ☐ Dark mode (toggle)
- Language (select)
- Font size (small/medium/large)

**Security:**
- ☐ Two-factor authentication (enable/disable)
- ☐ Auto-save work
- ☐ Data backup

**Privacy:**
- ☐ Show in directory
- ☐ Allow others to see my activity

### Save Preferences
1. Toggle options as desired
2. Click **"Save All Settings"**
3. Confirmation appears
4. Settings saved and applied

### Change Password
1. Click **"Change Password"**
2. Enter current password
3. Enter new password
4. Confirm new password
5. Click **"Update"**

### Two-Factor Authentication
Enable for extra security:
1. Click **"Enable 2FA"**
2. Scan QR code with authenticator app
3. Enter 6-digit code from app
4. Click **"Verify"**
5. 2FA enabled
6. Next login requires 2FA code

---

# COMMON WORKFLOWS

## Complete Project Workflow

```
1. CREATE PROJECT
   ├─ Enter project details
   ├─ Set budget
   └─ Assign project manager

2. ASSIGN STAFF
   ├─ Add team members
   ├─ Assign roles
   └─ Link to tasks

3. CREATE TASKS
   ├─ Define milestones
   ├─ Set timelines
   └─ Assign team members

4. TRACK PROGRESS
   ├─ Update task status
   ├─ Monitor timeline
   └─ Track costs

5. MANAGE FINANCE
   ├─ Track expenses
   ├─ Monitor budget
   └─ Generate invoices

6. COMPLETE PROJECT
   ├─ Mark all tasks done
   ├─ Final cost report
   └─ Release retentions
```

---

## Procurement to Payment Workflow

```
1. CREATE INDENT
   ├─ List materials needed
   ├─ Set quantities
   └─ Submit for approval

2. APPROVE INDENT
   ├─ Review quantities
   ├─ Check budget
   └─ Approve/Reject

3. CREATE & SEND PO
   ├─ Select supplier
   ├─ Add items
   └─ Send to supplier

4. RECEIVE GOODS
   ├─ Create GRN
   ├─ Inspect goods
   └─ Record receipt

5. PROCESS INVOICE
   ├─ Receive supplier invoice
   ├─ Match to GRN
   └─ Verify amounts

6. MAKE PAYMENT
   ├─ Approve invoice
   ├─ Process payment
   └─ Record in ledger
```

---

## Expense Approval Workflow

```
1. SUBMIT EXPENSE
   ├─ Enter amount
   ├─ Select category
   └─ Attach receipt

2. TIER 1 REVIEW
   ├─ If ≤ ₹50K: Manager approves
   ├─ Reviewed
   └─ Approved/Rejected

3. TIER 2 REVIEW (if > ₹50K)
   ├─ Director reviews
   ├─ Manager's note reviewed
   └─ Approved/Rejected

4. POST TO TRANSACTIONS
   ├─ Approved expense
   ├─ Posted to GL
   └─ Included in reports

5. REIMBURSEMENT
   ├─ Amount paid to employee
   ├─ Included in payroll/payment
   └─ Recorded as paid
```

---

## Payroll Processing Workflow

```
1. CREATE PAYROLL CYCLE
   ├─ Select month
   ├─ System calculates
   └─ Review amounts

2. REVIEW & ADJUST
   ├─ Check attendance
   ├─ Verify deductions
   └─ Make adjustments if needed

3. SUBMIT FOR APPROVAL
   ├─ Review all records
   ├─ Prepare for approval
   └─ Submit

4. MANAGER APPROVAL
   ├─ Review salary data
   ├─ Check budget
   └─ Approve

5. PROCESS PAYMENT
   ├─ Generate bank file
   ├─ Send to bank
   └─ Process payments

6. DISTRIBUTE SLIPS
   ├─ Generate salary slips
   ├─ Distribute to staff
   └─ File records
```

---

# TIPS & BEST PRACTICES

## Data Entry Best Practices

### Accuracy Tips
1. **Double-check amounts** before saving
2. **Use consistent naming** (e.g., all vendor names same format)
3. **Attach all supporting documents** (receipts, invoices, photos)
4. **Fill in descriptions** - Future you will need context
5. **Use today's date** for current transactions
6. **Don't leave required fields blank**

### Organization Tips
1. **Use categories consistently** - Stick to defined categories
2. **Name projects clearly** - "Project ABC - Phase 2" not "Proj2"
3. **Use sequential references** - Invoice numbers, PO numbers
4. **Group related items** - Link transactions to projects
5. **Archive old records** - Keep system clean

---

## Financial Management Best Practices

### Budget Control
1. **Set realistic budgets** - Base on historical data
2. **Review actual vs budget monthly** - Catch overruns early
3. **Adjust budgets if needed** - Get approval for changes
4. **Set budget alerts** - Know when approaching limits
5. **Track contingency** - Keep 10-15% buffer for overruns

### Cash Flow Management
1. **Monitor cash daily** - Know available cash
2. **Plan payments** - Pay on due dates to maintain relationships
3. **Follow up receivables** - Invoice clients promptly
4. **Negotiate terms** - Better payment terms improve cash
5. **Forecast cash** - Plan ahead for big expenses

### Approval Workflow
1. **Submit expenses with receipt** - Always attach proof
2. **Submit timely** - Don't wait months to submit
3. **Include justification** - Explain why needed
4. **Use correct category** - Helps with analysis
5. **Follow routing rules** - Know who approves what amount

---

## Project Management Best Practices

### Planning
1. **Define all tasks** - List everything that needs doing
2. **Assign durations** - Be realistic about time
3. **Set dependencies** - Show which tasks block others
4. **Assign owners** - Clear responsibility
5. **Set milestones** - Break project into phases

### Execution
1. **Update progress weekly** - Keep data current
2. **Communicate changes** - Alert team of delays
3. **Flag risks early** - Don't wait for problems
4. **Track costs daily** - Monitor spending
5. **Manage changes** - Document scope changes

### Monitoring
1. **Check budget vs actual** - Monthly review
2. **Monitor timeline** - Watch for delays
3. **Track team productivity** - Attendance/progress
4. **Generate reports** - Share status with stakeholders
5. **Adjust as needed** - Make corrections early

---

## Attendance & HR Best Practices

### For Employees
1. **Punch in & out on time** - System tracks attendance
2. **Take clear photos** - Good lighting, face visible
3. **Complete daily** - Don't bunch punches at month end
4. **Submit leaves early** - Give advance notice
5. **Update profile** - Keep contact info current

### For Managers
1. **Review attendance monthly** - Identify trends
2. **Address absences early** - Talk to employees
3. **Approve reasonable leaves** - Be fair and consistent
4. **Monitor overtime** - Track extra hours
5. **Generate reports** - Document attendance records

---

## Procurement Best Practices

### Vendor Management
1. **Evaluate multiple quotes** - Compare before buying
2. **Negotiate prices** - Don't accept first quote
3. **Check delivery terms** - Faster isn't always better
4. **Review vendor performance** - Rate suppliers
5. **Build relationships** - Good vendors valuable long-term

### Purchase Orders
1. **Always use POs** - Document all purchases
2. **Be specific** - Include specs, quantities, delivery date
3. **Set expectations** - Clear payment/delivery terms
4. **Follow up delivery** - Confirm receipt
5. **Keep records** - Archive all POs

### Invoice Processing
1. **Match invoice to PO & GRN** - "3-way match"
2. **Check quantities** - Received matches PO
3. **Check prices** - Invoiced matches PO
4. **Check dates** - Payment terms haven't expired
5. **Process on time** - Pay by due date

---

## Security Best Practices

### Password Security
1. **Use strong passwords** - Mix uppercase, lowercase, numbers, symbols
2. **Change regularly** - Every 90 days
3. **Don't share passwords** - Keep them private
4. **Use unique passwords** - Different for each system
5. **Never write passwords down** - Use a secure password manager

### Data Protection
1. **Don't leave system unattended** - Lock when away
2. **Log out completely** - Don't just close browser
3. **Report suspicious activity** - Tell admin immediately
4. **Use HTTPS only** - Check for padlock icon
5. **Don't use public WiFi** - VPN if necessary

### Access Control
1. **Only access your role's data** - Respect permissions
2. **Don't try to bypass restrictions** - Report if you need access
3. **Report inappropriate access** - If someone accesses your data
4. **Keep credentials safe** - No one else should log in as you
5. **Confirm before sharing** - Get approval before sharing data

---

# TROUBLESHOOTING

## Common Issues & Solutions

### Login Issues

**Issue: Can't Login**
- **Solution 1:** Check username/email spelling
- **Solution 2:** Check CAPS LOCK is off
- **Solution 3:** Click "Forgot Password" to reset
- **Solution 4:** Clear browser cookies and cache
- **Solution 5:** Try different browser
- **Contact:** Admin if still can't login

**Issue: Account Locked**
- **Cause:** Too many failed login attempts
- **Solution:** Wait 15 minutes and try again
- **Or:** Contact admin to unlock

---

### Data Loading Issues

**Issue: Page shows "Loading..." but never loads**
- **Check 1:** Internet connection OK?
- **Check 2:** Try refreshing page (F5)
- **Check 3:** Clear browser cache
- **Check 4:** Try different browser
- **Check 5:** Check back-end status
- **If persistent:** Contact admin

**Issue: Data shows as "N/A" or blank**
- **Check 1:** Is data actually entered?
- **Check 2:** Do you have permission to view?
- **Check 3:** Is date filter set correctly?
- **Check 4:** Try clearing filters and reloading
- **If persistent:** Contact admin

---

### Form Issues

**Issue: Can't submit form - "Required field" error**
- **Cause:** Missing required field
- **Solution:** Look for red * marks
- **Action:** Fill in all required fields
- **Common:** Name, Email, Amount fields often required

**Issue: Form saves but data doesn't appear**
- **Check 1:** Page might be cached
- **Solution 1:** Refresh page (Ctrl+F5)
- **Solution 2:** Wait a moment and refresh
- **Solution 3:** Check different filter/date range
- **If still not visible:** Contact admin

---

### Upload Issues

**Issue: Can't upload file**
- **Check file size:** Some files too large
- **Check file type:** Only certain formats allowed
- **Check browser:** Different browsers handle uploads differently
- **Solution:** Compress large files
- **Solution:** Convert to allowed format (PDF, JPG, Excel)
- **Solution:** Try different browser

**Issue: Photo capture not working**
- **Check camera permission:** Browser asks permission
- **Check browser settings:** Allow camera access
- **Check camera:** Make sure camera works
- **Solution:** Refresh page and try again
- **Solution:** Use different browser
- **Solution:** Try on different device

---

### Report Issues

**Issue: Report shows no data**
- **Check filters:** Are filters too restrictive?
- **Solution:** Remove filters and try again
- **Solution:** Check date range includes data
- **Check:** You have permission to view this report
- **Try:** Different date range or all data

**Issue: Report won't export**
- **Check:** Pop-ups aren't blocked
- **Solution:** Allow pop-ups for this site
- **Check:** Sufficient disk space on computer
- **Solution:** Try different export format (PDF vs Excel)
- **Solution:** Try different browser

---

### Performance Issues

**Issue: System running slow**
- **Check:** Internet speed OK?
- **Solution 1:** Refresh page
- **Solution 2:** Close other browser tabs
- **Solution 3:** Clear browser cache
- **Solution 4:** Try different browser
- **If peak hours:** System might be busy, try again later

**Issue: Photos taking long to load**
- **Cause:** Large photo files
- **Solution:** Compress photos before uploading
- **Solution:** Reduce photo quality setting
- **Solution:** Upload during off-peak hours

---

### Permission Issues

**Issue: "Permission Denied" or "Access Restricted"**
- **Cause:** Your role doesn't allow this action
- **Solution:** Ask your manager or admin
- **Action:** Admin can grant permission to your role
- **Request:** Email admin with exactly what you need

**Issue: Can't see certain modules**
- **Cause:** Your role doesn't include that module
- **Solution:** Contact admin to add module to your role
- **Info:** Tell admin exactly which module you need

---

### Financial Calculation Issues

**Issue: Invoice total showing incorrectly**
- **Check:** All item quantities and prices entered?
- **Check:** Tax % set correctly?
- **Solution:** Verify each line item manually
- **Solution:** Delete problematic line and re-enter

**Issue: Budget showing different amount**
- **Check:** Latest updates saved?
- **Solution:** Refresh page (Ctrl+F5)
- **Check:** Verify all transactions posted
- **If different:** Contact finance person

---

### Approval Workflow Issues

**Issue: Expense stuck in "Pending Approval"**
- **Check:** Is it Tier 1 or Tier 2 needed?
- **Check:** Has Tier 1 approved yet?
- **Solution:** Check who needs to approve
- **Action:** Remind approver to review

**Issue: Can't approve/reject item**
- **Cause:** Not in your approval chain
- **Check:** Your role has approval permission?
- **Solution:** Contact admin if you should be approver

---

## Getting Help

### Contact Support
1. **Document the issue:** What were you doing?
2. **Note error message:** Write it down exactly
3. **Take screenshot:** Visual proof helps
4. **Contact admin:** Send email with details
5. **Include:** Login name, module, time issue occurred

### Information to Provide
- **Your Name & Email**
- **Issue Description** - What were you trying to do?
- **Error Message** - Exact message if any
- **When it happened** - Date and time
- **How to reproduce** - Steps to cause issue
- **Screenshot** - Image of error
- **What you expected** - What should have happened

### Response Time
- **Critical (can't work):** ASAP
- **High (major feature broken):** Same day
- **Medium (feature not working right):** 1-2 days
- **Low (minor issue):** Within a week

---

## Prevention Tips

### Avoid Issues
1. **Keep software updated** - Install updates when available
2. **Clear cache regularly** - Weekly or monthly
3. **Backup important documents** - In case of loss
4. **Use strong passwords** - Harder to hack
5. **Report issues early** - Before they get worse
6. **Ask before doing** - When unsure how to do something
7. **Read help text** - Tool-tips often explain things
8. **Follow procedures** - Use workflows as designed

---

# CONCLUSION

Congratulations! You now have a comprehensive understanding of the Construction Finance Management System.

## Key Takeaways

✅ **Dashboard** - Your command center for key metrics
✅ **Projects** - Complete project lifecycle management
✅ **Staff** - Team management and payroll
✅ **Attendance** - Employee punch in/out with photo verification
✅ **Finance** - Complete financial tracking and reporting
✅ **Procurement** - Full supply chain from indent to payment
✅ **Administration** - Users, roles, permissions, and settings

## Next Steps

1. **Explore the system** - Log in and navigate around
2. **Create test data** - Practice with sample projects/transactions
3. **Involve your team** - Train staff on their modules
4. **Set up processes** - Configure workflows for your organization
5. **Generate reports** - Start tracking key metrics
6. **Monitor regularly** - Weekly/monthly review of data

## Remember

- **Data quality matters** - Garbage in, garbage out
- **Follow workflows** - They exist for a reason
- **Ask questions** - Better to ask than make mistakes
- **Keep learning** - New features and improvements coming
- **Provide feedback** - Help us improve the system

---

**Questions? Contact your System Administrator**

**Happy Managing! 🚀**

