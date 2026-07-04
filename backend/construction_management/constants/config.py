"""
Application Configuration Constants

Centralized configuration for rates, limits, defaults, and other constants
used throughout the application.
"""

# GST (Goods and Services Tax) Configuration
GST_RATES = {
    "zero": 0.0,
    "five": 5.0,
    "twelve": 12.0,
    "eighteen": 18.0,
    "twenty_eight": 28.0
}

GST_CATEGORIES = {
    "services": 18.0,
    "materials": 18.0,
    "equipment": 12.0,
    "labor": 18.0,
    "supplies": 5.0,
    "food": 5.0
}

# Payroll Configuration
PAYROLL_CONFIG = {
    "pf_percentage": 12.0,  # Provident Fund
    "esi_percentage": 0.75,  # Employee State Insurance
    "pt_percentage": 0.0,  # Professional Tax (state-dependent)
    "it_slab": {
        "500000": 0.05,
        "1000000": 0.20,
        "2000000": 0.30
    },
    "working_days_per_month": 26,
    "pf_threshold": 15000  # PF only if salary > threshold
}

# Attendance Configuration
ATTENDANCE_CONFIG = {
    "mark_attendance_deadline_hours": 8,  # Hours after shift start
    "half_day_threshold": 0.5,  # 50% attendance = half day
    "max_consecutive_leave_days": 30,
    "penalty_for_late": 50,  # Rupees
    "penalty_for_absent": 100  # Rupees
}

# Budget Configuration
BUDGET_CONFIG = {
    "warning_threshold": 80,  # Alert at 80% of budget
    "critical_threshold": 95,  # Critical alert at 95%
    "allow_over_budget": True,
    "approval_required_above": 100000  # Approval needed for budgets > 100k
}

# Approval Workflow Configuration
APPROVAL_CONFIG = {
    "multi_level_enabled": True,
    "finance_approval_levels": 2,  # Manager -> Director
    "purchase_approval_levels": 2,
    "payment_approval_threshold": 50000,  # Amount requiring additional approval
    "auto_approve_below": 5000  # Auto-approve transactions < 5k
}

# Pagination Defaults
PAGINATION = {
    "default_per_page": 10,
    "max_per_page": 100,
    "min_per_page": 1
}

# Date/Time Configuration
DATETIME_CONFIG = {
    "timezone": "Asia/Kolkata",
    "date_format": "%d-%m-%Y",
    "datetime_format": "%d-%m-%Y %H:%M:%S",
    "fiscal_year_start": "04-01",  # April 1 (India)
    "fiscal_year_end": "03-31"  # March 31 (India)
}

# File Upload Configuration
FILE_CONFIG = {
    "max_file_size_mb": 10,
    "allowed_extensions": ["pdf", "jpg", "jpeg", "png", "xlsx", "xls", "doc", "docx"],
    "upload_folder": "uploads",
    "document_subfolder": "documents",
    "photo_subfolder": "photos",
    "report_subfolder": "reports"
}

# Report Configuration
REPORT_CONFIG = {
    "items_per_page": 50,
    "include_totals": True,
    "include_footer": True,
    "default_format": "pdf",
    "supported_formats": ["pdf", "excel", "csv"]
}

# Employee Roles
EMPLOYEE_ROLES = {
    "admin": "Admin",
    "project_manager": "Project Manager",
    "site_engineer": "Site Engineer",
    "foreman": "Foreman",
    "laborer": "Laborer",
    "accountant": "Accountant",
    "finance_manager": "Finance Manager",
    "hr_manager": "HR Manager",
    "supervisor": "Supervisor",
    "equipment_operator": "Equipment Operator"
}

# Retention Configuration
RETENTION_CONFIG = {
    "default_percentage": 5.0,  # 5% retention
    "max_percentage": 20.0,
    "min_percentage": 0.0,
    "release_after_days": 30,  # Release after 30 days of payment
}

# Material Units
MATERIAL_UNITS = {
    "pcs": "Pieces",
    "kg": "Kilogram",
    "bag": "Bag",
    "box": "Box",
    "crate": "Crate",
    "meter": "Meter",
    "sqm": "Square Meter",
    "cum": "Cubic Meter",
    "liter": "Liter",
    "rft": "Running Feet",
    "ton": "Metric Ton"
}

# Project Types
PROJECT_TYPES = {
    "residential": "Residential",
    "commercial": "Commercial",
    "industrial": "Industrial",
    "infrastructure": "Infrastructure",
    "renovation": "Renovation",
    "maintenance": "Maintenance"
}

# Vehicle Types
VEHICLE_TYPES = {
    "truck": "Truck",
    "van": "Van",
    "tempo": "Tempo",
    "excavator": "Excavator",
    "jcb": "JCB",
    "paver": "Paver",
    "roller": "Roller",
    "crane": "Crane",
    "mixer": "Mixer",
    "generator": "Generator"
}

# Fuel Types
FUEL_TYPES = {
    "petrol": "Petrol",
    "diesel": "Diesel",
    "cng": "CNG",
    "lpg": "LPG",
    "electric": "Electric"
}

# Email Configuration
EMAIL_CONFIG = {
    "from_address": "noreply@constructionmanagement.com",
    "from_name": "Construction Management",
    "max_retries": 3,
    "timeout_seconds": 30
}

# API Configuration
API_CONFIG = {
    "request_timeout": 30,
    "max_request_size_mb": 50,
    "rate_limit_per_minute": 100,
    "enable_cors": True,
    "cors_origins": ["*"]
}
