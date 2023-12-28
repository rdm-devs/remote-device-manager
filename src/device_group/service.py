from sqlalchemy.orm import Session
from src.tenant.service import check_tenant_exists
from src.device.models import Device
from . import schemas, models, exceptions


def check_device_group_exists(db: Session, device_group_id: int):
    db_device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device_group_id)
        .first()
    )
    if not db_device_group:
        raise exceptions.DeviceGroupNotFoundError()


def check_device_group_name_taken(db: Session, device_group_name: str):
    device_name_taken = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.name == device_group_name)
        .first()
    )
    if device_name_taken:
        raise exceptions.DeviceGroupNameTakenError()


def check_has_no_devices_attached(db: Session, device_group_id: int):
    db_device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device_group_id)
        .first()
    )
    if db_device_group and len(db_device_group.devices) > 0:
        raise exceptions.DeviceGroupHasDevicesAttachedError()


def create_device_group(db: Session, device_group: schemas.DeviceGroupCreate):
    # sanity check
    check_device_group_name_taken(db, device_group.name)
    if device_group.tenant_id:
        check_tenant_exists(db, device_group.tenant_id)

    create_values = device_group.model_dump()

    devices_to_add = []
    if "devices" in create_values:
        devices_to_add = create_values.pop("devices")

    db_device_group = models.DeviceGroup(**create_values)
    db.add(db_device_group)
    db.commit()
    db.refresh(db_device_group)

    if devices_to_add:
        db_device_group = add_devices(db, db_device_group, devices_to_add)
    return db_device_group


def get_device_group(db: Session, device_group_id: int):
    db_device_group = (
        db.query(models.DeviceGroup)
        .filter(models.DeviceGroup.id == device_group_id)
        .first()
    )
    if db_device_group is None:
        raise exceptions.DeviceGroupNotFoundError()
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
        raise exceptions.DeviceGroupNotFoundError()
    return device_group


def update_device_group(
    db: Session,
    device_group_id: int,
    updated_device_group: schemas.DeviceGroupUpdate,
):
    # sanity checks
    db_device_group = get_device_group(db, device_group_id)
    check_device_group_name_taken(db, updated_device_group.name)
    if updated_device_group.tenant_id:
        check_tenant_exists(db, updated_device_group.tenant_id)

    update_values = updated_device_group.model_dump()
    devices_to_add = []
    if "devices" in update_values:
        devices_to_add = update_values.pop("devices")

    db.query(models.DeviceGroup).filter(
        models.DeviceGroup.id == device_group_id
    ).update(values=update_values)
    db.commit()
    db.refresh(db_device_group)

    if devices_to_add:
        db_device_group = add_devices(db, db_device_group, devices_to_add)
    return db_device_group


def add_devices(
    db: Session, db_device_group: models.DeviceGroup, devices: list[Device]
):
    device_ids = [device.id for device in db_device_group.devices]
    for device in devices:
        device = db.query(Device).filter(Device.id == device.id).first()
        if device and device.id not in device_ids:
            db_device = db.query(Device).filter(Device.id == device.id).first()
            db_device_group.devices.append(db_device)

    db.add(db_device_group)
    db.commit()
    db.refresh(db_device_group)

    return db_device_group


def delete_device_group(db: Session, db_device_group: schemas.DeviceGroup):
    # sanity check
    check_device_group_exists(db, db_device_group.id)
    check_has_no_devices_attached(db, db_device_group.id)

    db.delete(db_device_group)
    db.commit()
    return db_device_group.id


def get_devices_from_device_group(db: Session, device_group_id: int):
    check_device_group_exists(db, device_group_id)
    db_device_group = get_device_group(db, device_group_id)
    return db_device_group.devices
