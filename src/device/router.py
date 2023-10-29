from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter()


@router.post("/devices/", response_model=schemas.Device)
def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    db_device = service.get_device_by_name(db, device_name=device.name)
    if db_device:
        raise HTTPException(status_code=400, detail="Device name already registered")
    db_device = service.create_device(db=db, device=device)
    if not db_device:
        raise HTTPException(
            status_code=400, detail=f"Device group {device.device_group_id} not found"
        )
    return db_device


@router.get("/devices/{device_id}", response_model=schemas.Device)
def read_device(device_id: int, db: Session = Depends(get_db)):
    db_device = service.get_device(db, device_id=device_id)
    if db_device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return db_device


@router.get("/devices/", response_model=list[schemas.Device])
def read_devices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_devices(db, skip=skip, limit=limit)


@router.patch("/devices/{device_id}", response_model=schemas.Device)
def update_device(
    device_id: int, device: schemas.DeviceUpdate, db: Session = Depends(get_db)
):
    db_device = read_device(device_id, db)
    updated_device = service.update_device(db, db_device, updated_device=device)
    if not updated_device:
        raise HTTPException(status_code=400, detail="Device could not be updated. Invalid Device group id")
    return updated_device


@router.delete("/devices/{device_id}", response_model=schemas.DeviceDelete)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    db_device = read_device(device_id, db)
    deleted_device_id = service.delete_device(db, db_device)
    if not deleted_device_id:
        raise HTTPException(status_code=400, detail="Device could not be deleted")
    return {
        "id": deleted_device_id,
        "msg": f"Device {deleted_device_id} removed succesfully!",
    }
