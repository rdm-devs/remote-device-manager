from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.folder.models import Folder
from src.tenant.models import tenants_and_users_table
from src.device import schemas, models, exceptions
from src.folder.service import check_folder_exist, get_folders
from src.entity.service import create_entity_auto
from src.user.service import get_user


def check_device_name_taken(db: Session, device_name: str, device_id: Optional[int] = None):
    device_name_taken = db.query(models.Device).filter(
        models.Device.name == device_name
    )
    if device_id:
        device_name_taken.filter(models.Device.id != device_id)
    if device_name_taken.first():
        raise exceptions.DeviceNameTaken()


def get_device(db: Session, device_id: int) -> models.Device:
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise exceptions.DeviceNotFound()
    return device


def get_devices_from_tenant(db: Session, tenant_id: int):
    return (
        db.query(models.Device)
        .filter(folder_models.Folder.id == models.Device.folder_id)
        .filter(folder_models.Folder.tenant_id == tenant_id)
    )


def get_devices(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user.is_admin:
        devices = select(models.Device)
    else:
        # folders = get_folders(db, user.id).subquery()
        device_ids = user.get_device_ids()
        devices = select(models.Device).where(
            # models.Device.folder_id.in_(folders)
            models.Device.id.in_(device_ids)
        )
    return devices


def get_device_by_name(db: Session, device_name: str):
    device = db.query(models.Device).filter(models.Device.name == device_name).first()
    if not device:
        raise exceptions.DeviceNotFound()
    return device


def create_device(db: Session, device: schemas.DeviceCreate):
    # sanity checks
    check_folder_exist(db, device.folder_id)
    check_device_name_taken(db, device.name)

    entity = create_entity_auto(db)
    db_device = models.Device(**device.model_dump(), entity_id=entity.id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device(
    db: Session, db_device: schemas.Device, updated_device: schemas.DeviceUpdate
):
    # sanity checks
    get_device(db, db_device.id)
    if updated_device.folder_id:
        check_folder_exist(db, updated_device.folder_id)
    check_device_name_taken(db, updated_device.name, db_device.id)

    #dev = db.query(models.Device).filter(models.Device.id == db_device.id).first()
    db.query(models.Device).filter(models.Device.id == db_device.id).update(
        values=updated_device.model_dump(exclude_unset=True)
    )
    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, db_device: schemas.Device):
    # sanity check
    get_device(db, db_device.id)

    db.delete(db_device)
    db.commit()
    return db_device.id
