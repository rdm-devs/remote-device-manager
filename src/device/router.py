from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from src.auth.dependencies import get_current_active_user
from src.user.schemas import User
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=schemas.Device)
def register_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_device = service.create_device(db=db, device=device)
    return db_device


@router.get("/{device_id}", response_model=schemas.Device)
def read_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_device = service.get_device(db, device_id=device_id)
    return db_device


@router.get("/", response_model=list[schemas.Device])
def read_devices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    return service.get_devices(db, skip=skip, limit=limit)


@router.patch("/{device_id}", response_model=schemas.Device)
def update_device(
    device_id: int,
    device: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_device = read_device(device_id, db)
    updated_device = service.update_device(db, db_device, updated_device=device)

    return updated_device


@router.delete("/{device_id}", response_model=schemas.DeviceDelete)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    db_device = read_device(device_id, db)
    deleted_device_id = service.delete_device(db, db_device)

    return {
        "id": deleted_device_id,
        "msg": f"Device {deleted_device_id} removed succesfully!",
    }
