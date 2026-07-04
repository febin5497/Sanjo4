"""
Base Model Mixins

Provides reusable model mixins for common functionality like:
- Timestamp tracking (created_at, updated_at)
- Audit trails (created_by, updated_by)
- Multi-tenancy (company_id)
- Approval workflows (approved_by, approval_notes, etc.)
"""

from datetime import datetime
from extensions import db


class TimestampMixin:
    """
    Mixin that adds timestamp fields to track model creation and updates.

    Fields:
    - created_at: When the record was created (auto-set)
    - updated_at: When the record was last updated (auto-set)
    """
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class CompanyMixin:
    """
    Mixin for multi-tenancy support via company_id.

    Ensures records are automatically scoped to the company context.

    Fields:
    - company_id: Foreign key to Company
    """
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False
    )


class AuditMixin(TimestampMixin, CompanyMixin):
    """
    Mixin that combines timestamp and audit trail functionality.

    Tracks who created/modified the record and when.

    Fields (from TimestampMixin):
    - created_at
    - updated_at

    Fields (from CompanyMixin):
    - company_id

    Fields (this mixin):
    - created_by_id: User who created the record
    - updated_by_id: User who last updated the record
    """
    created_by_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )
    updated_by_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )


class ApprovalFieldsMixin:
    """
    Mixin for approval workflow fields.

    Tracks approval status, who approved, and related notes.

    Fields:
    - approval_status: Current approval status (pending, approved, rejected)
    - approved_by_id: User who approved
    - approved_at: When approval happened
    - approval_notes: Approver's comments
    - rejection_reason: If rejected, why
    """
    approval_status = db.Column(
        db.String(20),
        default='pending',
        nullable=False
    )
    approved_by_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=True
    )
    approved_at = db.Column(
        db.DateTime,
        nullable=True
    )
    approval_notes = db.Column(
        db.Text,
        nullable=True
    )
    rejection_reason = db.Column(
        db.Text,
        nullable=True
    )

    def approve(self, user_id, notes=""):
        """Mark as approved"""
        self.approval_status = 'approved'
        self.approved_by_id = user_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes

    def reject(self, user_id, reason=""):
        """Mark as rejected"""
        self.approval_status = 'rejected'
        self.approved_by_id = user_id
        self.approved_at = datetime.utcnow()
        self.rejection_reason = reason


class AmountMixin:
    """
    Mixin for amount tracking in financial records.

    Supports amount, discount, tax, and total calculations.

    Fields:
    - amount: Base amount
    - discount_percentage: Discount percentage (0-100)
    - discount_amount: Calculated discount
    - tax_percentage: Tax percentage
    - tax_amount: Calculated tax
    - total_amount: Final amount (amount - discount + tax)
    """
    amount = db.Column(db.Float, default=0.0, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_percentage = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0, nullable=False)

    def calculate_totals(self):
        """Recalculate discount, tax, and total amounts"""
        self.discount_amount = (self.amount * self.discount_percentage) / 100
        self.tax_amount = ((self.amount - self.discount_amount) * self.tax_percentage) / 100
        self.total_amount = (self.amount - self.discount_amount + self.tax_amount)


class StatusMixin:
    """
    Mixin for status field with validation.

    Provides a standard status field for workflow tracking.

    Fields:
    - status: Current status value
    """
    status = db.Column(db.String(50), nullable=False)

    def can_transition_to(self, new_status, allowed_transitions):
        """
        Check if status transition is allowed.

        Args:
            new_status: Desired new status
            allowed_transitions: Dict mapping current_status to list of allowed next statuses

        Returns:
            bool: True if transition allowed
        """
        allowed = allowed_transitions.get(self.status, [])
        return new_status in allowed


class SearchableMixin:
    """
    Mixin to provide common search methods.

    Can be extended by child models to define searchable fields.
    """
    @classmethod
    def search(cls, query, search_term):
        """
        Filter query by search term.

        Child models should override this method and define which fields to search.

        Args:
            query: SQLAlchemy query object
            search_term: String to search for

        Returns:
            Filtered query object
        """
        # Override in child models
        return query


class PaginationMixin:
    """
    Utility mixin for pagination support.

    Provides helper methods for paginated queries.
    """
    @staticmethod
    def paginate(query, page=1, per_page=10):
        """
        Paginate a query.

        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Pagination object with items, total, pages
        """
        return query.paginate(page=page, per_page=per_page, error_out=False)
