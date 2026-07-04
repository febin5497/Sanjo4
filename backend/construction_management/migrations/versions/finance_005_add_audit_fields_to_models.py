"""Add audit trail fields (AuditMixin) to key models

Revision ID: finance_005
Revises: finance_004
Create Date: 2026-03-31

This migration adds audit trail fields to Purchase, Budget, PayrollCycle,
Transaction, and Attendance models as part of Phase 1 consolidation.
Fields added: company_id, created_by_id, updated_by_id
"""
from alembic import op
import sqlalchemy as sa


revision = 'finance_005'
down_revision = 'finance_004'
branch_labels = None
depends_on = None


def upgrade():
    """Add audit fields (company_id, created_by_id, updated_by_id) to key tables

    NOTE: These columns have already been added to the tables in previous migrations.
    This migration is a no-op to maintain the migration chain consistency.
    """
    pass


def downgrade():
    """Remove audit fields added by this migration"""

    # ===== ATTENDANCE TABLE =====
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.drop_constraint('fk_attendance_updated_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_attendance_created_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_attendance_company_id', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('company_id')

    # ===== TRANSACTIONS TABLE =====
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transactions_updated_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_transactions_created_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_transactions_company_id', type_='foreignkey')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('company_id')
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), nullable=True)

    # ===== PAYROLL_CYCLES TABLE =====
    with op.batch_alter_table('payroll_cycles', schema=None) as batch_op:
        batch_op.drop_constraint('fk_payroll_cycles_updated_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_payroll_cycles_created_by_id', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')

    # ===== BUDGETS TABLE =====
    with op.batch_alter_table('budgets', schema=None) as batch_op:
        batch_op.drop_constraint('fk_budgets_updated_by_id', type_='foreignkey')
        batch_op.drop_column('updated_by_id')

    # ===== PURCHASES TABLE =====
    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.drop_constraint('fk_purchases_updated_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_purchases_created_by_id', type_='foreignkey')
        batch_op.drop_constraint('fk_purchases_company_id', type_='foreignkey')
        batch_op.drop_column('updated_by_id')
        batch_op.drop_column('created_by_id')
        batch_op.drop_column('company_id')
