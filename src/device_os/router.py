from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/devices/os", tags=["devices"])


@router.post("/", response_model=schemas.DeviceOS, summary="Create Device OS")
def create_device_os(device_os: schemas.DeviceOSCreate, db: Session = Depends(get_db)):
    db_device_os = service.create_device_os(db=db, device_os=device_os)
    return db_device_os


@router.get(
    "/{os_id}", response_model=schemas.DeviceOS, summary="Read Device OS"
)
def read_device_os(os_id: int, db: Session = Depends(get_db)):
    db_device_os = service.get_device_os(db, os_id=os_id)
    return db_device_os


@router.get("/", response_model=list[schemas.DeviceOS], summary="Read All Device OS")
def read_all_device_os(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_all_device_os(db, skip=skip, limit=limit)


@router.patch("/{os_id}", response_model=schemas.DeviceOS, summary="Update Device OS")
def update_device_os(
    os_id: int, device_os: schemas.DeviceOSUpdate, db: Session = Depends(get_db)
):
    db_device_os = read_device_os(os_id, db)
    updated_device_os = service.update_device_os(db, db_device_os, updated_device_os=device_os)

    return updated_device_os


@router.delete(
    "/{os_id}", response_model=schemas.DeviceOSDelete, summary="Delete Device OS"
)
def delete_device_os(os_id: int, db: Session = Depends(get_db)):
    db_device_os = read_device_os(os_id, db)
    deleted_os_id = service.delete_device_os(db, db_device_os)

    return {
        "id": deleted_os_id,
        "msg": f"Device OS {deleted_os_id} removed succesfully!",
    }
