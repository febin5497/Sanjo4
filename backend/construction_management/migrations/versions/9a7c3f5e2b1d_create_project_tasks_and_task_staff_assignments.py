"""Create project tasks and task staff assignments tables

Revision ID: 9a7c3f5e2b1d
Revises: 73a2ad3dec7a
Create Date: 2026-03-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a7c3f5e2b1d'
down_revision = '73a2ad3dec7a'
branch_labels = None
depends_on = None


def upgrade():
    # Create project_tasks table
    op.create_table(
        'project_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('task_type', sa.String(50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), server_default='todo', nullable=False),
        sa.Column('progress', sa.Float(), server_default='0', nullable=False),
        sa.Column('order_index', sa.Integer(), server_default='0', nullable=False),
        sa.Column('priority', sa.String(20), server_default='medium', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create task_staff_assignments table
    op.create_table(
        'task_staff_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('staff_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('assigned_on', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('removed_on', sa.DateTime(), nullable=True),
        sa.Column('role_on_task', sa.String(100), nullable=True),
        sa.Column('assigned_by_user_id', sa.Integer(), nullable=True),
        sa.Column('hours_allocated', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['project_tasks.id'], ),
        sa.ForeignKeyConstraint(['staff_id'], ['staff.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indices for better query performance
    op.create_index('ix_project_tasks_project_id', 'project_tasks', ['project_id'])
    op.create_index('ix_project_tasks_status', 'project_tasks', ['status'])
    op.create_index('ix_task_staff_assignments_task_id', 'task_staff_assignments', ['task_id'])
    op.create_index('ix_task_staff_assignments_staff_id', 'task_staff_assignments', ['staff_id'])
    op.create_index('ix_task_staff_assignments_removed_on', 'task_staff_assignments', ['removed_on'])


def downgrade():
    # Drop indices
    op.drop_index('ix_task_staff_assignments_removed_on', 'task_staff_assignments')
    op.drop_index('ix_task_staff_assignments_staff_id', 'task_staff_assignments')
    op.drop_index('ix_task_staff_assignments_task_id', 'task_staff_assignments')
    op.drop_index('ix_project_tasks_status', 'project_tasks')
    op.drop_index('ix_project_tasks_project_id', 'project_tasks')

    # Drop tables
    op.drop_table('task_staff_assignments')
    op.drop_table('project_tasks')
