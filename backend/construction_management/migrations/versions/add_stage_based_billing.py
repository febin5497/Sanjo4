"""Add stage-based billing support

Revision ID: finance_002
Revises: finance_001
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa

revision = 'finance_002'
down_revision = 'add_approval_tier_expenses'
branch_labels = None
depends_on = None

def upgrade():
    # Create project_stages table
    op.create_table(
        'project_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('percentage_complete', sa.Float(), server_default='0'),
        sa.Column('billing_percentage', sa.Float(), server_default='0'),
        sa.Column('planned_start_date', sa.Date()),
        sa.Column('planned_end_date', sa.Date()),
        sa.Column('actual_start_date', sa.Date()),
        sa.Column('actual_end_date', sa.Date()),
        sa.Column('planned_invoice_date', sa.Date()),
        sa.Column('actual_invoice_date', sa.Date()),
        sa.Column('status', sa.String(50), server_default='not_started'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('company_id', sa.Integer()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add stage fields to invoices table
    op.add_column('invoices', sa.Column('project_id', sa.Integer()))
    op.add_column('invoices', sa.Column('stage_id', sa.Integer()))
    op.add_column('invoices', sa.Column('stage_percentage', sa.Float(), server_default='100'))
    op.create_foreign_key('invoices_stage_id_fk', 'invoices', 'project_stages', ['stage_id'], ['id'])
    op.create_foreign_key('invoices_project_id_fk', 'invoices', 'projects', ['project_id'], ['id'])

def downgrade():
    op.drop_constraint('invoices_project_id_fk', 'invoices', type_='foreignkey')
    op.drop_constraint('invoices_stage_id_fk', 'invoices', type_='foreignkey')
    op.drop_column('invoices', 'stage_percentage')
    op.drop_column('invoices', 'stage_id')
    op.drop_column('invoices', 'project_id')
    op.drop_table('project_stages')
