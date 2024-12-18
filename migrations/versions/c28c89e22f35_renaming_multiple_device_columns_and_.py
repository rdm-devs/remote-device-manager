"""renaming multiple device columns and adding time_zone column

Revision ID: c28c89e22f35
Revises: e318d3496d84
Create Date: 2024-12-18 17:00:41.491997

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "c28c89e22f35"
down_revision: Union[str, None] = "e318d3496d84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_device_os_name", table_name="device")
    op.drop_index("serialno", table_name="device")

    op.add_column(
       "device", sa.Column("time_zone", sa.String(length=1000), nullable=True)
    )

    op.alter_column(
        "device",
        column_name="os_name",
        new_column_name="SO_name",
        existing_type=sa.String(255),
        type_=sa.String(255),
    )
    op.alter_column(
        "device",
        column_name="os_version",
        new_column_name="SO_version",
        existing_type=sa.String(255),
        type_=sa.String(255),
    )
    op.alter_column(
        "device",
        column_name="ip_address",
        new_column_name="local_ips",
        existing_type=sa.String(length=15),
        type_=sa.String(length=512),
    )
    op.alter_column(
        "device",
        column_name="mac_address",
        new_column_name="MAC_addresses",
        existing_type=sa.String(length=17),
        type_=sa.String(length=512),
    )
    op.alter_column(
        "device",
        column_name="serialno",
        new_column_name="serial_number",
        existing_type=sa.String(length=255),
        type_=sa.String(length=255),
    )

    op.create_index(op.f("ix_device_SO_name"), "device", ["SO_name"], unique=False)
    op.create_unique_constraint(None, "device", ["serial_number"])


def downgrade() -> None:
    op.drop_column("device", "time_zone")
    op.drop_index("serial_number", table_name="device")
    op.drop_index(op.f("ix_device_SO_name"), table_name="device")

    op.alter_column(
        "device",
        column_name="SO_name",
        new_column_name="os_name",
        existing_type=sa.String(255),
        type_=sa.String(255),
    )
    op.alter_column(
        "device",
        column_name="SO_version",
        new_column_name="os_version",
        existing_type=sa.String(255),
        type_=sa.String(255),
    )
    op.alter_column(
        "device",
        column_name="local_ips",
        new_column_name="ip_address",
        existing_type=sa.String(length=512),
        type_=sa.String(length=15),
    )
    op.alter_column(
        "device",
        column_name="MAC_addresses",
        new_column_name="mac_address",
        existing_type=sa.String(length=512),
        type_=sa.String(length=17),
    )
    op.alter_column(
        "device",
        column_name="serial_number",
        new_column_name="serialno",
        existing_type=sa.String(length=255),
        type_=sa.String(length=255),
    )

    op.create_index("ix_device_os_name", "device", ["os_name"], unique=False)
    op.create_unique_constraint(None, "device", ["serialno"])
