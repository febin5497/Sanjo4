"""Add retention handling and vendor enhancements

Revision ID: finance_003
Revises: finance_002
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa

revision = 'finance_003'
down_revision = 'finance_002'
branch_labels = None
depends_on = None

def upgrade():
    # Add retention fields to invoices
    op.add_column('invoices', sa.Column('retention_percentage', sa.Float(), server_default='0'))
    op.add_column('invoices', sa.Column('retention_amount', sa.Float(), server_default='0'))
    op.add_column('invoices', sa.Column('retention_released_date', sa.Date()))
    op.add_column('invoices', sa.Column('retention_status', sa.String(20), server_default='pending'))

    # Add vendor enhancement fields to suppliers
    op.add_column('suppliers', sa.Column('bank_name', sa.String(150)))
    op.add_column('suppliers', sa.Column('account_number', sa.String(50)))
    op.add_column('suppliers', sa.Column('ifsc_code', sa.String(20)))
    op.add_column('suppliers', sa.Column('gstin', sa.String(15)))
    op.add_column('suppliers', sa.Column('payment_terms', sa.String(100)))
    op.add_column('suppliers', sa.Column('credit_limit', sa.Float(), server_default='0'))
    op.add_column('suppliers', sa.Column('performance_score', sa.Float(), server_default='0'))
    op.add_column('suppliers', sa.Column('on_time_delivery_percentage', sa.Float(), server_default='0'))

def downgrade():
    op.drop_column('invoices', 'retention_status')
    op.drop_column('invoices', 'retention_released_date')
    op.drop_column('invoices', 'retention_amount')
    op.drop_column('invoices', 'retention_percentage')

    op.drop_column('suppliers', 'on_time_delivery_percentage')
    op.drop_column('suppliers', 'performance_score')
    op.drop_column('suppliers', 'credit_limit')
    op.drop_column('suppliers', 'payment_terms')
    op.drop_column('suppliers', 'gstin')
    op.drop_column('suppliers', 'ifsc_code')
    op.drop_column('suppliers', 'account_number')
    op.drop_column('suppliers', 'bank_name')
