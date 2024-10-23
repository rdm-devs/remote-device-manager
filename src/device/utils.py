from sqlalchemy import select, update
from sqlalchemy.orm import Session
from typing import Union, Optional
from src.device import models


def get_device_by_serialno(
    db: Session, serialno: Optional[str] = None
) -> Union[models.Device | None]:
    stmt = select(models.Device).where(models.Device.serialno == serialno)
    return None if serialno is None else db.scalars(stmt).first()


def get_devices_from_folder(db: Session, folder_id: int):
    return db.scalars(
        select(models.Device).where(folder_models.Folder.id == folder_id)
    ).all()


def reset_devices_folder_id(db: Session, folder_id: int, tenant1_root_folder_id: int) -> None:
    # when deleting a folder every device assigned to it should be assigned to the root folder from tenant1.
    update_stmt = (
        update(models.Device)
        .where(models.Device.folder_id == folder_id)
        .values(folder_id=tenant1_root_folder_id)
    )
    db.execute(update_stmt)
