from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/devices/vendors", tags=["devices"])


@router.post("/", response_model=schemas.DeviceVendor)
def create_device_vendor(device_vendor: schemas.DeviceVendorCreate, db: Session = Depends(get_db)):
    db_device_vendor = service.create_device_vendor(db=db, device_vendor=device_vendor)
    return db_device_vendor


@router.get("/{vendor_id}", response_model=schemas.DeviceVendor)
def read_device_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db_device_vendor = service.get_device_vendor(db, vendor_id=vendor_id)
    return db_device_vendor


@router.get("/", response_model=list[schemas.DeviceVendor])
def read_device_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_device_vendors(db, skip=skip, limit=limit)


@router.patch("/{vendor_id}", response_model=schemas.DeviceVendor)
def update_device_vendor(
    vendor_id: int, device_vendor: schemas.DeviceVendorUpdate, db: Session = Depends(get_db)
):
    db_device_vendor = read_device_vendor(vendor_id, db)
    updated_device_vendor = service.update_device_vendor(
        db, db_device_vendor, updated_device_vendor=device_vendor
    )

    return updated_device_vendor


@router.delete("/{vendor_id}", response_model=schemas.DeviceVendorDelete)
def delete_device_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db_device_vendor = read_device_vendor(vendor_id, db)
    deleted_vendor_id = service.delete_device_vendor(db, db_device_vendor)

    return {
        "id": deleted_vendor_id,
        "msg": f"Device Vendor {deleted_vendor_id} removed succesfully!",
    }
