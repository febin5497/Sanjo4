"""Add soft-delete fields to all models

Revision ID: add_soft_delete_001
Revises: add_not_null_001
Create Date: 2026-04-04

This migration adds is_deleted, deleted_at, and deleted_by fields to all
61 models in the system for audit compliance and data preservation.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_soft_delete_001'
down_revision = 'add_not_null_001'
branch_labels = None
depends_on = None


# List of all tables that need soft-delete fields
TABLES_REQUIRING_SOFT_DELETE = [
    # Staff Management
    'staff',
    'expenses',
    # User & Auth Management
    'user',
    'role',
    'role_permission',
    'user_role',
    # Project Management
    'projects',
    'project_assignments',
    'project_staff_history',
    'project_tasks',
    'task_staff_assignments',
    'project_stages',
    # Material Management
    'materials',
    # Supplier Management
    'suppliers',
    # Finance Management
    'transactions',
    'invoices',
    'budgets',
    'budget_categories',
    'budget_approval_requests',
    'chart_of_accounts',
    'cash_transactions',
    'approval_requests',
    # Vehicle Management
    'vehicles',
    'driver_vehicle_assignment',
    'vehicle_project_assignment',
    'vehicle_project_history',
    'maintenance_logs',
    'maintenance_schedules',
    'fuel_logs',
    # Equipment Management
    'equipment',
    'equipment_maintenance_logs',
    'equipment_usage',
    # Purchase Management
    'purchases',
    'purchase_items',
    'purchase_indents',
    'purchase_indent_items',
    'goods_receipt_notes',
    'grn_items',
    'invoice_reconciliations',
    'vendor_performance',
    # Purchase Returns
    'purchase_returns',
    'purchase_return_items',
    # Sales Management
    'sales',
    'sale_items',
    'sales_returns',
    'sales_return_items',
    # Client Management
    'clients',
    # Company Management
    'companies',
    'company_settings',
    # Attendance
    'attendance',
    'attendance_photos',
    'payroll_cycles',
    'payroll_records',
    # Quote Management
    'quotes',
    'quote_items',
    'quote_templates',
    'template_items',
    # Notifications
    'notifications',
    # Admin
    'activity_log',
    'permission',
    # Error Logging
    'client_error_logs',
    # Planner
    'planner_tasks',
]


def upgrade():
    """Add soft-delete fields to all tables"""
    for table_name in TABLES_REQUIRING_SOFT_DELETE:
        try:
            # Add is_deleted column
            op.add_column(
                table_name,
                sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0')
            )

            # Add deleted_at column
            op.add_column(
                table_name,
                sa.Column('deleted_at', sa.DateTime(), nullable=True)
            )

            # Add deleted_by column (user ID)
            op.add_column(
                table_name,
                sa.Column('deleted_by', sa.Integer(), nullable=True)
            )

            # Create index for soft-delete queries
            try:
                op.create_index(
                    f'idx_{table_name}_is_deleted',
                    table_name,
                    ['is_deleted']
                )
            except Exception:
                pass  # Index might already exist

            print(f"[OK] Added soft-delete fields to {table_name}")
        except Exception as e:
            print(f"[WARN] Could not add soft-delete fields to {table_name}: {str(e)}")
            # Continue with other tables


def downgrade():
    """Remove soft-delete fields from all tables"""
    for table_name in TABLES_REQUIRING_SOFT_DELETE:
        try:
            # Drop index first
            try:
                op.drop_index(f'idx_{table_name}_is_deleted', table_name=table_name)
            except Exception:
                pass

            # Drop columns
            op.drop_column(table_name, 'is_deleted')
            op.drop_column(table_name, 'deleted_at')
            op.drop_column(table_name, 'deleted_by')

            print(f"[OK] Removed soft-delete fields from {table_name}")
        except Exception as e:
            print(f"[WARN] Could not remove soft-delete fields from {table_name}: {str(e)}")
