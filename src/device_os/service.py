from sqlalchemy.orm import Session
from . import schemas, models, exceptions


def check_device_os_name_taken(db: Session, os_name: str):
    # TODO: write a test to see how sqlalchemy handles name/version uniqueness. this function may not need to exist.
    device_os_name_taken = (
        db.query(models.DeviceOS).filter(models.DeviceOS.name == os_name).first()
    )
    if device_os_name_taken is not None:
        raise exceptions.DeviceOSNameTakenError()


def get_device_os(db: Session, os_id: int):
    device_os = db.query(models.DeviceOS).filter(models.DeviceOS.id == os_id).first()
    if not device_os:
        raise exceptions.DeviceOSNotFoundError()
    return device_os


def get_all_device_os(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DeviceOS).offset(skip).limit(limit).all()


def get_device_os_by_name(db: Session, os_name: str):
    device_os = db.query(models.DeviceOS).filter(models.DeviceOS.name == os_name).first()
    if not device_os:
        raise exceptions.DeviceOSNotFoundError()
    return device_os


def create_device_os(db: Session, device_os: schemas.DeviceOSCreate):
    # sanity checks
    # check_device_os_name_taken(db, device_os.name)

    db_device_os = models.DeviceOS(**device_os.model_dump())
    db.add(db_device_os)
    db.commit()
    db.refresh(db_device_os)
    return db_device_os


def update_device_os(
    db: Session, db_device_os: schemas.DeviceOS, updated_device_os: schemas.DeviceOSUpdate
):
    # sanity checks
    get_device_os(db, db_device_os.id)
    # check_device_os_name_taken(db, updated_device_os.name)

    db.query(models.DeviceOS).filter(models.DeviceOS.id == db_device_os.id).update(
        values=updated_device_os.model_dump()
    )
    db.commit()
    db.refresh(db_device_os)
    return db_device_os


def delete_device_os(db: Session, db_device_os: schemas.DeviceOS):
    # sanity check
    get_device_os(db, db_device_os.id)

    db.delete(db_device_os)
    db.commit()
    return db_device_os.id
