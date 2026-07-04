"""
Centralized Status Enumerations

Defines all valid status values across the application to ensure consistency
and provide a single source of truth for status management.
"""

from enum import Enum


class InvoiceStatus(Enum):
    """Invoice status workflow"""
    DRAFT = "draft"
    SENT = "sent"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class TransactionStatus(Enum):
    """Financial transaction status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PurchaseStatus(Enum):
    """Purchase order status workflow"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseIndentStatus(Enum):
    """Purchase indent request status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class GRNStatus(Enum):
    """Goods Receipt Note status"""
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    DISCREPANCY = "discrepancy"
    APPROVED = "approved"


class SalesStatus(Enum):
    """Sales order status"""
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class QuoteStatus(Enum):
    """Quote/Estimate status"""
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CONVERTED = "converted"
    EXPIRED = "expired"


class BudgetStatus(Enum):
    """Budget status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    ARCHIVED = "archived"


class PayrollCycleStatus(Enum):
    """Payroll cycle status"""
    DRAFT = "draft"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PAID = "paid"
    COMPLETED = "completed"


class AttendanceStatus(Enum):
    """Attendance status"""
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LEAVE = "leave"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalStatus(Enum):
    """Generic approval request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class RetentionStatus(Enum):
    """Retention amount status (typically for invoices)"""
    PENDING = "pending"
    RELEASED = "released"
    HOLD = "hold"


class DocumentStatus(Enum):
    """Document status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ProjectStatus(Enum):
    """Project status"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


# Status Validation Mappings
STATUS_TRANSITIONS = {
    "invoice": {
        "draft": ["sent", "cancelled"],
        "sent": ["pending", "cancelled"],
        "pending": ["paid", "cancelled"],
        "paid": [],
        "overdue": ["paid"],
        "partial": ["paid", "cancelled"],
        "cancelled": []
    },
    "purchase": {
        "draft": ["submitted", "cancelled"],
        "submitted": ["approved", "rejected"],
        "approved": ["ordered"],
        "rejected": [],
        "ordered": ["received"],
        "received": [],
        "cancelled": []
    },
    "purchase_indent": {
        "draft": ["submitted", "cancelled"],
        "submitted": ["approved", "rejected"],
        "approved": [],
        "rejected": [],
        "cancelled": []
    },
    "payroll_cycle": {
        "draft": ["calculated"],
        "calculated": ["approved"],
        "approved": ["paid"],
        "paid": ["completed"],
        "completed": []
    }
}


def is_valid_status_transition(entity_type, current_status, new_status):
    """
    Validate if a status transition is allowed

    Args:
        entity_type: Type of entity (e.g., 'invoice', 'purchase')
        current_status: Current status value
        new_status: Proposed new status

    Returns:
        bool: True if transition is valid, False otherwise
    """
    if entity_type not in STATUS_TRANSITIONS:
        return True  # No restrictions defined

    allowed_transitions = STATUS_TRANSITIONS[entity_type].get(current_status, [])
    return new_status in allowed_transitions


def get_all_statuses(enum_class):
    """
    Get all valid status values for an enum

    Args:
        enum_class: Status enum class

    Returns:
        list: List of status values
    """
    return [status.value for status in enum_class]
