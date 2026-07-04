"""Add indent_id FK to purchases table

Revision ID: finance_004
Revises: finance_003
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa


revision = 'finance_004'
down_revision = 'finance_003'
branch_labels = None
depends_on = None


def upgrade():
    # Add indent_id column to purchases table
    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.add_column(sa.Column('indent_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_purchases_indent_id', 'purchase_indents', ['indent_id'], ['id'])


def downgrade():
    with op.batch_alter_table('purchases', schema=None) as batch_op:
        batch_op.drop_constraint('fk_purchases_indent_id', type_='foreignkey')
        batch_op.drop_column('indent_id')
