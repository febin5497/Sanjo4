"""Add staff_id, staff_name, and project_name to cash_transactions table

Revision ID: 8e9f0a1b2c3d
Revises: add_leave_reason
Create Date: 2026-03-29 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e9f0a1b2c3d'
down_revision = 'add_leave_reason'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to cash_transactions table
    op.add_column('cash_transactions', sa.Column('staff_id', sa.Integer(), nullable=True))
    op.add_column('cash_transactions', sa.Column('staff_name', sa.String(255), nullable=True))
    op.add_column('cash_transactions', sa.Column('project_name', sa.String(255), nullable=True))


def downgrade():
    # Remove columns from cash_transactions table
    op.drop_column('cash_transactions', 'project_name')
    op.drop_column('cash_transactions', 'staff_name')
    op.drop_column('cash_transactions', 'staff_id')
