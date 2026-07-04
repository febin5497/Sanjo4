"""Add finance modules: approvals, budgets, procurement

Revision ID: finance_001
Revises:
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa

revision = 'finance_001'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None

def upgrade():
    # ApprovalRequest table
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('approval_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_levels', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_approver_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('required_approvers', sa.Text()),
        sa.Column('approval_notes', sa.Text()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('submitted_at', sa.DateTime()),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('rejected_at', sa.DateTime()),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('rejected_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id')),
        sa.PrimaryKeyConstraint('id')
    )

    # Add approval fields to Invoice
    op.add_column('invoices', sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')))
    op.add_column('invoices', sa.Column('approval_notes', sa.Text()))
    op.add_column('invoices', sa.Column('rejection_reason', sa.Text()))
    op.add_column('invoices', sa.Column('approved_at', sa.DateTime()))

    # Add approval fields to transactions
    op.add_column('transactions', sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')))
    op.add_column('transactions', sa.Column('approval_notes', sa.Text()))
    op.add_column('transactions', sa.Column('rejection_reason', sa.Text()))
    op.add_column('transactions', sa.Column('approved_at', sa.DateTime()))

    # Add approval fields to cash_transactions
    op.add_column('cash_transactions', sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')))
    op.add_column('cash_transactions', sa.Column('approval_notes', sa.Text()))
    op.add_column('cash_transactions', sa.Column('rejection_reason', sa.Text()))
    op.add_column('cash_transactions', sa.Column('approved_at', sa.DateTime()))

    # Budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('total_budget', sa.Float(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('description', sa.Text()),
        sa.Column('notes', sa.Text()),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Budget Categories table
    op.create_table(
        'budget_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('budget_id', sa.Integer(), sa.ForeignKey('budgets.id'), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('allocated_amount', sa.Float(), nullable=False),
        sa.Column('used_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('warning_threshold', sa.Float(), nullable=False, server_default='80'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Budget Approval Requests table
    op.create_table(
        'budget_approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('budget_id', sa.Integer(), sa.ForeignKey('budgets.id'), nullable=False),
        sa.Column('request_type', sa.String(20), nullable=False),
        sa.Column('proposed_changes', sa.Text()),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('approval_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_levels', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_approver_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('approval_notes', sa.Text()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('requested_by_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Purchase Indents table
    op.create_table(
        'purchase_indents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('indent_number', sa.String(50), nullable=False, unique=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id')),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id')),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('justification', sa.Text()),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('indent_date', sa.Date(), nullable=False),
        sa.Column('required_by_date', sa.Date(), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('rejection_reason', sa.Text()),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Purchase Indent Items table
    op.create_table(
        'purchase_indent_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('indent_id', sa.Integer(), sa.ForeignKey('purchase_indents.id'), nullable=False),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('materials.id')),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50), server_default='qty'),
        sa.Column('estimated_rate', sa.Float()),
        sa.Column('estimated_cost', sa.Float()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # GRN table
    op.create_table(
        'goods_receipt_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grn_number', sa.String(50), nullable=False, unique=True),
        sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchases.id'), nullable=False),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id')),
        sa.Column('receipt_date', sa.Date(), nullable=False),
        sa.Column('vehicle_number', sa.String(50)),
        sa.Column('driver_name', sa.String(255)),
        sa.Column('supplier_reference', sa.String(100)),
        sa.Column('quality_check_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('quality_check_notes', sa.Text()),
        sa.Column('quality_checked_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('quality_check_date', sa.DateTime()),
        sa.Column('status', sa.String(20), nullable=False, server_default='received'),
        sa.Column('accepted_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('accepted_at', sa.DateTime()),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # GRN Items table
    op.create_table(
        'grn_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grn_id', sa.Integer(), sa.ForeignKey('goods_receipt_notes.id'), nullable=False),
        sa.Column('po_item_id', sa.Integer()),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('quantity_ordered', sa.Float(), nullable=False),
        sa.Column('quantity_received', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(50)),
        sa.Column('quality_remarks', sa.Text()),
        sa.Column('is_damaged', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('damaged_quantity', sa.Float(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Invoice Reconciliation table
    op.create_table(
        'invoice_reconciliations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grn_id', sa.Integer(), sa.ForeignKey('goods_receipt_notes.id'), nullable=False),
        sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('discrepancy_type', sa.String(50)),
        sa.Column('quantity_variance', sa.Float(), server_default='0'),
        sa.Column('amount_variance', sa.Float(), server_default='0'),
        sa.Column('notes', sa.Text()),
        sa.Column('resolution', sa.Text()),
        sa.Column('resolved_by_id', sa.Integer(), sa.ForeignKey('user.id')),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('invoice_reconciliations')
    op.drop_table('grn_items')
    op.drop_table('goods_receipt_notes')
    op.drop_table('purchase_indent_items')
    op.drop_table('purchase_indents')
    op.drop_table('budget_approval_requests')
    op.drop_table('budget_categories')
    op.drop_table('budgets')

    op.drop_column('cash_transactions', 'approved_at')
    op.drop_column('cash_transactions', 'rejection_reason')
    op.drop_column('cash_transactions', 'approval_notes')
    op.drop_column('cash_transactions', 'approved_by_id')

    op.drop_column('transactions', 'approved_at')
    op.drop_column('transactions', 'rejection_reason')
    op.drop_column('transactions', 'approval_notes')
    op.drop_column('transactions', 'approved_by_id')

    op.drop_column('invoices', 'approved_at')
    op.drop_column('invoices', 'rejection_reason')
    op.drop_column('invoices', 'approval_notes')
    op.drop_column('invoices', 'approved_by_id')

    op.drop_table('approval_requests')
