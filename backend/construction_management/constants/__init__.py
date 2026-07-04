"""
Constants Package

Centralized configuration and status definitions for the application.
"""

from .statuses import (
    InvoiceStatus,
    TransactionStatus,
    PurchaseStatus,
    PurchaseIndentStatus,
    GRNStatus,
    SalesStatus,
    QuoteStatus,
    BudgetStatus,
    PayrollCycleStatus,
    AttendanceStatus,
    ApprovalStatus,
    RetentionStatus,
    DocumentStatus,
    ProjectStatus,
    STATUS_TRANSITIONS,
    is_valid_status_transition,
    get_all_statuses,
)

from .config import (
    GST_RATES,
    GST_CATEGORIES,
    PAYROLL_CONFIG,
    ATTENDANCE_CONFIG,
    BUDGET_CONFIG,
    APPROVAL_CONFIG,
    PAGINATION,
    DATETIME_CONFIG,
    FILE_CONFIG,
    REPORT_CONFIG,
    EMPLOYEE_ROLES,
    RETENTION_CONFIG,
    MATERIAL_UNITS,
    PROJECT_TYPES,
    VEHICLE_TYPES,
    FUEL_TYPES,
    EMAIL_CONFIG,
    API_CONFIG,
)

__all__ = [
    # Status Enums
    "InvoiceStatus",
    "TransactionStatus",
    "PurchaseStatus",
    "PurchaseIndentStatus",
    "GRNStatus",
    "SalesStatus",
    "QuoteStatus",
    "BudgetStatus",
    "PayrollCycleStatus",
    "AttendanceStatus",
    "ApprovalStatus",
    "RetentionStatus",
    "DocumentStatus",
    "ProjectStatus",
    # Status Functions
    "STATUS_TRANSITIONS",
    "is_valid_status_transition",
    "get_all_statuses",
    # Configuration
    "GST_RATES",
    "GST_CATEGORIES",
    "PAYROLL_CONFIG",
    "ATTENDANCE_CONFIG",
    "BUDGET_CONFIG",
    "APPROVAL_CONFIG",
    "PAGINATION",
    "DATETIME_CONFIG",
    "FILE_CONFIG",
    "REPORT_CONFIG",
    "EMPLOYEE_ROLES",
    "RETENTION_CONFIG",
    "MATERIAL_UNITS",
    "PROJECT_TYPES",
    "VEHICLE_TYPES",
    "FUEL_TYPES",
    "EMAIL_CONFIG",
    "API_CONFIG",
]
