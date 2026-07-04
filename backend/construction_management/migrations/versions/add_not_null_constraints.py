"""Add NOT NULL constraints to required fields

Revision ID: add_not_null_001
Revises: add_indexes_001
Create Date: 2026-04-04 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_not_null_001'
down_revision = 'add_indexes_001'
branch_labels = None
depends_on = None


def upgrade():
    """Add NOT NULL constraints to required fields"""

    # First, set defaults for any existing NULL values
    op.execute("""UPDATE staff SET personal_phone = '' WHERE personal_phone IS NULL""")
    op.execute("""UPDATE staff SET salary = 0 WHERE salary IS NULL""")
    op.execute("""UPDATE staff SET pf = 0 WHERE pf IS NULL""")
    op.execute("""UPDATE staff SET esi = 0 WHERE esi IS NULL""")
    op.execute("""UPDATE projects SET company_id = 1 WHERE company_id IS NULL""")

    # Now add NOT NULL constraints via batch_alter_table for SQLite compatibility
    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.alter_column('personal_phone',
                existing_type=sa.String(length=20),
                nullable=False)
        batch_op.alter_column('salary',
                existing_type=sa.Float(),
                nullable=False,
                server_default='0')
        batch_op.alter_column('pf',
                existing_type=sa.Float(),
                nullable=False,
                server_default='0')
        batch_op.alter_column('esi',
                existing_type=sa.Float(),
                nullable=False,
                server_default='0')

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.alter_column('company_id',
                existing_type=sa.Integer(),
                nullable=False)


def downgrade():
    """Remove NOT NULL constraints (allow NULL again)"""

    with op.batch_alter_table('staff', schema=None) as batch_op:
        batch_op.alter_column('personal_phone',
                existing_type=sa.String(length=20),
                nullable=True)
        batch_op.alter_column('salary',
                existing_type=sa.Float(),
                nullable=True)
        batch_op.alter_column('pf',
                existing_type=sa.Float(),
                nullable=True)
        batch_op.alter_column('esi',
                existing_type=sa.Float(),
                nullable=True)

    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.alter_column('company_id',
                existing_type=sa.Integer(),
                nullable=True)
