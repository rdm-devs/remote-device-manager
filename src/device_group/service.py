from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.tenant.service import check_tenant_exists
from src.device_group.exceptions import (
    DeviceGroupNameTakenError,
    DeviceGroupNotFoundError,
    InvalidDeviceGroupAttrsError,
)
from . import schemas, models


def check_device_group_exists(db: Session, device_group_id: int):
    db_device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device_group_id)
        .first()
    )
    if not db_device_group:
        raise DeviceGroupNotFoundError()


def check_device_group_name_taken(db: Session, device_group_name: str):
    device_name_taken = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.name == device_group_name)
        .first()
    )
    if device_name_taken:
        raise DeviceGroupNameTakenError()


def create_device_group(db: Session, device_group: schemas.DeviceGroupCreate):
    # sanity check
    check_device_group_name_taken(db, device_group.name)
    if device_group.tenant_id:
        check_tenant_exists(db, device_group.tenant_id)

    db_device = models.DeviceGroup(**device_group.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device_group(db: Session, device_group_id: int):
    db_device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device_group_id)
        .first()
    )
    if db_device_group is None:
        raise DeviceGroupNotFoundError()
    return db_device_group


def get_device_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DeviceGroup).offset(skip).limit(limit).all()


def get_device_group_by_name(db: Session, device_group_name: str):
    device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.name == device_group_name)
        .first()
    )
    if not device_group:
        raise DeviceGroupNotFoundError()
    return device_group


def update_device_group(
    db: Session,
    db_device_group: schemas.DeviceGroup,
    updated_device_group: schemas.DeviceGroupUpdate,
):
    # sanity checks
    get_device_group(db, db_device_group.id)
    check_device_group_name_taken(db, updated_device_group.name)
    if updated_device_group.tenant_id: 
        check_tenant_exists(db, updated_device_group.tenant_id)

    db.query(models.DeviceGroup).filter(
        models.DeviceGroup.id == db_device_group.id
    ).update(values=updated_device_group.model_dump())

    db.commit()
    db.refresh(db_device_group)
    return db_device_group

def delete_device_group(db: Session, db_device_group: schemas.DeviceGroup):
    # sanity check
    check_device_group_exists(db, db_device_group.id)

    db.delete(db_device_group)
    db.commit()
    return db_device_group.id
