"""adding id column as pk and unique constraint to tenants_and_users

Revision ID: 8a3569fc9d25
Revises: 96524a06cd64
Create Date: 2024-11-06 15:34:30.471389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8a3569fc9d25'
down_revision: Union[str, None] = '96524a06cd64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tenants_and_users', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    op.alter_column('tenants_and_users', 'tenant_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.alter_column('tenants_and_users', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_unique_constraint('uix_tenant_user', 'tenants_and_users', ['tenant_id', 'user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uix_tenant_user', 'tenants_and_users', type_='unique')
    op.alter_column('tenants_and_users', 'user_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.alter_column('tenants_and_users', 'tenant_id',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.drop_column('tenants_and_users', 'id')
    # ### end Alembic commands ###
