"""Add GST fields to invoices table

Revision ID: a1b2c3d4e5f6
Revises: 8e9f0a1b2c3d
Create Date: 2026-03-30 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '8e9f0a1b2c3d'
branch_labels = None
depends_on = None


def upgrade():
    # Add GST fields to invoices table
    with op.batch_alter_table('invoices', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subtotal', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('include_gst', sa.Boolean(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('gst_rate', sa.Float(), nullable=False, server_default='18.0'))
        batch_op.add_column(sa.Column('gst_amount', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('discount', sa.Float(), nullable=False, server_default='0'))


def downgrade():
    # Remove GST fields from invoices table
    with op.batch_alter_table('invoices', schema=None) as batch_op:
        batch_op.drop_column('discount')
        batch_op.drop_column('gst_amount')
        batch_op.drop_column('gst_rate')
        batch_op.drop_column('include_gst')
        batch_op.drop_column('subtotal')
