"""Adding heartbeat_logs table

Revision ID: 1d389aa29576
Revises: 83f46b609498
Create Date: 2024-12-11 21:39:20.275053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d389aa29576'
down_revision: Union[str, None] = '83f46b609498'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('heartbeat_logs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=False),
    sa.Column('CPU_load', sa.Integer(), nullable=True),
    sa.Column('MEM_load_mb', sa.Integer(), nullable=True),
    sa.Column('free_space_mb', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['device.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_heartbeat_logs_id'), 'heartbeat_logs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_heartbeat_logs_id'), table_name='heartbeat_logs')
    op.drop_table('heartbeat_logs')
    # ### end Alembic commands ###