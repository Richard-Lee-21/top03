"""Create configuration table

Revision ID: 0001
Revises:
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create configurations table
    op.create_table('configurations',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键'),
        sa.Column('key', sa.String(length=100), nullable=False, comment='配置项的唯一键'),
        sa.Column('value', sa.Text(), nullable=False, comment='配置项的值'),
        sa.Column('group', sa.String(length=50), nullable=False, comment='配置组 (api, prompt, ui, cache)'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='最后更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # Create indexes
    op.create_index(op.f('ix_configurations_id'), 'configurations', ['id'], unique=False)
    op.create_index(op.f('ix_configurations_key'), 'configurations', ['key'], unique=False)
    op.create_index(op.f('ix_configurations_group'), 'configurations', ['group'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_configurations_group'), table_name='configurations')
    op.drop_index(op.f('ix_configurations_key'), table_name='configurations')
    op.drop_index(op.f('ix_configurations_id'), table_name='configurations')

    # Drop table
    op.drop_table('configurations')