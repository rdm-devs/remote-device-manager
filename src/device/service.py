from sqlalchemy.orm import Session
from . import schemas, models


def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()


def get_device_by_name(db: Session, device_name: str):
    return db.query(models.Device).filter(models.Device.name == device_name).first()


def create_device(db: Session, device: schemas.DeviceCreate):
    db_device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device.device_group_id)
        .first()
    )
    if db_device_group:
        db_device = models.Device(**device)
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device
    return None


def update_device(
    db: Session, db_device: schemas.Device, updated_device: schemas.DeviceUpdate
):
    updated_db_device = (
        db.query(models.Device)
        .filter(models.Device.id == db_device.id)
        .update(values=updated_device.model_dump())
    )

    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, db_device: schemas.Device):
    db.delete(db_device)
    db.commit()
    return db_device.id
