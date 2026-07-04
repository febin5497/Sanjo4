"""Add approval tier fields to expenses table

Revision ID: add_approval_tier_expenses
Revises: add_finance_modules
Create Date: 2026-04-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_approval_tier_expenses'
down_revision = 'finance_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to expenses table
    op.add_column('expenses', sa.Column('approval_tier', sa.String(10), nullable=True, server_default='Tier1'))
    op.add_column('expenses', sa.Column('approvals_required', sa.Integer, nullable=True, server_default='1'))
    op.add_column('expenses', sa.Column('approvals_received', sa.Integer, nullable=True, server_default='0'))
    op.add_column('expenses', sa.Column('first_approver_id', sa.Integer, nullable=True))
    op.add_column('expenses', sa.Column('first_approval_date', sa.DateTime, nullable=True))
    op.add_column('expenses', sa.Column('second_approver_id', sa.Integer, nullable=True))
    op.add_column('expenses', sa.Column('second_approval_date', sa.DateTime, nullable=True))

    # Add foreign key constraints
    op.create_foreign_key('fk_expenses_first_approver', 'expenses', 'user', ['first_approver_id'], ['id'])
    op.create_foreign_key('fk_expenses_second_approver', 'expenses', 'user', ['second_approver_id'], ['id'])


def downgrade():
    # Remove foreign keys and columns
    op.drop_constraint('fk_expenses_second_approver', 'expenses', type_='foreignkey')
    op.drop_constraint('fk_expenses_first_approver', 'expenses', type_='foreignkey')
    op.drop_column('expenses', 'second_approval_date')
    op.drop_column('expenses', 'second_approver_id')
    op.drop_column('expenses', 'first_approval_date')
    op.drop_column('expenses', 'first_approver_id')
    op.drop_column('expenses', 'approvals_received')
    op.drop_column('expenses', 'approvals_required')
    op.drop_column('expenses', 'approval_tier')
