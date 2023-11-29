from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas
from ..device.schemas import Device

router = APIRouter()


@router.post("/device_groups/", response_model=schemas.DeviceGroup)
def create_device_group(
    device_group: schemas.DeviceGroupCreate, db: Session = Depends(get_db)
):
    db_device_group = service.create_device_group(db, device_group)
    return db_device_group


@router.get("/device_groups/{device_group_id}", response_model=schemas.DeviceGroup)
def read_device_group(device_group_id: int, db: Session = Depends(get_db)):
    db_device_group = service.get_device_group(db, device_group_id)
    return db_device_group


@router.get("/device_groups/", response_model=list[schemas.DeviceGroup])
def read_device_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_device_groups(db, skip=skip, limit=limit)


@router.patch("/device_groups/{device_group_id}", response_model=schemas.DeviceGroup)
def update_device_group(
    device_group_id: int,
    device_group: schemas.DeviceGroupUpdate,
    db: Session = Depends(get_db),
):
    updated_device = service.update_device_group(
        db, device_group_id, updated_device_group=device_group
    )
    return updated_device


@router.delete(
    "/device_groups/{device_group_id}", response_model=schemas.DeviceGroupDelete
)
def delete_device_group(device_group_id: int, db: Session = Depends(get_db)):
    db_device_group_group = read_device_group(device_group_id, db)
    deleted_device_group_id = service.delete_device_group(db, db_device_group_group)
    return {
        "id": deleted_device_group_id,
        "msg": f"Device group {deleted_device_group_id} removed succesfully!",
    }


@router.get("/device_groups/{device_group_id}/devices", response_model=list[Device])
def get_devices_from_device_group(
    device_group_id: int,
    db: Session = Depends(get_db),
):
    db_devices = service.get_devices_from_device_group(db, device_group_id)
    return db_devices
