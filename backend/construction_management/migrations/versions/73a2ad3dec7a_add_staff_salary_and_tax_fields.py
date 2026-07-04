"""Add staff salary and tax fields

Revision ID: 73a2ad3dec7a
Revises: 575e03e381d5
Create Date: 2026-03-26 14:12:52.437514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73a2ad3dec7a'
down_revision = '575e03e381d5'
branch_labels = None
depends_on = None


def upgrade():
    # Add staff financial columns
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.add_column(sa.Column('monthly_salary', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('ctc', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('pf_applicable', sa.Boolean(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('pf_percentage', sa.Float(), nullable=False, server_default='12.0'))
        batch_op.add_column(sa.Column('pf_account_number', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('esi_applicable', sa.Boolean(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('esi_percentage', sa.Float(), nullable=False, server_default='0.75'))
        batch_op.add_column(sa.Column('esi_account_number', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('professional_tax_applicable', sa.Boolean(), nullable=False, server_default='1'))
        batch_op.add_column(sa.Column('professional_tax_state', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('professional_tax_amount', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('pan_number', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('income_tax_regime', sa.String(length=20), nullable=False, server_default='Old'))
        batch_op.add_column(sa.Column('lic_premium', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('loan_deduction', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('other_deductions', sa.Float(), nullable=False, server_default='0'))


def downgrade():
    # Remove staff financial columns
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.drop_column('other_deductions')
        batch_op.drop_column('loan_deduction')
        batch_op.drop_column('lic_premium')
        batch_op.drop_column('income_tax_regime')
        batch_op.drop_column('pan_number')
        batch_op.drop_column('professional_tax_amount')
        batch_op.drop_column('professional_tax_state')
        batch_op.drop_column('professional_tax_applicable')
        batch_op.drop_column('esi_account_number')
        batch_op.drop_column('esi_percentage')
        batch_op.drop_column('esi_applicable')
        batch_op.drop_column('pf_account_number')
        batch_op.drop_column('pf_percentage')
        batch_op.drop_column('pf_applicable')
        batch_op.drop_column('ctc')
        batch_op.drop_column('monthly_salary')
