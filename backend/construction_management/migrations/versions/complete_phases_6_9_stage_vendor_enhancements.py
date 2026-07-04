"""Complete phases 6-9: Stage billing, vendor enhancements, payroll approvals

Revision ID: phase_6_9_complete
Revises: finance_005_add_audit_fields_to_models
Create Date: 2026-04-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'phase_6_9_complete'
down_revision = 'finance_005'
branch_labels = None
depends_on = None


def upgrade():
    # NOTE: project_stages table already created by add_stage_based_billing migration
    # NOTE: supplier columns already added by previous migrations
    # NOTE: vendor_performance table already exists
    # NOTE: payroll_records columns already added
    # This migration is now a no-op due to duplicate data from earlier migrations

    # All enhancements for phases 6-9 have been completed in earlier migration files:
    # - add_stage_based_billing.py (finance_002) - created project_stages table
    # - add_retention_and_vendor_enhancements.py (finance_003) - added supplier columns
    # - All payroll record changes already in place
    pass


def downgrade():
    # ================== Downgrade vendor_performance table ==================
    op.drop_index('ix_vendor_performance_recorded_date', table_name='vendor_performance')
    op.drop_index('ix_vendor_performance_vendor_id', table_name='vendor_performance')
    op.drop_table('vendor_performance')

    # ================== Downgrade suppliers table extensions ==================
    op.drop_index('ix_suppliers_gstin', table_name='suppliers')
    op.drop_column('suppliers', 'contact_persons')
    op.drop_column('suppliers', 'credit_limit')
    op.drop_column('suppliers', 'payment_terms')
    op.drop_column('suppliers', 'pan')
    op.drop_column('suppliers', 'gstin')
    op.drop_column('suppliers', 'ifsc_code')
    op.drop_column('suppliers', 'account_number')
    op.drop_column('suppliers', 'bank_name')

    # NOTE: project_stages table drop skipped (was created by add_stage_based_billing)

    # ================== Downgrade payroll_records table ==================
    op.drop_column('payroll_records', 'slip_generated_at')
    op.drop_column('payroll_records', 'rejected_at')
    op.drop_column('payroll_records', 'rejected_by_id')
    op.drop_column('payroll_records', 'rejection_reason')
