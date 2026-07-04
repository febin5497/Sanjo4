"""Add database indexes for performance optimization

Revision ID: add_indexes_001
Revises: phase_6_9_complete
Create Date: 2026-04-04 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_indexes_001'
down_revision = 'phase_6_9_complete'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for frequently queried columns"""

    # Staff indexes
    op.create_index('idx_staff_company', 'staff', ['company_id'])
    op.create_index('idx_staff_phone', 'staff', ['personal_phone'])
    op.create_index('idx_staff_email', 'staff', ['personal_email'])
    op.create_index('idx_staff_status', 'staff', ['status'])

    # User indexes
    op.create_index('idx_user_company', 'user', ['company_id'])
    op.create_index('idx_user_email', 'user', ['email'])
    op.create_index('idx_user_username', 'user', ['username'])
    op.create_index('idx_user_is_active', 'user', ['is_active'])

    # Project indexes
    op.create_index('idx_project_company', 'projects', ['company_id'])
    op.create_index('idx_project_client', 'projects', ['client_id'])
    op.create_index('idx_project_status', 'projects', ['status'])
    op.create_index('idx_project_user', 'projects', ['user_id'])

    # Material indexes
    op.create_index('idx_material_project', 'materials', ['project_id'])
    op.create_index('idx_material_name', 'materials', ['name'])

    # Supplier indexes
    op.create_index('idx_supplier_name', 'suppliers', ['name'])
    op.create_index('idx_supplier_is_active', 'suppliers', ['is_active'])
    op.create_index('idx_supplier_gstin', 'suppliers', ['gstin'])


def downgrade():
    """Remove all created indexes"""

    # Drop indexes (in reverse order)
    op.drop_index('idx_supplier_gstin', 'suppliers')
    op.drop_index('idx_supplier_is_active', 'suppliers')
    op.drop_index('idx_supplier_name', 'suppliers')

    op.drop_index('idx_material_name', 'materials')
    op.drop_index('idx_material_project', 'materials')

    op.drop_index('idx_project_user', 'projects')
    op.drop_index('idx_project_status', 'projects')
    op.drop_index('idx_project_client', 'projects')
    op.drop_index('idx_project_company', 'projects')

    op.drop_index('idx_user_is_active', 'user')
    op.drop_index('idx_user_username', 'user')
    op.drop_index('idx_user_email', 'user')
    op.drop_index('idx_user_company', 'user')

    op.drop_index('idx_staff_status', 'staff')
    op.drop_index('idx_staff_email', 'staff')
    op.drop_index('idx_staff_phone', 'staff')
    op.drop_index('idx_staff_company', 'staff')
