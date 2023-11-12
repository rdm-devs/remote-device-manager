from sqlalchemy.orm import Session

from src.device.exceptions import DeviceNameTakenError, DeviceNotFoundError
from src.device_group.exceptions import DeviceGroupNotFoundError
from src.device_group.service import check_device_group_exist
from . import schemas, models


def check_device_name_taken(db: Session, device_name: str):
    device_name_taken = (
        db.query(models.Device).filter(models.Device.name == device_name).first()
    )
    if device_name_taken is not None:
        raise DeviceNameTakenError()


def get_device(db: Session, device_id: int):
    device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if not device:
        raise DeviceNotFoundError()
    return device


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()


def get_device_by_name(db: Session, device_name: str):
    device = db.query(models.Device).filter(models.Device.name == device_name).first()
    if not device:
        raise DeviceNotFoundError()
    return device


def create_device(db: Session, device: schemas.DeviceCreate):
    # sanity checks
    check_device_group_exist(db, device.device_group_id)
    check_device_name_taken(db, device.name)

    db_device = models.Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device(
    db: Session, db_device: schemas.Device, updated_device: schemas.DeviceUpdate
):
    # sanity checks
    get_device(db, db_device.id)
    check_device_group_exist(db, updated_device.device_group_id)
    check_device_name_taken(db, updated_device.name)

    db.query(models.Device).filter(models.Device.id == db_device.id).update(
        values=updated_device.model_dump()
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
