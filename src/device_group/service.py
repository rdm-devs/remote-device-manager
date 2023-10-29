from sqlalchemy.orm import Session
from . import schemas, models


def create_device_group(db: Session, device_group: schemas.DeviceGroupCreate):
    db_device = models.DeviceGroup(**device_group)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device_group(db: Session, device_group_id: int):
    return (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device_group_id)
        .first()
    )


def get_device_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DeviceGroup).offset(skip).limit(limit).all()


def get_device_group_by_name(db: Session, device_group_name: str):
    return (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.name == device_group_name)
        .first()
    )


def update_device_group(
    db: Session,
    db_device: schemas.Device,
    updated_device_group: schemas.DeviceGroupUpdate,
):
    db.query(models.DeviceGroup).filter(models.DeviceGroup.id == db_device.id).update(
        values=updated_device_group.model_dump()
    )

    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device_group(db: Session, db_device_group: schemas.DeviceGroup):
    db.delete(db_device_group)
    db.commit()
    return db_device_group.id
