"""Add leave_reason to attendance

Revision ID: add_leave_reason
Revises: 575e03e381d5
Create Date: 2026-03-18 01:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_leave_reason'
down_revision = 'f9d791e66671'  # Updated to be after location columns migration
branch_labels = None
depends_on = None


def upgrade():
    """Add leave_reason column to attendance table."""
    try:
        with op.batch_alter_table('attendance', schema=None) as batch_op:
            batch_op.add_column(sa.Column('leave_reason', sa.String(255), nullable=True))
    except Exception as e:
        # Column might already exist
        print(f"Note: {e}")


def downgrade():
    """Remove leave_reason column from attendance table."""
    with op.batch_alter_table('attendance', schema=None) as batch_op:
        batch_op.drop_column('leave_reason')
