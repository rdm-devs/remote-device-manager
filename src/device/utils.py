import os
from datetime import datetime, UTC
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from typing import Union, Optional, List
from src.device import models


def get_device_by_serial_number(
    db: Session, serial_number: Optional[str] = None
) -> Union[models.Device | None]:
    stmt = select(models.Device).where(models.Device.serial_number == serial_number)
    return None if serial_number is None else db.scalars(stmt).first()


def get_devices_from_folder(db: Session, folder_id: int):
    return db.scalars(
        select(models.Device).where(folder_models.Folder.id == folder_id)
    ).all()


def get_devices_in_tree(db: Session, folder_ids: List[int]):
    return db.scalars(
        select(models.Device.id).where(models.Device.folder_id.in_(folder_ids))
    ).all()


def reset_devices_folder_id(
    db: Session, folder_ids: List[int], tenant1_root_folder_id: int
) -> None:
    # when deleting a folder every device assigned to it should be assigned to the root folder from tenant1.
    update_stmt = (
        update(models.Device)
        .where(models.Device.folder_id.in_(folder_ids))
        .values(folder_id=tenant1_root_folder_id)
    )
    db.execute(update_stmt)
    db.commit()

# TODO: pending tests. Will probably delete it.
def get_online_status(device: models.Device):
    if not device.folder:
        return False
    if not device.folder.tenant:
        return False
    if not device.heartbeats:
        return False

    tenant_heartbeats_interval = device.folder.tenant.settings.heartbeat_s
    latest_heartbeat_timestamp = device.heartbeats[-1].timestamp
    diff_minutes = (
        datetime.now(UTC) - latest_heartbeat_timestamp.astimezone(UTC)
    ).total_seconds() // 60
    
    return diff_minutes <= tenant_heartbeats_interval * int(
        os.getenv("MAX_TOLERANCE_HEARTBEATS")
    )
