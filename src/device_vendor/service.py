from sqlalchemy.orm import Session
from . import schemas, models, exceptions


def check_device_vendor_brand_name_taken(db: Session, device_vendor_brand_name: str):
    device_vendor_brand_name_taken = (
        db.query(models.DeviceVendor).filter(models.DeviceVendor.name == device_vendor_name).first()
    )
    if device_vendor_brand_name_taken is not None:
        raise exceptions.DeviceVendorNameTakenError()


def get_device_vendor(db: Session, vendor_id: int):
    device_vendor = (
        db.query(models.DeviceVendor).filter(models.DeviceVendor.id == vendor_id).first()
    )
    if not device_vendor:
        raise exceptions.DeviceVendorNotFoundError()
    return device_vendor


def get_device_vendors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DeviceVendor).offset(skip).limit(limit).all()


def get_device_vendor_by_brand_name(db: Session, brand_name: str):
    device_vendor = (
        db.query(models.DeviceVendor).filter(models.DeviceVendor.brand == brand_name).first()
    )
    if not device_vendor:
        raise exceptions.DeviceVendorNotFoundError()
    return device_vendor


def create_device_vendor(db: Session, device_vendor: schemas.DeviceVendorCreate):
    # sanity checks
    # check_device_vendor_brand_name_taken(db, device_vendor.name)

    db_device_vendor = models.DeviceVendor(**device_vendor.model_dump())
    db.add(db_device_vendor)
    db.commit()
    db.refresh(db_device_vendor)
    return db_device_vendor


def update_device_vendor(
    db: Session,
    db_device_vendor: schemas.DeviceVendor,
    updated_device_vendor: schemas.DeviceVendorUpdate,
):
    # sanity checks
    get_device_vendor(db, db_device_vendor.id)
    # check_device_vendor_brand_name_taken(db, updated_device_vendor.name)

    db.query(models.DeviceVendor).filter(models.DeviceVendor.id == db_device_vendor.id).update(
        values=updated_device_vendor.model_dump()
    )
    db.commit()
    db.refresh(db_device_vendor)
    return db_device_vendor


def delete_device_vendor(db: Session, db_device_vendor: schemas.DeviceVendor):
    # sanity check
    get_device_vendor(db, db_device_vendor.id)

    db.delete(db_device_vendor)
    db.commit()
    return db_device_vendor.id
