"""Add account_code column to cash_transactions for Chart of Accounts integration

Revision ID: finance_006
Revises: add_soft_delete_001
Create Date: 2026-04-05

"""
from alembic import op
import sqlalchemy as sa


revision = 'finance_006'
down_revision = 'add_soft_delete_001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cash_transactions', sa.Column('account_code', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('cash_transactions', 'account_code')
