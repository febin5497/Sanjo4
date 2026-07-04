"""
Approval Management Module

Unified approval workflow system consolidating approvals from:
- Finance (invoices, transactions)
- Budget management
- Attendance (photo approvals)
- Any other entity requiring approvals

Provides:
- Multi-level approval requests
- Role-based approver assignment
- Amount-based approval thresholds
- Complete audit trail
- Configurable approval rules per entity type
"""

from .models.approval import (
    ApprovalRequest,
    ApprovalHistory,
    ApprovalConfiguration
)
from .services.approval_service import ApprovalService

__all__ = [
    'ApprovalRequest',
    'ApprovalHistory',
    'ApprovalConfiguration',
    'ApprovalService',
]
